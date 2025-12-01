"""Tests routines."""

import pathlib

import pytest

import sandman_main.controls as controls
import sandman_main.routines as routines

_default_delay_ms = -1
_default_control_name = ""
_default_control_state = controls.Control.State.IDLE


def _check_default_routine_step(step: routines.RoutineDesc.Step) -> None:
    """Check whether a step is all default values."""
    assert step.delay_ms == _default_delay_ms
    assert step.control_name == _default_control_name
    assert step.control_state == _default_control_state
    assert step.is_valid() == False


def test_routine_step_initialization() -> None:
    """Test routine step initialization."""
    step = routines.RoutineDesc.Step()
    _check_default_routine_step(step)

    with pytest.raises(TypeError):
        step.delay_ms = ""
    _check_default_routine_step(step)

    with pytest.raises(ValueError):
        step.delay_ms = -5
    _check_default_routine_step(step)

    intended_delay_ms = 0
    step.delay_ms = intended_delay_ms
    assert step.delay_ms == intended_delay_ms
    assert step.control_name == _default_control_name
    assert step.control_state == _default_control_state
    assert step.is_valid() == False

    with pytest.raises(ValueError):
        step.delay_ms = -1
    assert step.delay_ms == intended_delay_ms
    assert step.control_name == _default_control_name
    assert step.control_state == _default_control_state
    assert step.is_valid() == False

    intended_delay_ms = 1
    step.delay_ms = intended_delay_ms
    assert step.delay_ms == intended_delay_ms
    assert step.control_name == _default_control_name
    assert step.control_state == _default_control_state
    assert step.is_valid() == False

    with pytest.raises(TypeError):
        step.control_name = 1
    assert step.delay_ms == intended_delay_ms
    assert step.control_name == _default_control_name
    assert step.control_state == _default_control_state
    assert step.is_valid() == False

    with pytest.raises(ValueError):
        step.control_name = ""
    assert step.delay_ms == intended_delay_ms
    assert step.control_name == _default_control_name
    assert step.control_state == _default_control_state
    assert step.is_valid() == False

    intended_control_name = "test_control"
    step.control_name = intended_control_name
    assert step.delay_ms == intended_delay_ms
    assert step.control_name == intended_control_name
    assert step.control_state == _default_control_state
    assert step.is_valid() == False

    with pytest.raises(ValueError):
        step.control_name = ""
    assert step.delay_ms == intended_delay_ms
    assert step.control_name == intended_control_name
    assert step.control_state == _default_control_state
    assert step.is_valid() == False

    with pytest.raises(TypeError):
        step.control_state = ""
    assert step.delay_ms == intended_delay_ms
    assert step.control_name == intended_control_name
    assert step.control_state == _default_control_state
    assert step.is_valid() == False

    with pytest.raises(ValueError):
        step.control_state = controls.Control.State.COOL_DOWN
    assert step.delay_ms == intended_delay_ms
    assert step.control_name == intended_control_name
    assert step.control_state == _default_control_state
    assert step.is_valid() == False

    with pytest.raises(ValueError):
        step.control_state = controls.Control.State.IDLE
    assert step.delay_ms == intended_delay_ms
    assert step.control_name == intended_control_name
    assert step.control_state == _default_control_state
    assert step.is_valid() == False

    intended_control_state = controls.Control.State.MOVE_UP
    step.control_state = intended_control_state
    assert step.delay_ms == intended_delay_ms
    assert step.control_name == intended_control_name
    assert step.control_state == intended_control_state
    assert step.is_valid() == True

    with pytest.raises(ValueError):
        step.control_state = controls.Control.State.IDLE
    assert step.delay_ms == intended_delay_ms
    assert step.control_name == intended_control_name
    assert step.control_state == intended_control_state
    assert step.is_valid() == True

    intended_control_state = controls.Control.State.MOVE_DOWN
    step.control_state = intended_control_state
    assert step.delay_ms == intended_delay_ms
    assert step.control_name == intended_control_name
    assert step.control_state == intended_control_state
    assert step.is_valid() == True


_default_name = ""
_default_is_looping = False


def _check_default_routine_desc(desc: routines.RoutineDesc) -> None:
    """Check whether a description is all default values."""
    assert desc.name == _default_name
    assert desc.is_looping == _default_is_looping
    assert desc.is_valid() == False


def test_routine_desc_initialization() -> None:
    """Test routine description initialization."""
    desc = routines.RoutineDesc()
    _check_default_routine_desc(desc)

    with pytest.raises(TypeError):
        desc.is_looping = ""
    _check_default_routine_desc(desc)

    intended_is_looping = True
    desc.is_looping = intended_is_looping
    assert desc.name == _default_name
    assert desc.is_looping == intended_is_looping
    assert desc.is_valid() == False

    with pytest.raises(TypeError):
        desc.name = 1
    assert desc.name == _default_name
    assert desc.is_looping == intended_is_looping
    assert desc.is_valid() == False

    # Empty strings are not valid names.
    with pytest.raises(ValueError):
        desc.name = ""
    assert desc.name == _default_name
    assert desc.is_looping == intended_is_looping
    assert desc.is_valid() == False

    intended_name = "test"
    desc.name = intended_name
    assert desc.name == intended_name
    assert desc.is_looping == intended_is_looping
    assert desc.is_valid() == True

    with pytest.raises(ValueError):
        desc.name = ""
    assert desc.name == intended_name
    assert desc.is_looping == intended_is_looping
    assert desc.is_valid() == True


def test_routine_desc_loading() -> None:
    """Test routine description loading."""


def test_routine_bootstrap(tmp_path: pathlib.Path) -> None:
    """Test routine bootstrapping."""
    reports_path = tmp_path / "routines/"
    assert reports_path.exists() == False

    routines.bootstrap_routines(str(tmp_path) + "/")
    assert reports_path.exists() == True

    # Save a file and make sure it still exists after bootstrapping again.

    routines.bootstrap_routines(str(tmp_path) + "/")
    assert reports_path.exists() == True
