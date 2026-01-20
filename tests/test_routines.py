"""Tests routines."""

import pathlib

import pytest

import sandman_main.commands as commands
import sandman_main.routines as routines
import tests.test_time_util as test_time_util

_default_delay_ms = -1
_default_control_name = ""
_default_move_direction = commands.MoveControlCommand.Direction.UP


def _check_default_routine_step(step: routines.RoutineDesc.Step) -> None:
    """Check whether a step is all default values."""
    assert step.delay_ms == _default_delay_ms
    assert step.control_name == _default_control_name
    assert step.move_direction == _default_move_direction
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
    assert step.move_direction == _default_move_direction
    assert step.is_valid() == False

    with pytest.raises(ValueError):
        step.delay_ms = -1
    assert step.delay_ms == intended_delay_ms
    assert step.control_name == _default_control_name
    assert step.move_direction == _default_move_direction
    assert step.is_valid() == False

    intended_delay_ms = 1
    step.delay_ms = intended_delay_ms
    assert step.delay_ms == intended_delay_ms
    assert step.control_name == _default_control_name
    assert step.move_direction == _default_move_direction
    assert step.is_valid() == False

    with pytest.raises(TypeError):
        step.control_name = 1
    assert step.delay_ms == intended_delay_ms
    assert step.control_name == _default_control_name
    assert step.move_direction == _default_move_direction
    assert step.is_valid() == False

    with pytest.raises(ValueError):
        step.control_name = ""
    assert step.delay_ms == intended_delay_ms
    assert step.control_name == _default_control_name
    assert step.move_direction == _default_move_direction
    assert step.is_valid() == False

    intended_control_name = "test_control"
    step.control_name = intended_control_name
    assert step.delay_ms == intended_delay_ms
    assert step.control_name == intended_control_name
    assert step.move_direction == _default_move_direction
    assert step.is_valid() == True

    with pytest.raises(ValueError):
        step.control_name = ""
    assert step.delay_ms == intended_delay_ms
    assert step.control_name == intended_control_name
    assert step.move_direction == _default_move_direction
    assert step.is_valid() == True

    with pytest.raises(TypeError):
        step.move_direction = ""
    assert step.delay_ms == intended_delay_ms
    assert step.control_name == intended_control_name
    assert step.move_direction == _default_move_direction
    assert step.is_valid() == True

    intended_move_direction = commands.MoveControlCommand.Direction.DOWN
    step.move_direction = intended_move_direction
    assert step.delay_ms == intended_delay_ms
    assert step.control_name == intended_control_name
    assert step.move_direction == intended_move_direction
    assert step.is_valid() == True

    with pytest.raises(TypeError):
        step.move_direction = 1
    assert step.delay_ms == intended_delay_ms
    assert step.control_name == intended_control_name
    assert step.move_direction == intended_move_direction
    assert step.is_valid() == True

    intended_move_direction = commands.MoveControlCommand.Direction.UP
    step.move_direction = intended_move_direction
    assert step.delay_ms == intended_delay_ms
    assert step.control_name == intended_control_name
    assert step.move_direction == intended_move_direction
    assert step.is_valid() == True


_default_name = ""
_default_is_looping = False


def _check_default_routine_desc(desc: routines.RoutineDesc) -> None:
    """Check whether a description is all default values."""
    assert desc.name == _default_name
    assert desc.is_looping == _default_is_looping
    assert len(desc.steps) == 0
    assert desc.is_valid() == False


