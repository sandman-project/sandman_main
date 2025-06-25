"""Tests GPIO."""

import sandman_main.gpio as gpio


def test_gpio_initialization() -> None:
    """Test GPIO initialization."""
    manager: gpio.GPIOManager = gpio.GPIOManager(is_live_mode=False)
    assert manager is not None
    assert len(manager.acquired_lines) == 0

    manager.initialize()
    assert len(manager.acquired_lines) == 0

    manager.uninitialize()
    assert len(manager.acquired_lines) == 0


def test_gpio_acquire_lines() -> None:
    """Test acquiring GPIO lines."""
    manager: gpio.GPIOManager = gpio.GPIOManager(is_live_mode=False)

    # Cannot acquire lines prior to initialization.
    assert manager.acquire_output_line(2) == False
    assert len(manager.acquired_lines) == 0

    manager.initialize()
    assert len(manager.acquired_lines) == 0

    assert manager.acquire_output_line(2) == True
    lines = manager.acquired_lines
    assert len(lines) == 1
    assert 2 in lines

    assert manager.acquire_output_line(4) == True
    lines = manager.acquired_lines
    assert len(lines) == 2
    assert 2 in lines
    assert 4 in lines

    # Can't acquire same line twice.
    assert manager.acquire_output_line(2) == False

    # Can't release a line that hasn't been acquired.
    assert manager.release_output_line(3) == False

    assert manager.release_output_line(2) == True
    lines = manager.acquired_lines
    assert len(lines) == 1
    assert 4 in lines

    # Can reacquire a line after it has been released.
    assert manager.acquire_output_line(2) == True
    lines = manager.acquired_lines
    assert len(lines) == 2
    assert 2 in lines
    assert 4 in lines

    manager.uninitialize()
    assert len(manager.acquired_lines) == 0


def test_gpio_line_values() -> None:
    """Test setting values on GPIO lines."""
    manager: gpio.GPIOManager = gpio.GPIOManager(is_live_mode=False)

    # Cannot set lines before initialization.
    assert manager.set_line_active(2) == False
    assert manager.set_line_inactive(4) == False
    manager.initialize()

    # Cannot set lines before acquiring.
    assert manager.set_line_active(3) == False
    assert manager.set_line_inactive(2) == False

    assert manager.acquire_output_line(3) == True
    assert manager.set_line_active(3) == True
    assert manager.set_line_inactive(3) == True

    # Cannot set lines after releasing.
    assert manager.release_output_line(3) == True
    assert manager.set_line_active(3) == False
    assert manager.set_line_inactive(3) == False

    # Cannot set lines after uninitialization.
    manager.uninitialize()
    assert manager.set_line_active(3) == False
    assert manager.set_line_inactive(4) == False
