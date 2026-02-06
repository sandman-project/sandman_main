"""Tests controls."""

import json
import pathlib

import pytest
import whenever

import sandman_main.commands as commands
import sandman_main.controls as controls
import sandman_main.gpio as gpio
import sandman_main.reports as reports
import tests.test_time_util as test_time_util

_default_name = ""
_default_gpio_line = -1
_default_moving_duration_ms = -1
_default_cool_down_duration_ms = 25


def _check_default_config(config: controls.ControlConfig) -> None:
    """Check whether a config is all default values."""
    assert config.name == _default_name
    assert config.up_gpio_line == _default_gpio_line
    assert config.down_gpio_line == _default_gpio_line
    assert config.moving_duration_ms == _default_moving_duration_ms
    assert config.cool_down_duration_ms == _default_cool_down_duration_ms
    assert config.is_valid() == False


def _check_file_and_read_lines(file_path: pathlib.Path) -> list[str]:
    """Check that a file exists and read all of its lines."""
    file_exists = file_path.exists()
    assert file_exists == True

    lines = []

    if file_exists == False:
        return lines

    with open(str(file_path)) as file:
        lines = file.readlines()

    return lines


def test_control_config_initialization() -> None:
    """Test control config initialization."""
    config = controls.ControlConfig()
    _check_default_config(config)

    # Empty strings are not valid names.
    with pytest.raises(ValueError):
        config.name = ""
    assert config.name == _default_name

    config.name = "test_control"
    assert config.name == "test_control"
    assert config.is_valid() == False

    with pytest.raises(ValueError):
        config.name = ""
    assert config.name == "test_control"

    with pytest.raises(ValueError):
        config.moving_duration_ms = -1
    assert config.moving_duration_ms == _default_moving_duration_ms

    config.moving_duration_ms = 100
    assert config.moving_duration_ms == 100
    assert config.is_valid() == False

    with pytest.raises(ValueError):
        config.moving_duration_ms = -2
    assert config.moving_duration_ms == 100

    with pytest.raises(ValueError):
        config.cool_down_duration_ms = -1
    assert config.cool_down_duration_ms == _default_cool_down_duration_ms

    config.cool_down_duration_ms = 1
    assert config.cool_down_duration_ms == 1
    assert config.is_valid() == False

    # Test setting GPIO lines last so that we can test validity when the lines
    # are equal?
    with pytest.raises(ValueError):
        config.up_gpio_line = -1
    assert config.up_gpio_line == _default_gpio_line

    with pytest.raises(ValueError):
        config.down_gpio_line = -1
    assert config.down_gpio_line == _default_gpio_line

    config.up_gpio_line = 1
    assert config.up_gpio_line == 1
    assert config.is_valid() == False

    with pytest.raises(ValueError):
        config.up_gpio_line = -2
    assert config.up_gpio_line == 1

    config.down_gpio_line = 1
    assert config.down_gpio_line == 1
    assert config.is_valid() == False

    with pytest.raises(ValueError):
        config.down_gpio_line = -2
    assert config.down_gpio_line == 1

    config.down_gpio_line = 2
    assert config.down_gpio_line == 2
    assert config.is_valid() == True