def _check_intended_routine_steps(
    steps: list[routines.RoutineDesc.Step],
    intended_steps: list[routines.RoutineDesc.Step],
) -> None:
    """Check whether routine steps match intended values."""
    num_steps = len(steps)
    num_intended_steps = len(intended_steps)
    assert num_steps == num_intended_steps

    if num_steps != num_intended_steps:
        return

    for index in range(num_steps):
        assert steps[index] == intended_steps[index]


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
    assert len(desc.steps) == 0
    assert desc.is_valid() == False

    with pytest.raises(TypeError):
        desc.name = 1
    assert desc.name == _default_name
    assert desc.is_looping == intended_is_looping
    assert len(desc.steps) == 0
    assert desc.is_valid() == False

    # Empty strings are not valid names.
    with pytest.raises(ValueError):
        desc.name = ""
    assert desc.name == _default_name
    assert desc.is_looping == intended_is_looping
    assert len(desc.steps) == 0
    assert desc.is_valid() == False

    intended_name = "test"
    desc.name = intended_name
    assert desc.name == intended_name
    assert desc.is_looping == intended_is_looping
    assert len(desc.steps) == 0
    assert desc.is_valid() == True

    with pytest.raises(ValueError):
        desc.name = ""
    assert desc.name == intended_name
    assert desc.is_looping == intended_is_looping
    assert len(desc.steps) == 0
    assert desc.is_valid() == True

    first_step = routines.RoutineDesc.Step()
    with pytest.raises(ValueError):
        desc.append_step(first_step)
    assert desc.name == intended_name
    assert desc.is_looping == intended_is_looping
    assert len(desc.steps) == 0
    assert desc.is_valid() == True

    first_step.delay_ms = 1
    first_step.control_name = "test_control"
    first_step.move_direction = commands.MoveControlCommand.Direction.UP
    assert first_step.is_valid() == True
    desc.append_step(first_step)
    assert desc.name == intended_name
    assert desc.is_looping == intended_is_looping
    _check_intended_routine_steps(desc.steps, [first_step])
    assert desc.is_valid() == True

    second_step = routines.RoutineDesc.Step()
    second_step.delay_ms = 2
    second_step.control_name = "test_control"
    second_step.move_direction = commands.MoveControlCommand.Direction.DOWN
    assert second_step.is_valid() == True
    desc.append_step(second_step)
    assert desc.name == intended_name
    assert desc.is_looping == intended_is_looping
    _check_intended_routine_steps(desc.steps, [first_step, second_step])
    assert desc.is_valid() == True


