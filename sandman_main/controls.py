"""Everything needed to manage controls.

Controls are used to manipulate parts of the bed.
"""

import enum
import logging


class ControlState(enum.Enum):
    """The various states a control can be in."""

    IDLE = 0


class Control:
    """The state and logic for a control that manages a part of the bed."""

    def __init__(self, name: str) -> None:
        """Initialize the instance."""
        self.__logger = logging.getLogger("sandman.control." + name)
        self.__state = ControlState.IDLE
        self.__name = name

    def get_state(self) -> ControlState:
        """Get the current state."""
        return self.__state