def test_control_config_loading() -> None:
    """Test control config loading."""
    path: str = "tests/data/controls/"

    with pytest.raises(FileNotFoundError):
        config = controls.ControlConfig.parse_from_file(path + "a")

    # Empty files cannot be parsed.
    config = controls.ControlConfig.parse_from_file(
        path + "control_test_empty.ctl"
    )
    _check_default_config(config)

    # Files with improperly formed JSON cannot be parsed.
    config = controls.ControlConfig.parse_from_file(
        path + "control_test_invalid.ctl"
    )
    _check_default_config(config)

    intended_name = "test"
    intended_up_gpio_line = 1
    intended_down_gpio_line = 2
    intended_moving_duration_ms = 100
    intended_cool_down_duration_ms = 20

    config = controls.ControlConfig.parse_from_file(
        path + "control_test_missing_name.ctl"
    )
    assert config.name == _default_name
    assert config.up_gpio_line == intended_up_gpio_line
    assert config.down_gpio_line == intended_down_gpio_line
    assert config.moving_duration_ms == intended_moving_duration_ms
    assert config.cool_down_duration_ms == intended_cool_down_duration_ms
    assert config.is_valid() == False

    config = controls.ControlConfig.parse_from_file(
        path + "control_test_type_name.ctl"
    )
    assert config.name == _default_name
    assert config.up_gpio_line == intended_up_gpio_line
    assert config.down_gpio_line == intended_down_gpio_line
    assert config.moving_duration_ms == intended_moving_duration_ms
    assert config.cool_down_duration_ms == intended_cool_down_duration_ms
    assert config.is_valid() == False

    config = controls.ControlConfig.parse_from_file(
        path + "control_test_invalid_name.ctl"
    )
    assert config.name == _default_name
    assert config.up_gpio_line == intended_up_gpio_line
    assert config.down_gpio_line == intended_down_gpio_line
    assert config.moving_duration_ms == intended_moving_duration_ms
    assert config.cool_down_duration_ms == intended_cool_down_duration_ms
    assert config.is_valid() == False

    config = controls.ControlConfig.parse_from_file(
        path + "control_test_missing_up_gpio.ctl"
    )
    assert config.name == intended_name
    assert config.up_gpio_line == _default_gpio_line
    assert config.down_gpio_line == intended_down_gpio_line
    assert config.moving_duration_ms == intended_moving_duration_ms
    assert config.cool_down_duration_ms == intended_cool_down_duration_ms
    assert config.is_valid() == False

    config = controls.ControlConfig.parse_from_file(
        path + "control_test_type_up_gpio.ctl"
    )
    assert config.name == intended_name
    assert config.up_gpio_line == _default_gpio_line
    assert config.down_gpio_line == intended_down_gpio_line
    assert config.moving_duration_ms == intended_moving_duration_ms
    assert config.cool_down_duration_ms == intended_cool_down_duration_ms
    assert config.is_valid() == False

    config = controls.ControlConfig.parse_from_file(
        path + "control_test_invalid_up_gpio.ctl"
    )
    assert config.name == intended_name
    assert config.up_gpio_line == _default_gpio_line
    assert config.down_gpio_line == intended_down_gpio_line
    assert config.moving_duration_ms == intended_moving_duration_ms
    assert config.cool_down_duration_ms == intended_cool_down_duration_ms
    assert config.is_valid() == False

    config = controls.ControlConfig.parse_from_file(
        path + "control_test_missing_down_gpio.ctl"
    )
    assert config.name == intended_name
    assert config.up_gpio_line == intended_up_gpio_line
    assert config.down_gpio_line == _default_gpio_line
    assert config.moving_duration_ms == intended_moving_duration_ms
    assert config.cool_down_duration_ms == intended_cool_down_duration_ms
    assert config.is_valid() == False

    config = controls.ControlConfig.parse_from_file(
        path + "control_test_type_down_gpio.ctl"
    )
    assert config.name == intended_name
    assert config.up_gpio_line == intended_up_gpio_line
    assert config.down_gpio_line == _default_gpio_line
    assert config.moving_duration_ms == intended_moving_duration_ms
    assert config.cool_down_duration_ms == intended_cool_down_duration_ms
    assert config.is_valid() == False

    config = controls.ControlConfig.parse_from_file(
        path + "control_test_invalid_down_gpio.ctl"
    )
    assert config.name == intended_name
    assert config.up_gpio_line == intended_up_gpio_line
    assert config.down_gpio_line == _default_gpio_line
    assert config.moving_duration_ms == intended_moving_duration_ms
    assert config.cool_down_duration_ms == intended_cool_down_duration_ms
    assert config.is_valid() == False

    config = controls.ControlConfig.parse_from_file(
        path + "control_test_missing_moving_duration.ctl"
    )
    assert config.name == intended_name
    assert config.up_gpio_line == intended_up_gpio_line
    assert config.down_gpio_line == intended_down_gpio_line
    assert config.moving_duration_ms == _default_moving_duration_ms
    assert config.cool_down_duration_ms == intended_cool_down_duration_ms
    assert config.is_valid() == False

    config = controls.ControlConfig.parse_from_file(
        path + "control_test_type_moving_duration.ctl"
    )
    assert config.name == intended_name
    assert config.up_gpio_line == intended_up_gpio_line
    assert config.down_gpio_line == intended_down_gpio_line
    assert config.moving_duration_ms == _default_moving_duration_ms
    assert config.cool_down_duration_ms == intended_cool_down_duration_ms
    assert config.is_valid() == False

    config = controls.ControlConfig.parse_from_file(
        path + "control_test_invalid_moving_duration.ctl"
    )
    assert config.name == intended_name
    assert config.up_gpio_line == intended_up_gpio_line
    assert config.down_gpio_line == intended_down_gpio_line
    assert config.moving_duration_ms == _default_moving_duration_ms
    assert config.cool_down_duration_ms == intended_cool_down_duration_ms
    assert config.is_valid() == False

    config = controls.ControlConfig.parse_from_file(
        path + "control_test_missing_cool_down.ctl"
    )
    assert config.name == intended_name
    assert config.up_gpio_line == intended_up_gpio_line
    assert config.down_gpio_line == intended_down_gpio_line
    assert config.moving_duration_ms == intended_moving_duration_ms
    assert config.cool_down_duration_ms == _default_cool_down_duration_ms
    assert config.is_valid() == True

    config = controls.ControlConfig.parse_from_file(
        path + "control_test_type_cool_down.ctl"
    )
    assert config.name == intended_name
    assert config.up_gpio_line == intended_up_gpio_line
    assert config.down_gpio_line == intended_down_gpio_line
    assert config.moving_duration_ms == intended_moving_duration_ms
    assert config.cool_down_duration_ms == _default_cool_down_duration_ms
    assert config.is_valid() == True

    config = controls.ControlConfig.parse_from_file(
        path + "control_test_invalid_cool_down.ctl"
    )
    assert config.name == intended_name
    assert config.up_gpio_line == intended_up_gpio_line
    assert config.down_gpio_line == intended_down_gpio_line
    assert config.moving_duration_ms == intended_moving_duration_ms
    assert config.cool_down_duration_ms == _default_cool_down_duration_ms
    assert config.is_valid() == True

    config = controls.ControlConfig.parse_from_file(
        path + "control_test_valid.ctl"
    )
    assert config.name == intended_name
    assert config.up_gpio_line == intended_up_gpio_line
    assert config.down_gpio_line == intended_down_gpio_line
    assert config.moving_duration_ms == intended_moving_duration_ms
    assert config.cool_down_duration_ms == intended_cool_down_duration_ms
    assert config.is_valid() == True


