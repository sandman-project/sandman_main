"""All of the commands that can be processed."""

import dataclasses
import enum
import logging
import typing


class StatusCommand:
    """A command to get the status."""

    pass


@dataclasses.dataclass
class MoveControlCommand:
    """A command to move a control."""

    @enum.unique
    class Direction(enum.Enum):
        """Value indicating a direction in which the control can move."""

        UP = enum.auto()
        DOWN = enum.auto()

        def as_string(self) -> str:
            """Return a readable phrase describing the direction."""
            match self:
                case MoveControlCommand.Direction.UP:
                    return "up"
                case MoveControlCommand.Direction.DOWN:
                    return "down"
                case _:
                    typing.assert_never(self)

    control_name: str
    direction: Direction
    source: str


@dataclasses.dataclass
class RoutineCommand:
    """A command to do something with a routine."""

    @enum.unique
    class Action(enum.Enum):
        """Value indicating an action to perform with a routine."""

        START = enum.auto()
        STOP = enum.auto()

        def as_string(self) -> str:
            """Return a readable phrase describing the action."""
            match self:
                case RoutineCommand.Action.START:
                    return "start"

                case RoutineCommand.Action.STOP:
                    return "stop"

                case _:
                    typing.assert_never(self)

    routine_name: str
    action: Action


_logger = logging.getLogger("sandman.commands")


def parse_from_intent(
    intent_json: dict[str, typing.Any],
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
    intent_json: dict[str, typing.Any],
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
    control_name: str | None = None
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
                control_name = slot_value

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
        direction.as_string(),
    )
    return MoveControlCommand(control_name, direction, "voice")
