"""All of the commands that can be processed."""

import dataclasses


class StatusCommand:
    """A command to get the status."""

    pass


@dataclasses.dataclass
class MoveControlCommand:
    """A command to move a control."""

    control_name: str
    direction: str
