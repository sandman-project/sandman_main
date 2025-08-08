"""Tests configuration for controls."""

import pathlib

import pytest

import sandman_main.control_config as control_config

_default_name = ""
_default_gpio_line = -1
_default_moving_duration_ms = -1
_default_cool_down_duration_ms = 25


def _check_default_config(config: control_config.ControlConfig) -> None:
    """Check whether a config is all default values."""
    assert config.name == _default_name
    assert config.up_gpio_line == _default_gpio_line
    assert config.down_gpio_line == _default_gpio_line
    assert config.moving_duration_ms == _default_moving_duration_ms
    assert config.cool_down_duration_ms == _default_cool_down_duration_ms
    assert config.is_valid() == False


def test_control_config_initialization() -> None:
    """Test control config initialization."""
    config = control_config.ControlConfig()
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
        config = control_config.ControlConfig.parse_from_file(path + "a")

    # Empty files cannot be parsed.
    config = control_config.ControlConfig.parse_from_file(
        path + "control_test_empty.ctl"
    )
    _check_default_config(config)

    # Files with improperly formed JSON cannot be parsed.
    config = control_config.ControlConfig.parse_from_file(
        path + "control_test_invalid.ctl"
    )
    _check_default_config(config)

    intended_name = "test"
    intended_up_gpio_line = 1
    intended_down_gpio_line = 2
    intended_moving_duration_ms = 100
    intended_cool_down_duration_ms = 20

    config = control_config.ControlConfig.parse_from_file(
        path + "control_test_missing_name.ctl"
    )
    assert config.name == _default_name
    assert config.up_gpio_line == intended_up_gpio_line
    assert config.down_gpio_line == intended_down_gpio_line
    assert config.moving_duration_ms == intended_moving_duration_ms
    assert config.cool_down_duration_ms == intended_cool_down_duration_ms
    assert config.is_valid() == False

    config = control_config.ControlConfig.parse_from_file(
        path + "control_test_type_name.ctl"
    )
    assert config.name == _default_name
    assert config.up_gpio_line == intended_up_gpio_line
    assert config.down_gpio_line == intended_down_gpio_line
    assert config.moving_duration_ms == intended_moving_duration_ms
    assert config.cool_down_duration_ms == intended_cool_down_duration_ms
    assert config.is_valid() == False

    config = control_config.ControlConfig.parse_from_file(
        path + "control_test_invalid_name.ctl"
    )
    assert config.name == _default_name
    assert config.up_gpio_line == intended_up_gpio_line
    assert config.down_gpio_line == intended_down_gpio_line
    assert config.moving_duration_ms == intended_moving_duration_ms
    assert config.cool_down_duration_ms == intended_cool_down_duration_ms
    assert config.is_valid() == False

    config = control_config.ControlConfig.parse_from_file(
        path + "control_test_missing_up_gpio.ctl"
    )
    assert config.name == intended_name
    assert config.up_gpio_line == _default_gpio_line
    assert config.down_gpio_line == intended_down_gpio_line
    assert config.moving_duration_ms == intended_moving_duration_ms
    assert config.cool_down_duration_ms == intended_cool_down_duration_ms
    assert config.is_valid() == False

    config = control_config.ControlConfig.parse_from_file(
        path + "control_test_type_up_gpio.ctl"
    )
    assert config.name == intended_name
    assert config.up_gpio_line == _default_gpio_line
    assert config.down_gpio_line == intended_down_gpio_line
    assert config.moving_duration_ms == intended_moving_duration_ms
    assert config.cool_down_duration_ms == intended_cool_down_duration_ms
    assert config.is_valid() == False

    config = control_config.ControlConfig.parse_from_file(
        path + "control_test_invalid_up_gpio.ctl"
    )
    assert config.name == intended_name
    assert config.up_gpio_line == _default_gpio_line
    assert config.down_gpio_line == intended_down_gpio_line
    assert config.moving_duration_ms == intended_moving_duration_ms
    assert config.cool_down_duration_ms == intended_cool_down_duration_ms
    assert config.is_valid() == False

    config = control_config.ControlConfig.parse_from_file(
        path + "control_test_missing_down_gpio.ctl"
    )
    assert config.name == intended_name
    assert config.up_gpio_line == intended_up_gpio_line
    assert config.down_gpio_line == _default_gpio_line
    assert config.moving_duration_ms == intended_moving_duration_ms
    assert config.cool_down_duration_ms == intended_cool_down_duration_ms
    assert config.is_valid() == False

    config = control_config.ControlConfig.parse_from_file(
        path + "control_test_type_down_gpio.ctl"
    )
    assert config.name == intended_name
    assert config.up_gpio_line == intended_up_gpio_line
    assert config.down_gpio_line == _default_gpio_line
    assert config.moving_duration_ms == intended_moving_duration_ms
    assert config.cool_down_duration_ms == intended_cool_down_duration_ms
    assert config.is_valid() == False

    config = control_config.ControlConfig.parse_from_file(
        path + "control_test_invalid_down_gpio.ctl"
    )
    assert config.name == intended_name
    assert config.up_gpio_line == intended_up_gpio_line
    assert config.down_gpio_line == _default_gpio_line
    assert config.moving_duration_ms == intended_moving_duration_ms
    assert config.cool_down_duration_ms == intended_cool_down_duration_ms
    assert config.is_valid() == False

    config = control_config.ControlConfig.parse_from_file(
        path + "control_test_missing_moving_duration.ctl"
    )
    assert config.name == intended_name
    assert config.up_gpio_line == intended_up_gpio_line
    assert config.down_gpio_line == intended_down_gpio_line
    assert config.moving_duration_ms == _default_moving_duration_ms
    assert config.cool_down_duration_ms == intended_cool_down_duration_ms
    assert config.is_valid() == False

    config = control_config.ControlConfig.parse_from_file(
        path + "control_test_type_moving_duration.ctl"
    )
    assert config.name == intended_name
    assert config.up_gpio_line == intended_up_gpio_line
    assert config.down_gpio_line == intended_down_gpio_line
    assert config.moving_duration_ms == _default_moving_duration_ms
    assert config.cool_down_duration_ms == intended_cool_down_duration_ms
    assert config.is_valid() == False

    config = control_config.ControlConfig.parse_from_file(
        path + "control_test_invalid_moving_duration.ctl"
    )
    assert config.name == intended_name
    assert config.up_gpio_line == intended_up_gpio_line
    assert config.down_gpio_line == intended_down_gpio_line
    assert config.moving_duration_ms == _default_moving_duration_ms
    assert config.cool_down_duration_ms == intended_cool_down_duration_ms
    assert config.is_valid() == False

    config = control_config.ControlConfig.parse_from_file(
        path + "control_test_missing_cool_down.ctl"
    )
    assert config.name == intended_name
    assert config.up_gpio_line == intended_up_gpio_line
    assert config.down_gpio_line == intended_down_gpio_line
    assert config.moving_duration_ms == intended_moving_duration_ms
    assert config.cool_down_duration_ms == _default_cool_down_duration_ms
    assert config.is_valid() == True

    config = control_config.ControlConfig.parse_from_file(
        path + "control_test_type_cool_down.ctl"
    )
    assert config.name == intended_name
    assert config.up_gpio_line == intended_up_gpio_line
    assert config.down_gpio_line == intended_down_gpio_line
    assert config.moving_duration_ms == intended_moving_duration_ms
    assert config.cool_down_duration_ms == _default_cool_down_duration_ms
    assert config.is_valid() == True

    config = control_config.ControlConfig.parse_from_file(
        path + "control_test_invalid_cool_down.ctl"
    )
    assert config.name == intended_name
    assert config.up_gpio_line == intended_up_gpio_line
    assert config.down_gpio_line == intended_down_gpio_line
    assert config.moving_duration_ms == intended_moving_duration_ms
    assert config.cool_down_duration_ms == _default_cool_down_duration_ms
    assert config.is_valid() == True

    config = control_config.ControlConfig.parse_from_file(
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
    original_config = control_config.ControlConfig()
    assert original_config.is_valid() == False

    file_path = tmp_path / "test_invalid.ctl"
    assert file_path.exists() == False

    original_config.save_to_file(str(file_path))
    assert file_path.exists() == False

    # After writing a valid config, it should be the same when read back in.
    original_config = control_config.ControlConfig.parse_from_file(
        "tests/data/controls/control_test_valid.ctl"
    )
    assert original_config.is_valid() == True
