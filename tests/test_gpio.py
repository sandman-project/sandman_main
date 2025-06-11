"""Tests GPIO."""

import sandman_main.gpio as gpio


def test_gpio_initialization() -> None:
    """Test GPIO initialization."""
    manager = gpio.GPIOManager()
    assert manager is not None
