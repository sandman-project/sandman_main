"""Everything needed to support routines.

Routines are user specified sequences of actions.
"""

import logging
import pathlib

_logger = logging.getLogger("sandman.routines")


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
