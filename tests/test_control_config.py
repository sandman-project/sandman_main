"""Tests configuration for controls."""

import pytest

import sandman_main.control_config as control_config


def _check_default_config(config: control_config.ControlConfig) -> None:
    """Check whether a config is all default values."""
    assert config.name == ""
    assert config.up_gpio_line == -1
    assert config.down_gpio_line == -1
    assert config.moving_duration_ms == -1
    assert config.cool_down_duration_ms == 25
    assert config.is_valid() == False


def test_control_config_initialization() -> None:
    """Test control config initialization."""
    config = control_config.ControlConfig()
    _check_default_config(config)

    # Empty strings are not valid names.
    with pytest.raises(ValueError):
        config.name = ""
    assert config.name == ""

    config.name = "test_control"
    assert config.name == "test_control"
    assert config.is_valid() == False

    with pytest.raises(ValueError):
        config.name = ""
    assert config.name == "test_control"

    with pytest.raises(ValueError):
        config.moving_duration_ms = -1
    assert config.moving_duration_ms == -1

    config.moving_duration_ms = 100
    assert config.moving_duration_ms == 100
    assert config.is_valid() == False

    with pytest.raises(ValueError):
        config.moving_duration_ms = -2
    assert config.moving_duration_ms == 100

    with pytest.raises(ValueError):
        config.cool_down_duration_ms = -1
    assert config.cool_down_duration_ms == 25

    config.cool_down_duration_ms = 1
    assert config.cool_down_duration_ms == 1
    assert config.is_valid() == False

    # Test setting GPIO lines last so that we can test validity when the lines
    # are equal?
    with pytest.raises(ValueError):
        config.up_gpio_line = -1
    assert config.up_gpio_line == -1

    with pytest.raises(ValueError):
        config.down_gpio_line = -1
    assert config.down_gpio_line == -1

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