def test_routine_desc_loading() -> None:
    """Test routine description loading."""
    path: str = "tests/data/routines/"

    with pytest.raises(FileNotFoundError):
        desc = routines.RoutineDesc.parse_from_file(path + "a")

    # Empty files cannot be parsed.
    desc = routines.RoutineDesc.parse_from_file(
        path + "routine_test_empty.rtn"
    )
    _check_default_routine_desc(desc)

    # Files with improperly formed JSON cannot be parsed.
    desc = routines.RoutineDesc.parse_from_file(
        path + "routine_test_invalid.rtn"
    )
    _check_default_routine_desc(desc)

    intended_name = "test"
    intended_is_looping = True

    intended_step0 = routines.RoutineDesc.Step()
    intended_step0.delay_ms = 1
    intended_step0.control_name = "test_control"
    intended_step0.move_direction = commands.MoveControlCommand.Direction.UP
    assert intended_step0.is_valid() == True

    intended_step1 = routines.RoutineDesc.Step()
    intended_step1.delay_ms = 2
    intended_step1.control_name = "test_control"
    intended_step1.move_direction = commands.MoveControlCommand.Direction.DOWN
    assert intended_step1.is_valid() == True

    intended_steps = [intended_step0, intended_step1]

    desc = routines.RoutineDesc.parse_from_file(
        path + "routine_test_missing_name.rtn"
    )
    assert desc.name == _default_name
    assert desc.is_looping == intended_is_looping
    _check_intended_routine_steps(desc.steps, intended_steps)
    assert desc.is_valid() == False

    desc = routines.RoutineDesc.parse_from_file(
        path + "routine_test_type_name.rtn"
    )
    assert desc.name == _default_name
    assert desc.is_looping == intended_is_looping
    _check_intended_routine_steps(desc.steps, intended_steps)
    assert desc.is_valid() == False

    desc = routines.RoutineDesc.parse_from_file(
        path + "routine_test_invalid_name.rtn"
    )
    assert desc.name == _default_name
    assert desc.is_looping == intended_is_looping
    _check_intended_routine_steps(desc.steps, intended_steps)
    assert desc.is_valid() == False

    desc = routines.RoutineDesc.parse_from_file(
        path + "routine_test_missing_looping.rtn"
    )
    assert desc.name == intended_name
    assert desc.is_looping == _default_is_looping
    _check_intended_routine_steps(desc.steps, intended_steps)
    assert desc.is_valid() == True

    desc = routines.RoutineDesc.parse_from_file(
        path + "routine_test_type_looping.rtn"
    )
    assert desc.name == intended_name
    assert desc.is_looping == _default_is_looping
    _check_intended_routine_steps(desc.steps, intended_steps)
    assert desc.is_valid() == True

    desc = routines.RoutineDesc.parse_from_file(
        path + "routine_test_missing_steps.rtn"
    )
    assert desc.name == intended_name
    assert desc.is_looping == intended_is_looping
    assert len(desc.steps) == 0
    assert desc.is_valid() == True

    desc = routines.RoutineDesc.parse_from_file(
        path + "routine_test_type_steps.rtn"
    )
    assert desc.name == intended_name
    assert desc.is_looping == intended_is_looping
    assert len(desc.steps) == 0
    assert desc.is_valid() == True

    desc = routines.RoutineDesc.parse_from_file(
        path + "routine_test_step_missing_delay.rtn"
    )
    assert desc.name == intended_name
    assert desc.is_looping == intended_is_looping
    _check_intended_routine_steps(desc.steps, [intended_step1])
    assert desc.is_valid() == True

    desc = routines.RoutineDesc.parse_from_file(
        path + "routine_test_step_type_delay.rtn"
    )
    assert desc.name == intended_name
    assert desc.is_looping == intended_is_looping
    _check_intended_routine_steps(desc.steps, [intended_step1])
    assert desc.is_valid() == True

    desc = routines.RoutineDesc.parse_from_file(
        path + "routine_test_step_invalid_delay.rtn"
    )
    assert desc.name == intended_name
    assert desc.is_looping == intended_is_looping
    _check_intended_routine_steps(desc.steps, [intended_step1])
    assert desc.is_valid() == True

    desc = routines.RoutineDesc.parse_from_file(
        path + "routine_test_step_missing_control_name.rtn"
    )
    assert desc.name == intended_name
    assert desc.is_looping == intended_is_looping
    _check_intended_routine_steps(desc.steps, [intended_step1])
    assert desc.is_valid() == True

    desc = routines.RoutineDesc.parse_from_file(
        path + "routine_test_step_type_control_name.rtn"
    )
    assert desc.name == intended_name
    assert desc.is_looping == intended_is_looping
    _check_intended_routine_steps(desc.steps, [intended_step1])
    assert desc.is_valid() == True

    desc = routines.RoutineDesc.parse_from_file(
        path + "routine_test_step_invalid_control_name.rtn"
    )
    assert desc.name == intended_name
    assert desc.is_looping == intended_is_looping
    _check_intended_routine_steps(desc.steps, [intended_step1])
    assert desc.is_valid() == True

    desc = routines.RoutineDesc.parse_from_file(
        path + "routine_test_step_missing_move_direction.rtn"
    )
    assert desc.name == intended_name
    assert desc.is_looping == intended_is_looping
    _check_intended_routine_steps(desc.steps, intended_steps)
    assert desc.is_valid() == True

    desc = routines.RoutineDesc.parse_from_file(
        path + "routine_test_step_type_move_direction.rtn"
    )
    assert desc.name == intended_name
    assert desc.is_looping == intended_is_looping
    _check_intended_routine_steps(desc.steps, intended_steps)
    assert desc.is_valid() == True

    desc = routines.RoutineDesc.parse_from_file(
        path + "routine_test_step_invalid_move_direction.rtn"
    )
    assert desc.name == intended_name
    assert desc.is_looping == intended_is_looping
    _check_intended_routine_steps(desc.steps, intended_steps)
    assert desc.is_valid() == True

    desc = routines.RoutineDesc.parse_from_file(
        path + "routine_test_valid_no_steps.rtn"
    )
    assert desc.name == intended_name
    assert desc.is_looping == intended_is_looping
    assert len(desc.steps) == 0
    assert desc.is_valid() == True

    desc = routines.RoutineDesc.parse_from_file(
        path + "routine_test_valid_steps.rtn"
    )
    assert desc.name == intended_name
    assert desc.is_looping == intended_is_looping
    _check_intended_routine_steps(desc.steps, intended_steps)
    assert desc.is_valid() == True


