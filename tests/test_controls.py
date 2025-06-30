"""Tests controls."""

import pytest

import sandman_main.controls as controls
import sandman_main.gpio as gpio
import tests.test_timer as test_timer


def test_control_initialization() -> None:
    """Test control initialization."""
    timer = test_timer.TestTimer()
    gpio_manager = gpio.GPIOManager(is_live_mode=False)
    gpio_manager.initialize()

    # A control should start off idle.
    control = controls.Control("test_initialization", timer, gpio_manager)
    assert control.get_state() == controls.ControlState.IDLE

    notifications = []

    # We cannot use the control before it is initialized.
    with pytest.raises(ValueError):
        control.set_desired_state(controls.ControlState.IDLE)

    with pytest.raises(ValueError):
        control.process(notifications)

    # Controls start out uninitialized.
    assert control.uninitialize() == False

    # Initialization will fail if either line is negative or if the lines are
    # the same.
    assert (
        control.initialize(
            up_gpio_line=-1,
            down_gpio_line=2,
            moving_duration_ms=10,
            cool_down_duration_ms=5,
        )
        == False
    )
    assert (
        control.initialize(
            up_gpio_line=1,
            down_gpio_line=-5,
            moving_duration_ms=10,
            cool_down_duration_ms=5,
        )
        == False
    )
    assert (
        control.initialize(
            up_gpio_line=1,
            down_gpio_line=1,
            moving_duration_ms=10,
            cool_down_duration_ms=5,
        )
        == False
    )
    # The moving duration must be greater than zero and cool down must not be
    # negative.
    assert (
        control.initialize(
            up_gpio_line=1,
            down_gpio_line=2,
            moving_duration_ms=0,
            cool_down_duration_ms=5,
        )
        == False
    )
    assert (
        control.initialize(
            up_gpio_line=1,
            down_gpio_line=2,
            moving_duration_ms=10,
            cool_down_duration_ms=-1,
        )
        == False
    )

    # This one should finally succeeded.
    assert (
        control.initialize(
            up_gpio_line=1,
            down_gpio_line=2,
            moving_duration_ms=10,
            cool_down_duration_ms=5,
        )
        == True
    )
    # But we can't initialize again.
    assert (
        control.initialize(
            up_gpio_line=1,
            down_gpio_line=2,
            moving_duration_ms=10,
            cool_down_duration_ms=5,
        )
        == False
    )

    # It should remain idle without change.
    control.process(notifications)
    assert control.get_state() == controls.ControlState.IDLE

    timer.set_current_time_ms(1000)
    control.process(notifications)
    assert control.get_state() == controls.ControlState.IDLE

    assert control.uninitialize() == True
    assert control.uninitialize() == False

    gpio_manager.uninitialize()


def _test_control_moving_flow(
    control_name: str,
    desired_state: controls.ControlState,
    moving_duration_ms: int,
    cool_down_duration_ms: int,
) -> None:
    """Test control moving state flow."""
    timer = test_timer.TestTimer()
    gpio_manager = gpio.GPIOManager(is_live_mode=False)
    gpio_manager.initialize()

    control = controls.Control(
        control_name,
        timer,
        gpio_manager,
    )
    assert control.get_state() == controls.ControlState.IDLE

    assert (
        control.initialize(
            up_gpio_line=1,
            down_gpio_line=2,
            moving_duration_ms=moving_duration_ms,
            cool_down_duration_ms=cool_down_duration_ms,
        )
        == True
    )

    notifications = []

    # There should be no state change after setting the desired state without
    # processing.
    control.set_desired_state(desired_state)
    assert control.get_state() == controls.ControlState.IDLE

    # Immediately after processing the state should change.
    control.process(notifications)
    assert control.get_state() == desired_state

    # We should remain in this state indefinitely without time changing.
    for _iteration in range(50):
        control.process(notifications)
        assert control.get_state() == desired_state

    # We should remain in this state until just before the moving duration is
    # over.
    for time_ms in range(moving_duration_ms):
        timer.set_current_time_ms(time_ms)
        control.process(notifications)
        assert control.get_state() == desired_state

    # After time is up, we should transition to cool down.
    timer.set_current_time_ms(moving_duration_ms)
    control.process(notifications)
    assert control.get_state() == controls.ControlState.COOL_DOWN

    # We should remain in this state until just before the cooldown duration
    # is over.
    for time_ms in range(cool_down_duration_ms):
        timer.set_current_time_ms(moving_duration_ms + time_ms)
        control.process(notifications)
        assert control.get_state() == controls.ControlState.COOL_DOWN

    # After time is up, we should transition to idle.
    timer.set_current_time_ms(moving_duration_ms + cool_down_duration_ms)
    control.process(notifications)
    assert control.get_state() == controls.ControlState.IDLE

    assert control.uninitialize() == True
    gpio_manager.uninitialize()


