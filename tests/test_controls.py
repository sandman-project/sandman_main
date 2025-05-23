"""Tests controls."""

import sandman_main.controls as controls
import tests.test_timer as test_timer


def test_control_initialization() -> None:
    """Test control initialization."""
    timer = test_timer.TestTimer()

    # A control should start off idle.
    control = controls.Control(
        "test_initialization",
        timer,
        moving_duration_ms=10,
        cool_down_duration_ms=5,
    )
    assert control.get_state() == controls.ControlState.IDLE

    # It should remain idle without change.
    control.process()
    assert control.get_state() == controls.ControlState.IDLE

    timer.set_current_time_ms(1000)
    control.process()
    assert control.get_state() == controls.ControlState.IDLE


def _test_control_moving_flow(
    control_name: str,
    desired_state: controls.ControlState,
    moving_duration_ms: int,
    cool_down_duration_ms: int,
) -> None:
    """Test control moving state flow."""
    timer = test_timer.TestTimer()

    control = controls.Control(
        control_name, timer, moving_duration_ms, cool_down_duration_ms
    )
    assert control.get_state() == controls.ControlState.IDLE

    # There should be no state change after setting the desired state without
    # processing.
    control.set_desired_state(desired_state)
    assert control.get_state() == controls.ControlState.IDLE

    # Immediately after processing the state should change.
    control.process()
    assert control.get_state() == desired_state

    # We should remain in this state indefinitely without time changing.
    for _iteration in range(50):
        control.process()
        assert control.get_state() == desired_state

    # We should remain in this state until just before the moving duration is
    # over.
    for time_ms in range(moving_duration_ms):
        timer.set_current_time_ms(time_ms)
        control.process()
        assert control.get_state() == desired_state

    # After time is up, we should transition to cool down.
    timer.set_current_time_ms(moving_duration_ms)
    control.process()
    assert control.get_state() == controls.ControlState.COOL_DOWN

    # We should remain in this state until just before the cooldown duration
    # is over.
    for time_ms in range(cool_down_duration_ms):
        timer.set_current_time_ms(moving_duration_ms + time_ms)
        control.process()
        assert control.get_state() == controls.ControlState.COOL_DOWN

    # After time is up, we should transition to idle.
    timer.set_current_time_ms(moving_duration_ms + cool_down_duration_ms)
    control.process()
    assert control.get_state() == controls.ControlState.IDLE


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
    control = controls.Control(
        "test_moving_switch",
        test_timer.TestTimer(),
        moving_duration_ms=10,
        cool_down_duration_ms=5,
    )

    # We should be able to immediately transition between direction without
    # changing time, but processing steps are required.
    control.set_desired_state(controls.ControlState.MOVE_UP)
    control.process()
    assert control.get_state() == controls.ControlState.MOVE_UP

    control.set_desired_state(controls.ControlState.MOVE_DOWN)
    assert control.get_state() == controls.ControlState.MOVE_UP
    control.process()
    assert control.get_state() == controls.ControlState.MOVE_DOWN

    control.set_desired_state(controls.ControlState.MOVE_UP)
    assert control.get_state() == controls.ControlState.MOVE_DOWN
    control.process()
    assert control.get_state() == controls.ControlState.MOVE_UP


def test_control_moving_stop() -> None:
    """Test that we can stop moving."""
    control = controls.Control(
        "test_moving_stop",
        test_timer.TestTimer(),
        moving_duration_ms=10,
        cool_down_duration_ms=5,
    )

    # We should be able to immediately stop moving without changing time, but
    # processing steps are required.
    control.set_desired_state(controls.ControlState.MOVE_UP)
    control.process()
    assert control.get_state() == controls.ControlState.MOVE_UP

    control.set_desired_state(controls.ControlState.IDLE)
    assert control.get_state() == controls.ControlState.MOVE_UP
    control.process()
    assert control.get_state() == controls.ControlState.IDLE

    control.set_desired_state(controls.ControlState.MOVE_DOWN)
    control.process()
    assert control.get_state() == controls.ControlState.MOVE_DOWN

    control.set_desired_state(controls.ControlState.IDLE)
    assert control.get_state() == controls.ControlState.MOVE_DOWN
    control.process()
    assert control.get_state() == controls.ControlState.IDLE


def test_control_cool_down() -> None:
    """Test the cool down state."""
    timer = test_timer.TestTimer()

    moving_duration_ms = 4
    cool_down_duration_ms = 10
    control = controls.Control(
        "test_cool_down", timer, moving_duration_ms, cool_down_duration_ms
    )
    assert control.get_state() == controls.ControlState.IDLE

    # First we need to get into the cool down state.
    control.set_desired_state(controls.ControlState.MOVE_DOWN)
    control.process()
    assert control.get_state() == controls.ControlState.MOVE_DOWN
    timer.set_current_time_ms(moving_duration_ms)
    control.process()
    assert control.get_state() == controls.ControlState.COOL_DOWN

    # We cannot change the state during the cool down.
    for time_ms in range(cool_down_duration_ms):
        timer.set_current_time_ms(moving_duration_ms + time_ms)

        control.set_desired_state(controls.ControlState.IDLE)
        control.process()
        assert control.get_state() == controls.ControlState.COOL_DOWN

        control.set_desired_state(controls.ControlState.MOVE_UP)
        control.process()
        assert control.get_state() == controls.ControlState.COOL_DOWN

        control.set_desired_state(controls.ControlState.MOVE_DOWN)
        control.process()
        assert control.get_state() == controls.ControlState.COOL_DOWN

    # After the cool down is over, we should go idle and stay there.
    timer.set_current_time_ms(moving_duration_ms + cool_down_duration_ms)
    control.process()
    assert control.get_state() == controls.ControlState.IDLE
    control.process()
    assert control.get_state() == controls.ControlState.IDLE