def test_routine_desc_saving(tmp_path: pathlib.Path) -> None:
    """Test routine description saving."""
    # Don't write invalid descriptions.
    original_desc = routines.RoutineDesc()
    assert original_desc.is_valid() == False

    filename = tmp_path / "test_invalid.rtn"
    assert filename.exists() == False

    original_desc.save_to_file(str(filename))
    assert filename.exists() == False

    # After writing a valid routine description, it should be the same when
    # read back in.
    original_desc = routines.RoutineDesc.parse_from_file(
        "tests/data/routines/routine_test_valid_steps.rtn"
    )
    assert original_desc.is_valid() == True

    filename = tmp_path / "test_valid.rtn"
    assert filename.exists() == False

    original_desc.save_to_file(str(filename))
    assert filename.exists() == True

    written_desc = routines.RoutineDesc.parse_from_file(str(filename))
    assert written_desc.is_valid() == True
    assert written_desc == original_desc

    with pytest.raises(OSError):
        original_desc.save_to_file("")


def test_routines() -> None:
    """Test routine functionality."""
    timer = test_time_util.TestTimer()

    no_steps_desc = routines.RoutineDesc.parse_from_file(
        "tests/data/routines/routine_test_valid_no_steps.rtn"
    )
    assert no_steps_desc.is_valid() == True
    assert no_steps_desc.is_looping == True
    assert len(no_steps_desc.steps) == 0

    no_steps_non_looping_desc = routines.RoutineDesc.parse_from_file(
        "tests/data/routines/routine_test_valid_no_steps.rtn"
    )
    no_steps_non_looping_desc.is_looping = False
    assert no_steps_non_looping_desc.is_valid() == True
    assert len(no_steps_non_looping_desc.steps) == 0

    steps_desc = routines.RoutineDesc.parse_from_file(
        "tests/data/routines/routine_test_valid_steps.rtn"
    )
    assert steps_desc.is_valid() == True
    assert steps_desc.is_looping == True
    assert len(steps_desc.steps) == 2

    steps_non_looping_desc = routines.RoutineDesc.parse_from_file(
        "tests/data/routines/routine_test_valid_steps.rtn"
    )
    steps_non_looping_desc.is_looping = False
    assert steps_non_looping_desc.is_valid() == True
    assert len(steps_non_looping_desc.steps) == 2

    steps_non_looping_no_delay_desc = routines.RoutineDesc.parse_from_file(
        "tests/data/routines/routine_test_valid_steps.rtn"
    )
    steps_non_looping_no_delay_desc.is_looping = False
    assert steps_non_looping_no_delay_desc.is_valid() == True
    assert len(steps_non_looping_no_delay_desc.steps) == 2
    steps_non_looping_no_delay_desc.steps[0].delay_ms = 0

    # Routines can't finish before processing.
    no_steps = routines.Routine(no_steps_desc, timer)
    no_steps_non_looping = routines.Routine(no_steps_non_looping_desc, timer)
    steps = routines.Routine(steps_desc, timer)
    steps_non_looping = routines.Routine(steps_non_looping_desc, timer)
    steps_non_looping_no_delay = routines.Routine(
        steps_non_looping_no_delay_desc, timer
    )
    assert no_steps.is_finished == False
    assert no_steps_non_looping.is_finished == False
    assert steps.is_finished == False
    assert steps_non_looping.is_finished == False
    assert steps_non_looping_no_delay.is_finished == False

    intended_control_name = "test_control"
    up_command = commands.MoveControlCommand(
        intended_control_name,
        commands.MoveControlCommand.Direction.UP,
        "routine",
    )
    down_command = commands.MoveControlCommand(
        intended_control_name,
        commands.MoveControlCommand.Direction.DOWN,
        "routine",
    )

    # Non-looping routines with no steps are finished instantly.
    command_list = []
    no_steps.process(command_list)
    assert len(command_list) == 0
    assert no_steps.is_finished == False

    command_list = []
    no_steps_non_looping.process(command_list)
    assert len(command_list) == 0
    assert no_steps_non_looping.is_finished == True

    command_list = []
    steps.process(command_list)
    assert len(command_list) == 0
    assert steps.is_finished == False

    command_list = []
    steps_non_looping.process(command_list)
    assert len(command_list) == 0
    assert steps_non_looping.is_finished == False

    # The routine with zero initial delay will instantly produce a command.
    command_list = []
    steps_non_looping_no_delay.process(command_list)
    assert len(command_list) == 1
    if len(command_list) > 0:
        assert command_list[0] == up_command
    assert steps_non_looping_no_delay.is_finished == False

    # Processing again doesn't change anything.
    command_list = []
    no_steps.process(command_list)
    assert len(command_list) == 0
    assert no_steps.is_finished == False

    command_list = []
    no_steps_non_looping.process(command_list)
    assert len(command_list) == 0
    assert no_steps_non_looping.is_finished == True

    command_list = []
    steps.process(command_list)
    assert len(command_list) == 0
    assert steps.is_finished == False

    command_list = []
    steps_non_looping.process(command_list)
    assert len(command_list) == 0
    assert steps_non_looping.is_finished == False

    command_list = []
    steps_non_looping_no_delay.process(command_list)
    assert len(command_list) == 0
    assert steps_non_looping_no_delay.is_finished == False

    # Advancing time 1 ms should execute the first step, if there is one.
    # Except for the routine with zero initial delay.
    timer.set_current_time_ms(1)

    command_list = []
    no_steps.process(command_list)
    assert len(command_list) == 0
    assert no_steps.is_finished == False

    command_list = []
    no_steps_non_looping.process(command_list)
    assert len(command_list) == 0
    assert no_steps_non_looping.is_finished == True

    command_list = []
    steps.process(command_list)
    assert len(command_list) == 1
    if len(command_list) > 0:
        assert command_list[0] == up_command
    assert steps.is_finished == False

    command_list = []
    steps_non_looping.process(command_list)
    assert len(command_list) == 1
    if len(command_list) > 0:
        assert command_list[0] == up_command
    assert steps_non_looping.is_finished == False

    command_list = []
    steps_non_looping_no_delay.process(command_list)
    assert len(command_list) == 0
    assert steps_non_looping_no_delay.is_finished == False

    # Processing again does nothing.
    command_list = []
    no_steps.process(command_list)
    assert len(command_list) == 0
    assert no_steps.is_finished == False

    command_list = []
    no_steps_non_looping.process(command_list)
    assert len(command_list) == 0
    assert no_steps_non_looping.is_finished == True

    command_list = []
    steps.process(command_list)
    assert len(command_list) == 0
    assert steps.is_finished == False

    command_list = []
    steps_non_looping.process(command_list)
    assert len(command_list) == 0
    assert steps_non_looping.is_finished == False

    command_list = []
    steps_non_looping_no_delay.process(command_list)
    assert len(command_list) == 0
    assert steps_non_looping_no_delay.is_finished == False

    # Advancing another millisecond does nothing, because the delay hasn't
    # passed. Except for the routine with zero initial delay, which will
    # finish.
    timer.set_current_time_ms(2)

    command_list = []
    no_steps.process(command_list)
    assert len(command_list) == 0
    assert no_steps.is_finished == False

    command_list = []
    no_steps_non_looping.process(command_list)
    assert len(command_list) == 0
    assert no_steps_non_looping.is_finished == True

    command_list = []
    steps.process(command_list)
    assert len(command_list) == 0
    assert steps.is_finished == False

    command_list = []
    steps_non_looping.process(command_list)
    assert len(command_list) == 0
    assert steps_non_looping.is_finished == False

    command_list = []
    steps_non_looping_no_delay.process(command_list)
    assert len(command_list) == 1
    if len(command_list) > 0:
        assert command_list[0] == down_command
    assert steps_non_looping_no_delay.is_finished == True

    # A third millisecond completes the second step.
    timer.set_current_time_ms(3)

    command_list = []
    no_steps.process(command_list)
    assert len(command_list) == 0
    assert no_steps.is_finished == False

    command_list = []
    no_steps_non_looping.process(command_list)
    assert len(command_list) == 0
    assert no_steps_non_looping.is_finished == True

    command_list = []
    steps.process(command_list)
    assert len(command_list) == 1
    if len(command_list) > 0:
        assert command_list[0] == down_command
    assert steps.is_finished == False

    command_list = []
    steps_non_looping.process(command_list)
    assert len(command_list) == 1
    if len(command_list) > 0:
        assert command_list[0] == down_command
    assert steps_non_looping.is_finished == True

    command_list = []
    steps_non_looping_no_delay.process(command_list)
    assert len(command_list) == 0
    assert steps_non_looping_no_delay.is_finished == True

    # Advancing time further should only produce effects from the looping
    # routine with steps.
    timer.set_current_time_ms(4)

    command_list = []
    no_steps.process(command_list)
    assert len(command_list) == 0
    assert no_steps.is_finished == False

    command_list = []
    no_steps_non_looping.process(command_list)
    assert len(command_list) == 0
    assert no_steps_non_looping.is_finished == True

    command_list = []
    steps.process(command_list)
    assert len(command_list) == 1
    if len(command_list) > 0:
        assert command_list[0] == up_command
    assert steps.is_finished == False

    command_list = []
    steps_non_looping.process(command_list)
    assert len(command_list) == 0
    assert steps_non_looping.is_finished == True

    command_list = []
    steps_non_looping_no_delay.process(command_list)
    assert len(command_list) == 0
    assert steps_non_looping_no_delay.is_finished == True

    timer.set_current_time_ms(6)

    command_list = []
    no_steps.process(command_list)
    assert len(command_list) == 0
    assert no_steps.is_finished == False

    command_list = []
    no_steps_non_looping.process(command_list)
    assert len(command_list) == 0
    assert no_steps_non_looping.is_finished == True

    command_list = []
    steps.process(command_list)
    assert len(command_list) == 1
    if len(command_list) > 0:
        assert command_list[0] == down_command
    assert steps.is_finished == False

    command_list = []
    steps_non_looping.process(command_list)
    assert len(command_list) == 0
    assert steps_non_looping.is_finished == True

    command_list = []
    steps_non_looping_no_delay.process(command_list)
    assert len(command_list) == 0
    assert steps_non_looping_no_delay.is_finished == True


