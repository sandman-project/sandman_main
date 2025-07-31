"""Tests configuration for controls."""

import pytest

import sandman_main.control_config as control_config


def test_control_config_initialization() -> None:
    """Test control config initialization."""
    config = control_config.ControlConfig()
    assert config.name == ""
    assert config.up_gpio_line == -1
    assert config.down_gpio_line == -1
    assert config.moving_duration_ms == -1
    assert config.cool_down_duration_ms == 25
    assert config.is_valid() == False

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
