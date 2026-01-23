"""Tests commands."""

import sandman_main.commands as commands


def test_invalid_intents() -> None:
    """Test invalid intent constructions."""
    # Intents are expected to have an intent key.
    assert commands.parse_from_intent({}) is None

    # Which is expected to have an intentName key.
    assert commands.parse_from_intent({"intent": {}}) is None

    # Which should be a string.
    assert commands.parse_from_intent({"intent": {"intentName": 1}}) is None
    assert commands.parse_from_intent({"intent": {"intentName": ""}}) is None


def test_get_status_intent() -> None:
    """Test get status intent constructions."""
    command = commands.parse_from_intent(
        {"intent": {"intentName": "GetStatus"}}
    )
    assert isinstance(command, commands.StatusCommand)


def test_move_control_intents() -> None:
    """Test move control intent constructions."""
    # These intents must have a slots key.
    command = commands.parse_from_intent(
        {"intent": {"intentName": "MovePart"}}
    )
    assert command is None

    # Which is expected to be a list.
    command = commands.parse_from_intent(
        {"intent": {"intentName": "MovePart"}, "slots": None}
    )
    assert command is None

    # Which must contain at least two objects with slotName and rawValue keys.
    # One slot name must be name and another must be direction.
    command = commands.parse_from_intent(
        {
            "intent": {"intentName": "MovePart"},
            "slots": [{"rawValue": 1}],
        }
    )
    assert command is None

    command = commands.parse_from_intent(
        {
            "intent": {"intentName": "MovePart"},
            "slots": [{"slotName": 1}],
        }
    )
    assert command is None

    command = commands.parse_from_intent(
        {
            "intent": {"intentName": "MovePart"},
            "slots": [{"slotName": "name"}],
        }
    )
    assert command is None

    command = commands.parse_from_intent(
        {
            "intent": {"intentName": "MovePart"},
            "slots": [{"slotName": "name"}],
        }
    )
    assert command is None

    # The raw value of the name slot must be a string and the direction slot
    # must be either raise or lower.
    command = commands.parse_from_intent(
        {
            "intent": {"intentName": "MovePart"},
            "slots": [
                {"slotName": "direction", "rawValue": "chicken"},
                {"slotName": "name", "rawValue": -1},
            ],
        }
    )
    assert command is None

    command = commands.parse_from_intent(
        {
            "intent": {"intentName": "MovePart"},
            "slots": [
                {"slotName": "direction", "rawValue": "chicken"},
                {"slotName": "name", "rawValue": "legs"},
            ],
        }
    )
    assert command is None

    # Okay, now let's check some valid ones.
    command = commands.parse_from_intent(
        {
            "intent": {"intentName": "MovePart"},
            "slots": [
                {"slotName": "direction", "rawValue": "raise"},
                {"slotName": "name", "rawValue": "legs"},
            ],
        }
    )
    assert isinstance(command, commands.MoveControlCommand)
    assert command.control_name == "legs"
    assert command.direction == commands.MoveControlCommand.Direction.UP
    assert command.source == "voice"

    command = commands.parse_from_intent(
        {
            "intent": {"intentName": "MovePart"},
            "slots": [
                {"slotName": "direction", "rawValue": "lower"},
                {"slotName": "name", "rawValue": "legs"},
            ],
        }
    )
    assert isinstance(command, commands.MoveControlCommand)
    assert command.control_name == "legs"
    assert command.direction == commands.MoveControlCommand.Direction.DOWN
    assert command.source == "voice"


def test_control_routine_intents() -> None:
    """Test control routine intent constructions."""
    # These intents must have a slots key.
    command = commands.parse_from_intent(
        {"intent": {"intentName": "ControlRoutine"}}
    )
    assert command is None

    # Which is expected to be a list.
    command = commands.parse_from_intent(
        {"intent": {"intentName": "ControlRoutine"}, "slots": None}
    )
    assert command is None

    # Which must contain at least two objects with slotName and rawValue keys.
    # One slot name must be name and another must be action.
    command = commands.parse_from_intent(
        {
            "intent": {"intentName": "ControlRoutine"},
            "slots": [{"rawValue": 1}],
        }
    )
    assert command is None

    command = commands.parse_from_intent(
        {
            "intent": {"intentName": "ControlRoutine"},
            "slots": [{"slotName": 1}],
        }
    )
    assert command is None

    command = commands.parse_from_intent(
        {
            "intent": {"intentName": "ControlRoutine"},
            "slots": [{"slotName": "name"}],
        }
    )
    assert command is None

    command = commands.parse_from_intent(
        {
            "intent": {"intentName": "ControlRoutine"},
            "slots": [{"slotName": "name"}],
        }
    )
    assert command is None

    # The raw value of the name slot must be a string and the action slot
    # must be either start or stop.
    command = commands.parse_from_intent(
        {
            "intent": {"intentName": "ControlRoutine"},
            "slots": [
                {"slotName": "action", "rawValue": "chicken"},
                {"slotName": "name", "rawValue": -1},
            ],
        }
    )
    assert command is None

    command = commands.parse_from_intent(
        {
            "intent": {"intentName": "ControlRoutine"},
            "slots": [
                {"slotName": "action", "rawValue": "chicken"},
                {"slotName": "name", "rawValue": "wake"},
            ],
        }
    )
    assert command is None

    # Okay, now let's check some valid ones.
    command = commands.parse_from_intent(
        {
            "intent": {"intentName": "ControlRoutine"},
            "slots": [
                {"slotName": "action", "rawValue": "start"},
                {"slotName": "name", "rawValue": "wake"},
            ],
        }
    )
    assert isinstance(command, commands.RoutineCommand)
    assert command.routine_name == "wake"
    assert command.action == commands.RoutineCommand.Action.START

    command = commands.parse_from_intent(
        {
            "intent": {"intentName": "ControlRoutine"},
            "slots": [
                {"slotName": "action", "rawValue": "stop"},
                {"slotName": "name", "rawValue": "wake"},
            ],
        }
    )
    assert isinstance(command, commands.RoutineCommand)
    assert command.routine_name == "wake"
    assert command.action == commands.RoutineCommand.Action.STOP