def test_routine_manager() -> None:
    """Test the routine manager."""
    timer = test_time_util.TestTimer()

    manager = routines.RoutineManager(timer)
    assert manager.num_loaded == 0
    assert manager.num_running == 0

    num_valid_routines = 3
    manager.initialize("tests/data/routines/manager_valid/")
    assert manager.num_loaded == num_valid_routines
    assert manager.num_running == 0

    # Initializing again doesn't double up.
    manager.initialize("tests/data/routines/manager_valid/")
    assert manager.num_loaded == num_valid_routines
    assert manager.num_running == 0

    manager.uninitialize()
    assert manager.num_loaded == 0
    assert manager.num_running == 0

    manager.initialize("tests/data/routines/manager_duplicate/")
    assert manager.num_loaded == 2
    assert manager.num_running == 0

    manager.uninitialize()
    assert manager.num_loaded == 0
    assert manager.num_running == 0

    manager.initialize("tests/data/routines/manager_invalid/")
    assert manager.num_loaded == 1
    assert manager.num_running == 0

    manager.uninitialize()
    assert manager.num_loaded == 0
    assert manager.num_running == 0

    # Now that we have tested various loading situations, test running
    # routines.
    manager.initialize("tests/data/routines/manager_valid/")
    assert manager.num_loaded == num_valid_routines
    assert manager.num_running == 0

    # Can't start a routine that there isn't a description for.
    start_command = commands.RoutineCommand(
        "chicken", commands.RoutineCommand.Action.START
    )
    notification = manager.process_command(start_command)
    assert notification == "There is no chicken routine."
    assert manager.num_loaded == num_valid_routines
    assert manager.num_running == 0

    # Can't stop a routine that isn't running.
    stop_command = commands.RoutineCommand(
        "wake", commands.RoutineCommand.Action.STOP
    )
    notification = manager.process_command(stop_command)
    assert notification == "The wake routine is not running."
    assert manager.num_loaded == num_valid_routines
    assert manager.num_running == 0

    # Can't start the routine when it's already running.
    start_command = commands.RoutineCommand(
        "wake", commands.RoutineCommand.Action.START
    )
    notification = manager.process_command(start_command)
    assert notification == "Started the wake routine."
    assert manager.num_loaded == num_valid_routines
    assert manager.num_running == 1

    notification = manager.process_command(start_command)
    assert notification == "The wake routine is already running."
    assert manager.num_loaded == num_valid_routines
    assert manager.num_running == 1

    stop_command = commands.RoutineCommand(
        "sleep", commands.RoutineCommand.Action.STOP
    )
    notification = manager.process_command(stop_command)
    assert notification == "The sleep routine is not running."
    assert manager.num_loaded == num_valid_routines
    assert manager.num_running == 1

    # Actually stop the routine.
    stop_command = commands.RoutineCommand(
        "wake", commands.RoutineCommand.Action.STOP
    )
    notification = manager.process_command(stop_command)
    assert notification == "Stopped the wake routine."
    assert manager.num_loaded == num_valid_routines
    assert manager.num_running == 0

    # Processing does nothing with no routines running.
    command_list = []
    notification_list = []
    manager.process_routines(command_list, notification_list)
    assert manager.num_loaded == num_valid_routines
    assert manager.num_running == 0
    assert len(command_list) == 0
    assert len(notification_list) == 0

    # Start some routines.
    start_command = commands.RoutineCommand(
        "wake", commands.RoutineCommand.Action.START
    )
    notification = manager.process_command(start_command)
    assert notification == "Started the wake routine."
    assert manager.num_loaded == num_valid_routines
    assert manager.num_running == 1

    start_command = commands.RoutineCommand(
        "sleep", commands.RoutineCommand.Action.START
    )
    notification = manager.process_command(start_command)
    assert notification == "Started the sleep routine."
    assert manager.num_loaded == num_valid_routines
    assert manager.num_running == 2

    # Processing without time advancement does nothing.
    command_list = []
    notification_list = []
    manager.process_routines(command_list, notification_list)
    assert manager.num_loaded == num_valid_routines
    assert manager.num_running == 2
    assert len(command_list) == 0
    assert len(notification_list) == 0

    # We should start to see some commands after advancing the time.
    timer.set_current_time_ms(1)
    command_list = []
    notification_list = []
    manager.process_routines(command_list, notification_list)
    assert manager.num_loaded == num_valid_routines
    assert manager.num_running == 2
    assert len(command_list) == 2
    assert len(notification_list) == 0

    expected_command = commands.MoveControlCommand(
        "back", commands.MoveControlCommand.Direction.UP, "routine"
    )
    assert expected_command in command_list
    expected_command = commands.MoveControlCommand(
        "back", commands.MoveControlCommand.Direction.DOWN, "routine"
    )
    assert expected_command in command_list

    # Processing again does nothing.
    command_list = []
    notification_list = []
    manager.process_routines(command_list, notification_list)
    assert manager.num_loaded == num_valid_routines
    assert manager.num_running == 2
    assert len(command_list) == 0
    assert len(notification_list) == 0

    # Processing after starting a routine with a zero initial delay should see
    # a command without time advancement.
    start_command = commands.RoutineCommand(
        "sit", commands.RoutineCommand.Action.START
    )
    notification = manager.process_command(start_command)
    assert notification == "Started the sit routine."
    assert manager.num_loaded == num_valid_routines
    assert manager.num_running == 3

    command_list = []
    notification_list = []
    manager.process_routines(command_list, notification_list)
    assert manager.num_loaded == num_valid_routines
    assert manager.num_running == 3
    assert len(command_list) == 1
    assert len(notification_list) == 0

    expected_command = commands.MoveControlCommand(
        "legs", commands.MoveControlCommand.Direction.DOWN, "routine"
    )
    assert expected_command in command_list

    # Advancing further does nothing.
    timer.set_current_time_ms(2)
    command_list = []
    notification_list = []
    manager.process_routines(command_list, notification_list)
    assert manager.num_loaded == num_valid_routines
    assert manager.num_running == 3
    assert len(command_list) == 0
    assert len(notification_list) == 0

    # We should see more commands after advancing the time.
    timer.set_current_time_ms(3)
    command_list = []
    notification_list = []
    manager.process_routines(command_list, notification_list)
    assert manager.num_loaded == num_valid_routines
    assert manager.num_running == 2
    assert len(command_list) == 3
    assert len(notification_list) == 1

    expected_command = commands.MoveControlCommand(
        "legs", commands.MoveControlCommand.Direction.UP, "routine"
    )
    assert expected_command in command_list
    expected_command = commands.MoveControlCommand(
        "legs", commands.MoveControlCommand.Direction.DOWN, "routine"
    )
    assert expected_command in command_list
    expected_command = commands.MoveControlCommand(
        "back", commands.MoveControlCommand.Direction.UP, "routine"
    )
    assert expected_command in command_list

    assert "The sit routine finished." in notification_list

    # With looping routines, continuing to advance should produce the same
    # results.
    timer.set_current_time_ms(4)
    command_list = []
    notification_list = []
    manager.process_routines(command_list, notification_list)
    assert manager.num_loaded == num_valid_routines
    assert manager.num_running == 2
    assert len(command_list) == 2
    assert len(notification_list) == 0

    expected_command = commands.MoveControlCommand(
        "back", commands.MoveControlCommand.Direction.UP, "routine"
    )
    assert expected_command in command_list
    expected_command = commands.MoveControlCommand(
        "back", commands.MoveControlCommand.Direction.DOWN, "routine"
    )
    assert expected_command in command_list

    # Advancing further does nothing.
    timer.set_current_time_ms(5)
    command_list = []
    notification_list = []
    manager.process_routines(command_list, notification_list)
    assert manager.num_loaded == num_valid_routines
    assert manager.num_running == 2
    assert len(command_list) == 0
    assert len(notification_list) == 0

    # We should see more commands after advancing the time.
    timer.set_current_time_ms(6)
    command_list = []
    notification_list = []
    manager.process_routines(command_list, notification_list)
    assert manager.num_loaded == num_valid_routines
    assert manager.num_running == 2
    assert len(command_list) == 2
    assert len(notification_list) == 0

    expected_command = commands.MoveControlCommand(
        "legs", commands.MoveControlCommand.Direction.UP, "routine"
    )
    assert expected_command in command_list
    expected_command = commands.MoveControlCommand(
        "legs", commands.MoveControlCommand.Direction.DOWN, "routine"
    )
    assert expected_command in command_list


def test_routine_bootstrap(tmp_path: pathlib.Path) -> None:
    """Test routine bootstrapping."""
    routines_path = tmp_path / "routines/"
    assert routines_path.exists() == False

    routines.bootstrap_routines(str(tmp_path) + "/")
    assert routines_path.exists() == True

    original_desc = routines.RoutineDesc.parse_from_file(
        "tests/data/routines/routine_test_valid_steps.rtn"
    )
    assert original_desc.is_valid() == True

    # Bootstrap should not overwrite existing routine descriptions.
    filename = routines_path / "test_valid.rtn"
    assert filename.exists() == False

    original_desc.save_to_file(str(filename))
    assert filename.exists() == True

    routines.bootstrap_routines(str(tmp_path) + "/")
    assert routines_path.exists() == True

    written_desc = routines.RoutineDesc.parse_from_file(str(filename))
    assert written_desc.is_valid() == True
    assert written_desc == original_desc
