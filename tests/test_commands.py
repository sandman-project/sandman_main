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
    assert (
        commands.parse_from_intent({"intent": {"intentName": "MovePart"}})
        is None
    )

    # Which is expected to be a list.
    assert (
        commands.parse_from_intent(
            {"intent": {"intentName": "MovePart"}, "slots": None}
        )
        is None
    )

    # Which must contain at least two objects with slotName and rawValue keys.
    # One slot name must be name and another must be direction.
    assert (
        commands.parse_from_intent(
            {"intent": {"intentName": "MovePart"}, "slots": None}
        )
        is None
    )

    assert (
        commands.parse_from_intent(
            {
                "intent": {"intentName": "MovePart"},
                "slots": [{"rawValue": 1}, {"slotName": 1}],
            }
        )
        is None
    )

    # The raw value of the name slot must be a string and the direction slot
    # must be either raise or lower.
    assert (
        commands.parse_from_intent(
            {
                "intent": {"intentName": "MovePart"},
                "slots": [
                    {"slotName": "direction", "rawValue": "chicken"},
                    {"slotName": "name", "rawValue": -1},
                ],
            }
        )
        is None
    )
    assert (
        commands.parse_from_intent(
            {
                "intent": {"intentName": "MovePart"},
                "slots": [
                    {"slotName": "direction", "rawValue": "chicken"},
                    {"slotName": "name", "rawValue": "legs"},
                ],
            }
        )
        is None
    )

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
    assert command.control_name == "legs"
    assert command.direction == "up"

    command = commands.parse_from_intent(
        {
            "intent": {"intentName": "MovePart"},
            "slots": [
                {"slotName": "direction", "rawValue": "lower"},
                {"slotName": "name", "rawValue": "legs"},
            ],
        }
    )
    assert command.control_name == "legs"
    assert command.direction == "down"