def test_control_moving_up() -> None:
    """Test control moving up state flow."""
    moving_duration_ms = 10
    cool_down_duration_ms = 4
    _test_control_moving_flow(
        "test_moving_up",
        controls.ControlState.MOVE_UP,
        moving_duration_ms,
        cool_down_duration_ms,
    )


def test_control_moving_down() -> None:
    """Test control moving down state flow."""
    moving_duration_ms = 10
    cool_down_duration_ms = 4
    _test_control_moving_flow(
        "test_moving_down",
        controls.ControlState.MOVE_DOWN,
        moving_duration_ms,
        cool_down_duration_ms,
    )


def test_control_moving_switch() -> None:
    """Test that we can alternate between moving directions."""
    gpio_manager = gpio.GPIOManager(is_live_mode=False)
    gpio_manager.initialize()

    control = controls.Control(
        "test_moving_switch",
        test_timer.TestTimer(),
        gpio_manager,
    )
    control.initialize(
        up_gpio_line=1,
        down_gpio_line=2,
        moving_duration_ms=10,
        cool_down_duration_ms=5,
    )

    notifications = []

    # We should be able to immediately transition between direction without
    # changing time, but processing steps are required.
    control.set_desired_state(controls.ControlState.MOVE_UP)
    control.process(notifications)
    assert control.get_state() == controls.ControlState.MOVE_UP

    control.set_desired_state(controls.ControlState.MOVE_DOWN)
    assert control.get_state() == controls.ControlState.MOVE_UP
    control.process(notifications)
    assert control.get_state() == controls.ControlState.MOVE_DOWN

    control.set_desired_state(controls.ControlState.MOVE_UP)
    assert control.get_state() == controls.ControlState.MOVE_DOWN
    control.process(notifications)
    assert control.get_state() == controls.ControlState.MOVE_UP

    assert control.uninitialize() == True
    gpio_manager.uninitialize()


def test_control_moving_switch_time() -> None:
    """Test that switching moving direction resets the duration."""
    timer = test_timer.TestTimer()
    gpio_manager = gpio.GPIOManager(is_live_mode=False)
    gpio_manager.initialize()

    moving_duration_ms = 10
    control = controls.Control(
        "test_moving_switch_time",
        timer,
        gpio_manager,
    )
    control.initialize(
        up_gpio_line=1,
        down_gpio_line=2,
        moving_duration_ms=moving_duration_ms,
        cool_down_duration_ms=5,
    )

    notifications = []

    control.set_desired_state(controls.ControlState.MOVE_DOWN)
    control.process(notifications)
    assert control.get_state() == controls.ControlState.MOVE_DOWN

    time_before_switch_ms = 4
    timer.set_current_time_ms(time_before_switch_ms)
    control.set_desired_state(controls.ControlState.MOVE_UP)
    control.process(notifications)
    assert control.get_state() == controls.ControlState.MOVE_UP

    # The duration after switch should be the full moving duration.
    for time_ms in range(moving_duration_ms):
        timer.set_current_time_ms(time_before_switch_ms + time_ms)
        control.process(notifications)
        assert control.get_state() == controls.ControlState.MOVE_UP

    timer.set_current_time_ms(time_before_switch_ms + moving_duration_ms)
    control.process(notifications)
    assert control.get_state() == controls.ControlState.COOL_DOWN

    assert control.uninitialize() == True
    gpio_manager.uninitialize()


