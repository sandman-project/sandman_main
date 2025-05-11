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
        pass
