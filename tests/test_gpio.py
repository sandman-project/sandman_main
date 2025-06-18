"""Tests GPIO."""

import sandman_main.gpio as gpio


class TestGPIOManager(gpio.GPIOManager):
    """A special-purpose manager for use with testing."""

    # Despite its name, this class should not be collected for testing.
    __test__ = False

    def __init__(self) -> None:
        """Initialize the instance."""
        super().__init__()


def test_gpio_initialization() -> None:
    """Test GPIO initialization."""
    manager: TestGPIOManager = TestGPIOManager()
    assert manager is not None
    assert len(manager.acquired_lines) == 0

    manager.initialize()
    assert len(manager.acquired_lines) == 0

    manager.uninitialize()
    assert len(manager.acquired_lines) == 0


def test_gpio_acquire_lines() -> None:
    """Test acquiring GPIO lines."""
    manager: TestGPIOManager = TestGPIOManager()

    # Cannot acquire lines prior to initialization.
    assert manager.acquire_output_line(1) == False
    assert len(manager.acquired_lines) == 0
