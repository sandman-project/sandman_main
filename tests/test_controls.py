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


def test_control_state_transitions() -> None:
    """Test control transitioning between states."""
    control = controls.Control("test2")
    assert control.get_state() == controls.ControlState.IDLE

    # There should be no state change after setting the desired state without
    # processing.
    control.set_desired_state(controls.ControlState.MOVE_UP)
    assert control.get_state() == controls.ControlState.IDLE

    # Immediately after processing the state should change.
    control.process()
    assert control.get_state() == controls.ControlState.MOVE_UP
