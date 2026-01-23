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
) -> None | StatusCommand | MoveControlCommand | RoutineCommand:
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

    match intent_name:
        case "GetStatus":
            _logger.info("Recognized a get status intent.")
            return StatusCommand()

        case "MovePart":
            _logger.info("Attempting to recognize a move control intent.")
            return _parse_from_move_control_intent(intent_json)

        case "ControlRoutine":
            _logger.info("Attempting to recognize a control routine intent.")
            return _parse_from_control_routine_intent(intent_json)

    _logger.warning("Unrecognized intent '%s'.", intent_name)
    return None


@dataclasses.dataclass
class _IntentSlot:
    """A slot from an intent."""

    name: str
    value: str


def _parse_slots_from_intent(
    intent_json: dict[str, typing.Any],
) -> list[_IntentSlot]:
    """Parse slots from intent JSON."""
    slots: list[_IntentSlot] = []

    try:
        slots_json = intent_json["slots"]

    except KeyError:
        _logger.warning("Invalid intent: missing slots.")
        return slots

    if isinstance(slots_json, list) == False:
        _logger.warning("Invalid intent: slots is not a list.")
        return slots

    # Try to extract each slot.
    for slot in slots_json:
        # Each slot must have a name and a value.
        try:
            slot_name = slot["slotName"]

        except KeyError:
            _logger.warning("Intent slot is missing a name.")
            continue

        if type(slot_name) is not str:
            _logger.warning(
                "Intent slot name '%s' is not a string.", str(slot_name)
            )
            continue

        try:
            slot_value = slot["rawValue"]

        except KeyError:
            _logger.warning("Intent slot '%s' is missing a value.", slot_name)
            continue

        if type(slot_value) is not str:
            _logger.warning(
                "Intent slot value '%s' is not a string.", str(slot_value)
            )
            continue

        slots.append(_IntentSlot(slot_name, slot_value))

    return slots


def _parse_from_move_control_intent(
    intent_json: dict[str, typing.Any],
) -> None | MoveControlCommand:
    """Parse a move control intent from JSON."""
    slots = _parse_slots_from_intent(intent_json)

    if len(slots) == 0:
        _logger.warning("Invalid move control intent: missing slots.")
        return None

    # Try to find the control name and direction in the slots.
    control_name: str | None = None
    direction: MoveControlCommand.Direction | None = None

    for slot in slots:
        if slot.name == "name":
            control_name = slot.value

        elif slot.name == "direction":
            if slot.value == "raise":
                direction = MoveControlCommand.Direction.UP

            elif slot.value == "lower":
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


def _parse_from_control_routine_intent(
    intent_json: dict[str, typing.Any],
) -> None | RoutineCommand:
    """Parse a control routine intent from JSON."""
    slots = _parse_slots_from_intent(intent_json)

    if len(slots) == 0:
        _logger.warning("Invalid control routine intent: missing slots.")
        return None

    # Try to find the routine name and action in the slots.
    routine_name: str | None = None
    action: RoutineCommand.Action | None = None

    for slot in slots:
        if slot.name == "name":
            routine_name = slot.value

        elif slot.name == "action":
            if slot.value == "start":
                action = RoutineCommand.Action.START

            elif slot.value == "stop":
                action = RoutineCommand.Action.STOP

    if routine_name is None:
        _logger.warning(
            "Invalid control routine intent: missing routine name."
        )
        return None

    if action is None:
        _logger.warning("Invalid routine control intent: missing action.")
        return None

    _logger.info(
        "Recognized a control routine intent: '%s' routine '%s'.",
        action.as_string(),
        routine_name,
    )
    return RoutineCommand(routine_name, action)
