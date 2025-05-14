"""Everything needed to manage controls.

Controls are used to manipulate parts of the bed.
"""

import enum
import logging


@enum.unique
class ControlState(enum.Enum):
    """The various states a control can be in."""

    IDLE = 0
    MOVE_UP = 1
    MOVE_DOWN = 2
    COOL_DOWN = 3


_state_names = [
    "idle",  # IDLE
    "move up",  # MOVE_UP
    "move down",  # MOVE_DOWN
    "cool down",  # COOL_DOWN
]


class Control:
    """The state and logic for a control that manages a part of the bed."""

    def __init__(self, name: str) -> None:
        """Initialize the instance."""
        self.__logger = logging.getLogger("sandman.control." + name)
        self.__state = ControlState.IDLE
        self.__desired_state = ControlState.IDLE
        self.__name = name

    def get_state(self) -> ControlState:
        """Get the current state."""
        return self.__state

    def set_desired_state(self, state: ControlState) -> None:
        """Set the next state."""
        if state == ControlState.COOL_DOWN:
            return

        self.__desired_state = state

        self.__logger.info(
            "Set desired state to '%s'.", _state_names[state.value]
        )

    def process(self) -> None:
        """Process the control."""
        if self.__state == ControlState.IDLE:
            self.__process_idle_state()
            return

        self.__logger.warning(
            "Unhandled state '%s'.", _state_names[self.__state.value]
        )

    def __set_state(self, state: ControlState) -> None:
        """Trigger a state transition."""
        self.__logger.info(
            "State transition from '%s' to '%s'.",
            _state_names[self.__state.value],
            _state_names[state.value],
        )

        self.__state = state

    def __process_idle_state(self) -> None:
        """Process the idle state."""
        if self.__desired_state == ControlState.IDLE:
            return

        # Only transitions to moving up or down are allowed.
        if (self.__desired_state != ControlState.MOVE_UP) and (
            self.__desired_state != ControlState.MOVE_DOWN
        ):
            self.__desired_state = ControlState.IDLE
            return

        self.__set_state(self.__desired_state)