def test_control_config_saving(tmp_path: pathlib.Path) -> None:
    """Test control config saving."""
    # Don't write invalid configs.
    original_config = controls.ControlConfig()
    assert original_config.is_valid() == False

    filename = tmp_path / "test_invalid.ctl"
    assert filename.exists() == False

    original_config.save_to_file(str(filename))
    assert filename.exists() == False

    # After writing a valid config, it should be the same when read back in.
    original_config = controls.ControlConfig.parse_from_file(
        "tests/data/controls/control_test_valid.ctl"
    )
    assert original_config.is_valid() == True

    filename = tmp_path / "test_valid.ctl"
    assert filename.exists() == False

    original_config.save_to_file(str(filename))
    assert filename.exists() == True

    written_config = controls.ControlConfig.parse_from_file(str(filename))
    assert written_config.is_valid() == True
    assert written_config == original_config

    with pytest.raises(OSError):
        original_config.save_to_file("")


def test_control_initialization() -> None:
    """Test control initialization."""
    timer = test_time_util.TestTimer()
    gpio_manager = gpio.GPIOManager(is_live_mode=False)
    gpio_manager.initialize()

    # A control should start off idle.
    control = controls.Control("test_initialization", timer, gpio_manager)
    assert control.state == controls.Control.State.IDLE
    assert len(gpio_manager.acquired_lines) == 0

    notifications = []

    # We cannot use the control before it is initialized.
    with pytest.raises(ValueError):
        control.set_desired_state(controls.Control.State.IDLE)

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
    assert len(gpio_manager.acquired_lines) == 0

    assert (
        control.initialize(
            up_gpio_line=1,
            down_gpio_line=-5,
            moving_duration_ms=10,
            cool_down_duration_ms=5,
        )
        == False
    )
    assert len(gpio_manager.acquired_lines) == 0

    assert (
        control.initialize(
            up_gpio_line=1,
            down_gpio_line=1,
            moving_duration_ms=10,
            cool_down_duration_ms=5,
        )
        == False
    )
    assert len(gpio_manager.acquired_lines) == 0

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
    assert len(gpio_manager.acquired_lines) == 0

    assert (
        control.initialize(
            up_gpio_line=1,
            down_gpio_line=2,
            moving_duration_ms=10,
            cool_down_duration_ms=-1,
        )
        == False
    )
    assert len(gpio_manager.acquired_lines) == 0

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
    acquired_lines = gpio_manager.acquired_lines
    assert len(acquired_lines) == 2
    assert 1 in acquired_lines
    assert 2 in acquired_lines

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
    acquired_lines = gpio_manager.acquired_lines
    assert len(acquired_lines) == 2
    assert 1 in acquired_lines
    assert 2 in acquired_lines

    # It should remain idle without change.
    control.process(notifications)
    assert control.state == controls.Control.State.IDLE

    timer.set_current_time_ms(1000)
    control.process(notifications)
    assert control.state == controls.Control.State.IDLE

    # Make another control to test that different controls cannot use the same
    # GPIO lines.
    control2 = controls.Control("test_initialization2", timer, gpio_manager)

    assert (
        control2.initialize(
            up_gpio_line=1,
            down_gpio_line=3,
            moving_duration_ms=10,
            cool_down_duration_ms=5,
        )
        == False
    )
    acquired_lines = gpio_manager.acquired_lines
    assert len(acquired_lines) == 2
    assert 1 in acquired_lines
    assert 2 in acquired_lines

    assert (
        control2.initialize(
            up_gpio_line=3,
            down_gpio_line=2,
            moving_duration_ms=10,
            cool_down_duration_ms=5,
        )
        == False
    )
    acquired_lines = gpio_manager.acquired_lines
    assert len(acquired_lines) == 2
    assert 1 in acquired_lines
    assert 2 in acquired_lines

    # This one should succeed.
    assert (
        control2.initialize(
            up_gpio_line=3,
            down_gpio_line=4,
            moving_duration_ms=10,
            cool_down_duration_ms=5,
        )
        == True
    )
    acquired_lines = gpio_manager.acquired_lines
    assert len(acquired_lines) == 4
    assert 1 in acquired_lines
    assert 2 in acquired_lines
    assert 3 in acquired_lines
    assert 4 in acquired_lines

    assert control2.uninitialize() == True
    acquired_lines = gpio_manager.acquired_lines
    assert len(acquired_lines) == 2
    assert 1 in acquired_lines
    assert 2 in acquired_lines

    assert control.uninitialize() == True
    assert len(gpio_manager.acquired_lines) == 0
    assert control.uninitialize() == False
    assert len(gpio_manager.acquired_lines) == 0

    gpio_manager.uninitialize()


