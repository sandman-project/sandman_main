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

    # Which must contain at least two objects with slotName and value keys.
    # The value object must also have a value key, which is the actual value.
    # One slot name must be name and another must be direction.
    command = commands.parse_from_intent(
        {
            "intent": {"intentName": "MovePart"},
            "slots": [{"value": 1}],
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
            "slots": [{"slotName": "direction"}],
        }
    )
    assert command is None

    # The value must be an object with a value key.
    command = commands.parse_from_intent(
        {
            "intent": {"intentName": "MovePart"},
            "slots": [
                {"slotName": "direction", "value": "chicken"},
                {"slotName": "name", "value": {"tender": 1}},
            ],
        }
    )
    assert command is None

    # The value of the name slot must be a string and the direction slot
    # must be either up or down.
    command = commands.parse_from_intent(
        {
            "intent": {"intentName": "MovePart"},
            "slots": [
                {"slotName": "direction", "value": {"value": "chicken"}},
                {"slotName": "name", "value": {"value": -1}},
            ],
        }
    )
    assert command is None

    command = commands.parse_from_intent(
        {
            "intent": {"intentName": "MovePart"},
            "slots": [
                {"slotName": "direction", "value": {"value": "chicken"}},
                {"slotName": "name", "value": {"value": "legs"}},
            ],
        }
    )
    assert command is None

    # Okay, now let's check some valid ones.
    command = commands.parse_from_intent(
        {
            "intent": {"intentName": "MovePart"},
            "slots": [
                {"slotName": "direction", "value": {"value": "up"}},
                {"slotName": "name", "value": {"value": "legs"}},
            ],
        }
    )
    assert isinstance(command, commands.ControlCommand)
    assert command.control_name == "legs"
    assert command.action == commands.ControlCommand.Action.MOVE_UP
    assert command.source == "voice"

    command = commands.parse_from_intent(
        {
            "intent": {"intentName": "MovePart"},
            "slots": [
                {"slotName": "direction", "value": {"value": "down"}},
                {"slotName": "name", "value": {"value": "legs"}},
            ],
        }
    )
    assert isinstance(command, commands.ControlCommand)
    assert command.control_name == "legs"
    assert command.action == commands.ControlCommand.Action.MOVE_DOWN
    assert command.source == "voice"


def test_lock_control_intents() -> None:
    """Test lock control intent constructions."""
    # These intents must have a slots key.
    command = commands.parse_from_intent(
        {"intent": {"intentName": "LockControl"}}
    )
    assert command is None

    # Which is expected to be a list.
    command = commands.parse_from_intent(
        {"intent": {"intentName": "LockControl"}, "slots": None}
    )
    assert command is None

    # Which must contain at least two objects with slotName and value keys.
    # The value object must also have a value key, which is the actual value.
    # One slot name must be name and another must be action.
    command = commands.parse_from_intent(
        {
            "intent": {"intentName": "LockControl"},
            "slots": [{"value": 1}],
        }
    )
    assert command is None

    command = commands.parse_from_intent(
        {
            "intent": {"intentName": "LockControl"},
            "slots": [{"slotName": 1}],
        }
    )
    assert command is None

    command = commands.parse_from_intent(
        {
            "intent": {"intentName": "LockControl"},
            "slots": [{"slotName": "name"}],
        }
    )
    assert command is None

    command = commands.parse_from_intent(
        {
            "intent": {"intentName": "LockControl"},
            "slots": [{"slotName": "action"}],
        }
    )
    assert command is None

    # The value must be an object with a value key.
    command = commands.parse_from_intent(
        {
            "intent": {"intentName": "LockControl"},
            "slots": [
                {"slotName": "action", "value": "chicken"},
                {"slotName": "name", "value": {"tender": 1}},
            ],
        }
    )
    assert command is None

    # The value of the name slot must be a string and the action slot
    # must be either lock or unlock.
    command = commands.parse_from_intent(
        {
            "intent": {"intentName": "LockControl"},
            "slots": [
                {"slotName": "action", "value": {"value": "chicken"}},
                {"slotName": "name", "value": {"value": -1}},
            ],
        }
    )
    assert command is None

    command = commands.parse_from_intent(
        {
            "intent": {"intentName": "LockControl"},
            "slots": [
                {"slotName": "action", "value": {"value": "chicken"}},
                {"slotName": "name", "value": {"value": "legs"}},
            ],
        }
    )
    assert command is None

    # Okay, let's check some valid ones.
    command = commands.parse_from_intent(
        {
            "intent": {"intentName": "LockControl"},
            "slots": [
                {"slotName": "action", "value": {"value": "lock"}},
                {"slotName": "name", "value": {"value": "legs"}},
            ],
        }
    )
    assert isinstance(command, commands.ControlCommand)
    assert command.control_name == "legs"
    assert command.action == commands.ControlCommand.Action.LOCK
    assert command.source == "voice"

    command = commands.parse_from_intent(
        {
            "intent": {"intentName": "LockControl"},
            "slots": [
                {"slotName": "action", "value": {"value": "unlock"}},
                {"slotName": "name", "value": {"value": "legs"}},
            ],
        }
    )
    assert isinstance(command, commands.ControlCommand)
    assert command.control_name == "legs"
    assert command.action == commands.ControlCommand.Action.UNLOCK
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

    # Which must contain at least two objects with slotName and value keys.
    # The value object must also have a value key, which is the actual value.
    # One slot name must be name and another must be action.
    command = commands.parse_from_intent(
        {
            "intent": {"intentName": "ControlRoutine"},
            "slots": [{"value": 1}],
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

    # The value must be an object with a value key.
    command = commands.parse_from_intent(
        {
            "intent": {"intentName": "ControlRoutine"},
            "slots": [
                {"slotName": "action", "value": "chicken"},
                {"slotName": "name", "value": {"tender": 1}},
            ],
        }
    )
    assert command is None

    # The value of the name slot must be a string and the action slot
    # must be either start or stop.
    command = commands.parse_from_intent(
        {
            "intent": {"intentName": "ControlRoutine"},
            "slots": [
                {"slotName": "action", "value": {"value": "chicken"}},
                {"slotName": "name", "value": {"value": -1}},
            ],
        }
    )
    assert command is None

    command = commands.parse_from_intent(
        {
            "intent": {"intentName": "ControlRoutine"},
            "slots": [
                {"slotName": "action", "value": {"value": "chicken"}},
                {"slotName": "name", "value": {"value": "wake"}},
            ],
        }
    )
    assert command is None

    # Okay, now let's check some valid ones.
    command = commands.parse_from_intent(
        {
            "intent": {"intentName": "ControlRoutine"},
            "slots": [
                {"slotName": "action", "value": {"value": "start"}},
                {"slotName": "name", "value": {"value": "wake"}},
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
                {"slotName": "action", "value": {"value": "stop"}},
                {"slotName": "name", "value": {"value": "wake"}},
            ],
        }
    )
    assert isinstance(command, commands.RoutineCommand)
    assert command.routine_name == "wake"
    assert command.action == commands.RoutineCommand.Action.STOP