def test_control_moving_stop() -> None:
    """Test that we can stop moving."""
    gpio_manager = gpio.GPIOManager(is_live_mode=False)
    gpio_manager.initialize()

    control = controls.Control(
        "test_moving_stop",
        test_timer.TestTimer(),
        gpio_manager,
    )
    control.initialize(
        up_gpio_line=1,
        down_gpio_line=2,
        moving_duration_ms=10,
        cool_down_duration_ms=5,
    )

    notifications = []

    # We should be able to immediately stop moving without changing time, but
    # processing steps are required.
    control.set_desired_state(controls.ControlState.MOVE_UP)
    control.process(notifications)
    assert control.get_state() == controls.ControlState.MOVE_UP

    control.set_desired_state(controls.ControlState.IDLE)
    assert control.get_state() == controls.ControlState.MOVE_UP
    control.process(notifications)
    assert control.get_state() == controls.ControlState.COOL_DOWN

    assert control.uninitialize() == True

    control = controls.Control(
        "test_moving_stop",
        test_timer.TestTimer(),
        gpio_manager,
    )
    control.initialize(
        up_gpio_line=1,
        down_gpio_line=2,
        moving_duration_ms=10,
        cool_down_duration_ms=5,
    )

    control.set_desired_state(controls.ControlState.MOVE_DOWN)
    control.process(notifications)
    assert control.get_state() == controls.ControlState.MOVE_DOWN

    control.set_desired_state(controls.ControlState.IDLE)
    assert control.get_state() == controls.ControlState.MOVE_DOWN
    control.process(notifications)
    assert control.get_state() == controls.ControlState.COOL_DOWN

    assert control.uninitialize() == True
    gpio_manager.uninitialize()


def test_control_cool_down() -> None:
    """Test the cool down state."""
    timer = test_timer.TestTimer()
    gpio_manager = gpio.GPIOManager(is_live_mode=False)
    gpio_manager.initialize()

    moving_duration_ms = 4
    cool_down_duration_ms = 10
    control = controls.Control(
        "test_cool_down",
        timer,
        gpio_manager,
    )
    control.initialize(
        up_gpio_line=1,
        down_gpio_line=2,
        moving_duration_ms=moving_duration_ms,
        cool_down_duration_ms=cool_down_duration_ms,
    )
    assert control.get_state() == controls.ControlState.IDLE

    notifications = []

    # First we need to get into the cool down state.
    control.set_desired_state(controls.ControlState.MOVE_DOWN)
    control.process(notifications)
    assert control.get_state() == controls.ControlState.MOVE_DOWN
    timer.set_current_time_ms(moving_duration_ms)
    control.process(notifications)
    assert control.get_state() == controls.ControlState.COOL_DOWN

    # We cannot change the state during the cool down.
    for time_ms in range(cool_down_duration_ms):
        timer.set_current_time_ms(moving_duration_ms + time_ms)

        control.set_desired_state(controls.ControlState.IDLE)
        control.process(notifications)
        assert control.get_state() == controls.ControlState.COOL_DOWN

        control.set_desired_state(controls.ControlState.MOVE_UP)
        control.process(notifications)
        assert control.get_state() == controls.ControlState.COOL_DOWN

        control.set_desired_state(controls.ControlState.MOVE_DOWN)
        control.process(notifications)
        assert control.get_state() == controls.ControlState.COOL_DOWN

    # After the cool down is over, we should go idle and stay there.
    timer.set_current_time_ms(moving_duration_ms + cool_down_duration_ms)
    control.process(notifications)
    assert control.get_state() == controls.ControlState.IDLE
    control.process(notifications)
    assert control.get_state() == controls.ControlState.IDLE

    assert control.uninitialize() == True
    gpio_manager.uninitialize()


def test_control_no_desired_cool_down() -> None:
    """Test that we cannot set cool down as a desired state."""
    gpio_manager = gpio.GPIOManager(is_live_mode=False)
    gpio_manager.initialize()

    control = controls.Control(
        "test_desired_cool_down",
        test_timer.TestTimer(),
        gpio_manager,
    )
    control.initialize(
        up_gpio_line=1,
        down_gpio_line=2,
        moving_duration_ms=10,
        cool_down_duration_ms=5,
    )

    notifications = []

    assert control.get_state() == controls.ControlState.IDLE
    control.set_desired_state(controls.ControlState.COOL_DOWN)
    control.process(notifications)
    assert control.get_state() == controls.ControlState.IDLE

    control.set_desired_state(controls.ControlState.MOVE_DOWN)
    control.process(notifications)
    assert control.get_state() == controls.ControlState.MOVE_DOWN
    control.set_desired_state(controls.ControlState.COOL_DOWN)
    control.process(notifications)
    assert control.get_state() == controls.ControlState.MOVE_DOWN

    control.set_desired_state(controls.ControlState.MOVE_UP)
    control.process(notifications)
    assert control.get_state() == controls.ControlState.MOVE_UP
    control.set_desired_state(controls.ControlState.COOL_DOWN)
    control.process(notifications)
    assert control.get_state() == controls.ControlState.MOVE_UP

    assert control.uninitialize() == True
    gpio_manager.uninitialize()
