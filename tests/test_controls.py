"""Tests controls."""

import sandman_main.controls as controls


def test_control_initialization() -> None:
    """Test control initialization."""
    # A control should start off idle.
    control = controls.Control("test1")
    assert control.get_state() == controls.ControlState.IDLE

    # It should remain idle without change.
    control.process()
    assert control.get_state() == controls.ControlState.IDLE
