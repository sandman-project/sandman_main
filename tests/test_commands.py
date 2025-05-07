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
