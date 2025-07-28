"""Provides configuration for controls."""


class ControlConfig:
    """Specifies the configuration of a control."""

    def __init__(self) -> None:
        """Initialize the control config."""
        self.__name: str = ""

    @property
    def name(self) -> str:
        """Get the name."""
        return self.__name