def _test_control_moving_flow(
    control_name: str,
    desired_state: controls.Control.State,
    moving_duration_ms: int,
    cool_down_duration_ms: int,
) -> None:
    """Test control moving state flow."""
    timer = test_time_util.TestTimer()
    gpio_manager = gpio.GPIOManager(is_live_mode=False)
    gpio_manager.initialize()

    control = controls.Control(
        control_name,
        timer,
        gpio_manager,
    )
    assert control.state == controls.Control.State.IDLE

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
    assert control.state == controls.Control.State.IDLE

    # Immediately after processing the state should change.
    control.process(notifications)
    assert control.state == desired_state

    # We should remain in this state indefinitely without time changing.
    for _iteration in range(50):
        control.process(notifications)
        assert control.state == desired_state

    # We should remain in this state until just before the moving duration is
    # over.
    for time_ms in range(moving_duration_ms):
        timer.set_current_time_ms(time_ms)
        control.process(notifications)
        assert control.state == desired_state

    # After time is up, we should transition to cool down.
    timer.set_current_time_ms(moving_duration_ms)
    control.process(notifications)
    assert control.state == controls.Control.State.COOL_DOWN

    # We should remain in this state until just before the cooldown duration
    # is over.
    for time_ms in range(cool_down_duration_ms):
        timer.set_current_time_ms(moving_duration_ms + time_ms)
        control.process(notifications)
        assert control.state == controls.Control.State.COOL_DOWN

    # After time is up, we should transition to idle.
    timer.set_current_time_ms(moving_duration_ms + cool_down_duration_ms)
    control.process(notifications)
    assert control.state == controls.Control.State.IDLE

    assert control.uninitialize() == True
    gpio_manager.uninitialize()


