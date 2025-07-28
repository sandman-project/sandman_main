"""Tests configuration for controls."""

import sandman_main.control_config as control_config


def test_control_config_initialization() -> None:
    """Test control config initialization."""
    config = control_config.ControlConfig()
    assert config.name == ""
