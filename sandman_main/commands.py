"""All of the commands that can be processed."""

from collections.abc import Mapping
import dataclasses
import enum
import logging
from typing import Any
from controls import Control

class StatusCommand:
    """A command to get the status."""

    pass


@dataclasses.dataclass
class MoveControlCommand:
    """A command to move a control."""

    @enum.unique
    class Direction(enum.Enum):
        UP = enum.auto()
        DOWN = enum.auto()

    control_name: Control.Name
    direction: Direction


_logger = logging.getLogger("sandman.commands")


def parse_from_intent(
    intent_json: Mapping[str, Any],
) -> None | StatusCommand | MoveControlCommand:
    """Parse an intent from JSON.

    Return a command if one is recognized.
    """
    # Try to get the intent name.
    try:
        intent = intent_json["intent"]

    except KeyError:
        _logger.warning("Invalid intent.")
        return None

    try:
        intent_name = intent["intentName"]

    except KeyError:
        _logger.warning("Invalid intent: missing name.")
        return None

    if intent_name == "GetStatus":
        _logger.info("Recognized a get status intent.")
        return StatusCommand()

    elif intent_name == "MovePart":
        _logger.info("Attempting to recognize a move control intent.")
        return _parse_from_move_control_intent(intent_json)

    _logger.warning("Unrecognized intent '%s'.", intent_name)
    return None


def _parse_from_move_control_intent(
    intent_json: Mapping[str, Any],
) -> None | MoveControlCommand:
    """Parse a move control intent from JSON."""
    try:
        slots = intent_json["slots"]

    except KeyError:
        _logger.warning("Invalid move control intent: missing slots.")
        return None

    if isinstance(slots, list) == False:
        _logger.warning("Invalid move control intent: slots is not a list.")
        return None

    # Try to find the control name and direction in the slots.
    control_name: Control.Name | None = None
    direction: MoveControlCommand.Direction | None = None

    for slot in slots:
        # Each slot must have a name and a value.
        try:
            slot_name = slot["slotName"]

        except KeyError:
            continue

        try:
            slot_value = slot["rawValue"]

        except KeyError:
            continue

        if slot_name == "name":
            if type(slot_value) is str:
                # TODO: Handle the error if the slot value is not a valid control name.
                control_name = Control.Name(slot_value)

        elif slot_name == "direction":
            if slot_value == "raise":
                direction = MoveControlCommand.Direction.UP

            elif slot_value == "lower":
                direction = MoveControlCommand.Direction.DOWN

    if control_name is None:
        _logger.warning("Invalid move control intent: missing control name.")
        return None

    if direction is None:
        _logger.warning("Invalid move control intent: missing direction.")
        return None

    _logger.info(
        "Recognized a move control intent: move '%s' '%s'.",
        control_name,
        direction,
    )
    return MoveControlCommand(control_name, direction)
