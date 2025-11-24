"""Everything needed to support routines.

Routines are user specified sequences of actions.
"""

import logging
import pathlib

_logger = logging.getLogger("sandman.routines")


class RoutineDesc:
    """Describes a routine."""

    def __init__(self) -> None:
        """Initialize the description."""
        self.__name: str = ""

    @property
    def name(self) -> str:
        """Get the name."""
        return self.__name

    @name.setter
    def name(self, new_name: str) -> None:
        """Set the name."""
        if isinstance(new_name, str) == False:
            raise TypeError("Name must be a string.")

        if new_name == "":
            raise ValueError("Cannot set an empty name.")

        self.__name = new_name

    def is_valid(self) -> bool:
        """Check whether this is a valid routine description."""
        if self.__name == "":
            return False

        return True

    def __eq__(self, other: object) -> bool:
        """Check whether this description and another have equal values."""
        if not isinstance(other, RoutineDesc):
            return NotImplemented

        return self.__name == other.__name


def bootstrap_routines(base_dir: str) -> None:
    """Handle bootstrapping for routines."""
    routines_path = pathlib.Path(base_dir + "routines/")

    if routines_path.exists() == True:
        return

    _logger.info(
        "Creating missing routines directory '%s'.", str(routines_path)
    )

    try:
        routines_path.mkdir()

    except Exception:
        _logger.warning(
            "Failed to create routines directory '%s'.", str(routines_path)
        )
        return
