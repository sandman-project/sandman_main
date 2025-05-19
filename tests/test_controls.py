"""Tests controls."""

import sandman_main.controls as controls
import tests.test_timer as test_timer


def test_control_initialization() -> None:
    """Test control initialization."""
    timer = test_timer.TestTimer()

    # A control should start off idle.
    control = controls.Control("test1", timer)
    assert control.get_state() == controls.ControlState.IDLE

    # It should remain idle without change.
    control.process()
    assert control.get_state() == controls.ControlState.IDLE

    timer.set_current_time_ms(1000)
    control.process()
    assert control.get_state() == controls.ControlState.IDLE


def test_control_state_transitions() -> None:
    """Test control transitioning between states."""
    timer = test_timer.TestTimer()

    control = controls.Control("test2", timer)
    assert control.get_state() == controls.ControlState.IDLE

    # There should be no state change after setting the desired state without
    # processing.
    control.set_desired_state(controls.ControlState.MOVE_UP)
    assert control.get_state() == controls.ControlState.IDLE

    # Immediately after processing the state should change.
    control.process()
    assert control.get_state() == controls.ControlState.MOVE_UP

    # We should remain in this state indefinitely without time changing.
    for _iteration in range(50):
        control.process()
        assert control.get_state() == controls.ControlState.MOVE_UP