def test_control_moving_up() -> None:
    """Test control moving up state flow."""
    moving_duration_ms = 10
    cool_down_duration_ms = 4
    _test_control_moving_flow(
        "test_moving_up",
        controls.Control.State.MOVE_UP,
        moving_duration_ms,
        cool_down_duration_ms,
    )


def test_control_moving_down() -> None:
    """Test control moving down state flow."""
    moving_duration_ms = 10
    cool_down_duration_ms = 4
    _test_control_moving_flow(
        "test_moving_down",
        controls.Control.State.MOVE_DOWN,
        moving_duration_ms,
        cool_down_duration_ms,
    )


def test_control_moving_switch() -> None:
    """Test that we can alternate between moving directions."""
    gpio_manager = gpio.GPIOManager(is_live_mode=False)
    gpio_manager.initialize()

    control = controls.Control(
        "test_moving_switch",
        test_time_util.TestTimer(),
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
    control.set_desired_state(controls.Control.State.MOVE_UP)
    control.process(notifications)
    assert control.state == controls.Control.State.MOVE_UP

    control.set_desired_state(controls.Control.State.MOVE_DOWN)
    assert control.state == controls.Control.State.MOVE_UP
    control.process(notifications)
    assert control.state == controls.Control.State.MOVE_DOWN

    control.set_desired_state(controls.Control.State.MOVE_UP)
    assert control.state == controls.Control.State.MOVE_DOWN
    control.process(notifications)
    assert control.state == controls.Control.State.MOVE_UP

    assert control.uninitialize() == True
    gpio_manager.uninitialize()


def test_control_moving_switch_time() -> None:
    """Test that switching moving direction resets the duration."""
    timer = test_time_util.TestTimer()
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

    control.set_desired_state(controls.Control.State.MOVE_DOWN)
    control.process(notifications)
    assert control.state == controls.Control.State.MOVE_DOWN

    time_before_switch_ms = 4
    timer.set_current_time_ms(time_before_switch_ms)
    control.set_desired_state(controls.Control.State.MOVE_UP)
    control.process(notifications)
    assert control.state == controls.Control.State.MOVE_UP

    # The duration after switch should be the full moving duration.
    for time_ms in range(moving_duration_ms):
        timer.set_current_time_ms(time_before_switch_ms + time_ms)
        control.process(notifications)
        assert control.state == controls.Control.State.MOVE_UP

    timer.set_current_time_ms(time_before_switch_ms + moving_duration_ms)
    control.process(notifications)
    assert control.state == controls.Control.State.COOL_DOWN

    assert control.uninitialize() == True
    gpio_manager.uninitialize()


def test_control_moving_stop() -> None:
    """Test that we can stop moving."""
    gpio_manager = gpio.GPIOManager(is_live_mode=False)
    gpio_manager.initialize()

    control = controls.Control(
        "test_moving_stop",
        test_time_util.TestTimer(),
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
    control.set_desired_state(controls.Control.State.MOVE_UP)
    control.process(notifications)
    assert control.state == controls.Control.State.MOVE_UP

    control.set_desired_state(controls.Control.State.IDLE)
    assert control.state == controls.Control.State.MOVE_UP
    control.process(notifications)
    assert control.state == controls.Control.State.COOL_DOWN

    assert control.uninitialize() == True

    control = controls.Control(
        "test_moving_stop",
        test_time_util.TestTimer(),
        gpio_manager,
    )
    control.initialize(
        up_gpio_line=1,
        down_gpio_line=2,
        moving_duration_ms=10,
        cool_down_duration_ms=5,
    )

    control.set_desired_state(controls.Control.State.MOVE_DOWN)
    control.process(notifications)
    assert control.state == controls.Control.State.MOVE_DOWN

    control.set_desired_state(controls.Control.State.IDLE)
    assert control.state == controls.Control.State.MOVE_DOWN
    control.process(notifications)
    assert control.state == controls.Control.State.COOL_DOWN

    assert control.uninitialize() == True
    gpio_manager.uninitialize()


def test_control_cool_down() -> None:
    """Test the cool down state."""
    timer = test_time_util.TestTimer()
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
    assert control.state == controls.Control.State.IDLE

    notifications: list[str] = []

    # First we need to get into the cool down state.
    control.set_desired_state(controls.Control.State.MOVE_DOWN)
    control.process(notifications)
    assert control.state == controls.Control.State.MOVE_DOWN
    timer.set_current_time_ms(moving_duration_ms)
    control.process(notifications)
    assert control.state == controls.Control.State.COOL_DOWN

    # We cannot change the state during the cool down.
    for time_ms in range(cool_down_duration_ms):
        timer.set_current_time_ms(moving_duration_ms + time_ms)

        control.set_desired_state(controls.Control.State.IDLE)
        control.process(notifications)
        assert control.state == controls.Control.State.COOL_DOWN

        control.set_desired_state(controls.Control.State.MOVE_UP)
        control.process(notifications)
        assert control.state == controls.Control.State.COOL_DOWN

        control.set_desired_state(controls.Control.State.MOVE_DOWN)
        control.process(notifications)
        assert control.state == controls.Control.State.COOL_DOWN

    # After the cool down is over, we should go idle and stay there.
    timer.set_current_time_ms(moving_duration_ms + cool_down_duration_ms)
    control.process(notifications)
    assert control.state == controls.Control.State.IDLE
    control.process(notifications)
    assert control.state == controls.Control.State.IDLE

    assert control.uninitialize() == True
    gpio_manager.uninitialize()


def test_control_no_desired_cool_down() -> None:
    """Test that we cannot set cool down as a desired state."""
    gpio_manager = gpio.GPIOManager(is_live_mode=False)
    gpio_manager.initialize()

    control = controls.Control(
        "test_desired_cool_down",
        test_time_util.TestTimer(),
        gpio_manager,
    )
    control.initialize(
        up_gpio_line=1,
        down_gpio_line=2,
        moving_duration_ms=10,
        cool_down_duration_ms=5,
    )

    notifications: list[str] = []

    assert control.state == controls.Control.State.IDLE
    control.set_desired_state(controls.Control.State.COOL_DOWN)
    control.process(notifications)
    assert control.state == controls.Control.State.IDLE

    control.set_desired_state(controls.Control.State.MOVE_DOWN)
    control.process(notifications)
    assert control.state == controls.Control.State.MOVE_DOWN
    control.set_desired_state(controls.Control.State.COOL_DOWN)
    control.process(notifications)
    assert control.state == controls.Control.State.MOVE_DOWN

    control.set_desired_state(controls.Control.State.MOVE_UP)
    control.process(notifications)
    assert control.state == controls.Control.State.MOVE_UP
    control.set_desired_state(controls.Control.State.COOL_DOWN)
    control.process(notifications)
    assert control.state == controls.Control.State.MOVE_UP

    assert control.uninitialize() == True
    gpio_manager.uninitialize()


def _check_control_state(
    states: dict[str, controls.Control.State],
    name: str,
    state: controls.Control.State,
) -> None:
    """Check that a control with a name exists with the expected state."""
    assert name in states
    if name in states:
        assert states[name] == state


def test_control_manager(tmp_path: pathlib.Path) -> None:
    """Test the control manager."""
    timer = test_time_util.TestTimer()

    gpio_manager = gpio.GPIOManager(is_live_mode=False)
    gpio_manager.initialize()

    time_source = test_time_util.TestTimeSource()

    first_time = whenever.ZonedDateTime(
        year=2025,
        month=9,
        day=28,
        hour=16,
        minute=59,
        second=59,
        tz="America/Chicago",
    )
    time_source.set_current_time(first_time)
    assert time_source.get_current_time() == first_time

    reports_path = tmp_path / "reports/"
    reports.bootstrap_reports(str(tmp_path) + "/")
    assert reports_path.exists() == True

    report_manager = reports.ReportManager(time_source, str(tmp_path) + "/")

    controls.bootstrap_controls(str(tmp_path) + "/")

    control_manager = controls.ControlManager(
        timer, gpio_manager, report_manager
    )
    assert control_manager.num_controls == 0

    num_expected_controls = 3
    control_manager.initialize(str(tmp_path) + "/")
    assert control_manager.num_controls == num_expected_controls

    # Initializing again doesn't double up.
    control_manager.initialize(str(tmp_path) + "/")
    assert control_manager.num_controls == num_expected_controls

    control_manager.uninitialize()
    assert control_manager.num_controls == 0

    # Now that we have tested various loading situations, test manipulating
    # controls.
    control_manager.initialize(str(tmp_path) + "/")
    assert control_manager.num_controls == num_expected_controls
    states = control_manager.get_states()
    _check_control_state(states, "back", controls.Control.State.IDLE)
    _check_control_state(states, "legs", controls.Control.State.IDLE)
    _check_control_state(states, "elevation", controls.Control.State.IDLE)

    # Commands for nonexistent controls fail.
    command = commands.ControlCommand(
        "chicken", commands.ControlCommand.Direction.DOWN, "test"
    )
    assert control_manager.process_command(command) == False
    states = control_manager.get_states()
    _check_control_state(states, "back", controls.Control.State.IDLE)
    _check_control_state(states, "legs", controls.Control.State.IDLE)
    _check_control_state(states, "elevation", controls.Control.State.IDLE)

    # Commands for controls that exist succeed, but state doesn't update before
    # processing.
    command = commands.ControlCommand(
        "back", commands.ControlCommand.Direction.DOWN, "test"
    )
    assert control_manager.process_command(command) == True
    states = control_manager.get_states()
    _check_control_state(states, "back", controls.Control.State.IDLE)
    _check_control_state(states, "legs", controls.Control.State.IDLE)
    _check_control_state(states, "elevation", controls.Control.State.IDLE)

    command = commands.ControlCommand(
        "elevation", commands.ControlCommand.Direction.UP, "test"
    )
    assert control_manager.process_command(command) == True
    states = control_manager.get_states()
    _check_control_state(states, "back", controls.Control.State.IDLE)
    _check_control_state(states, "legs", controls.Control.State.IDLE)
    _check_control_state(states, "elevation", controls.Control.State.IDLE)

    # Make sure that the correct events were written to the report file.
    report_manager.process()

    report_path = reports_path / "sandman2025-09-27.rpt"
    report_lines = _check_file_and_read_lines(report_path)

    assert len(report_lines) == 3

    header = json.loads(report_lines[0])
    assert header["version"] == reports.ReportManager.REPORT_VERSION

    event_json = json.loads(report_lines[1])
    event_time = whenever.ZonedDateTime.parse_common_iso(event_json["when"])
    assert event_time == first_time
    assert event_json["info"] == {
        "type": "control",
        "control": "back",
        "action": "down",
        "source": "test",
    }

    event_json = json.loads(report_lines[2])
    event_time = whenever.ZonedDateTime.parse_common_iso(event_json["when"])
    assert event_time == first_time
    assert event_json["info"] == {
        "type": "control",
        "control": "elevation",
        "action": "up",
        "source": "test",
    }

    # State changes happen after processing.
    notification_list = []
    control_manager.process_controls(notification_list)
    assert len(notification_list) == 2
    assert "Lowering the back." in notification_list
    assert "Raising the elevation." in notification_list
    states = control_manager.get_states()
    _check_control_state(states, "back", controls.Control.State.MOVE_DOWN)
    _check_control_state(states, "legs", controls.Control.State.IDLE)
    _check_control_state(states, "elevation", controls.Control.State.MOVE_UP)

    # But nothing happens if we process again without advancing time.
    notification_list = []
    control_manager.process_controls(notification_list)
    assert len(notification_list) == 0
    states = control_manager.get_states()
    _check_control_state(states, "back", controls.Control.State.MOVE_DOWN)
    _check_control_state(states, "legs", controls.Control.State.IDLE)
    _check_control_state(states, "elevation", controls.Control.State.MOVE_UP)

    # If we advance enough time, the elevation should stop.
    timer.set_current_time_ms(4000)
    notification_list = []
    control_manager.process_controls(notification_list)
    assert len(notification_list) == 1
    assert "elevation stopped." in notification_list
    states = control_manager.get_states()
    _check_control_state(states, "back", controls.Control.State.MOVE_DOWN)
    _check_control_state(states, "legs", controls.Control.State.IDLE)
    _check_control_state(states, "elevation", controls.Control.State.COOL_DOWN)


def test_control_bootstrap(tmp_path: pathlib.Path) -> None:
    """Test control bootstrapping."""
    control_path = tmp_path / "controls/"
    assert control_path.exists() == False

    controls.bootstrap_controls(str(tmp_path) + "/")
    assert control_path.exists() == True

    back_control_path = control_path / "back.ctl"
    assert back_control_path.exists() == True

    back_config = controls.ControlConfig.parse_from_file(
        str(back_control_path)
    )
    assert back_config.name == "back"
    assert back_config.up_gpio_line == 20
    assert back_config.down_gpio_line == 16
    assert back_config.moving_duration_ms == 7000
    assert back_config.cool_down_duration_ms == 25
    assert back_config.is_valid() == True

    legs_control_path = control_path / "legs.ctl"
    assert legs_control_path.exists() == True

    legs_config = controls.ControlConfig.parse_from_file(
        str(legs_control_path)
    )
    assert legs_config.name == "legs"
    assert legs_config.up_gpio_line == 13
    assert legs_config.down_gpio_line == 26
    assert legs_config.moving_duration_ms == 4000
    assert legs_config.cool_down_duration_ms == 25
    assert legs_config.is_valid() == True

    elevation_control_path = control_path / "elevation.ctl"
    assert elevation_control_path.exists() == True

    elevation_config = controls.ControlConfig.parse_from_file(
        str(elevation_control_path)
    )
    assert elevation_config.name == "elevation"
    assert elevation_config.up_gpio_line == 5
    assert elevation_config.down_gpio_line == 19
    assert elevation_config.moving_duration_ms == 4000
    assert elevation_config.cool_down_duration_ms == 25
    assert elevation_config.is_valid() == True
