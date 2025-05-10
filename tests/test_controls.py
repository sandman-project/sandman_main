"""Tests controls."""

import sandman_main.controls as controls


def test_control_initialization() -> None:
    """Test control initialization."""
    assert controls.Control("test1").get_state() == controls.ControlState.IDLE
