"""Tests time utilities."""

import typing

import whenever

import sandman_main.time_util as time_util

_default_time = whenever.ZonedDateTime(
    year=2025, month=9, day=23, hour=21, minute=42, tz="America/Chicago"
)


class TestTimeSource(time_util.TimeSource):
    """A special-purpose time source for use with testing."""

    # Despite its name, this class should not be collected for testing.
    __test__ = False

    @typing.override
    def __init__(self) -> None:
        """Initialize the instance."""
        super().__init__()
        self.__time_zone_name = _default_time.tz
        self.__curr_time = _default_time.to_instant()

    @typing.override
    def get_current_time_zone_name(self) -> str:
        """Get the name of the current time zone."""
        return self.__time_zone_name

    @typing.override
    def get_current_time(self) -> whenever.ZonedDateTime:
        """Get the current time in the current time zone."""
        return self.__curr_time.to_tz(self.get_current_time_zone_name())

    def set_current_time(self, new_time: whenever.ZonedDateTime) -> None:
        """Set the current time and time zone."""
        self.__time_zone_name = new_time.tz
        self.__curr_time = new_time.to_instant()


def test_time_source() -> None:
    """Test the test time source."""
    time_source = TestTimeSource()
    assert time_source.get_current_time_zone_name() == _default_time.tz
    assert time_source.get_current_time() == _default_time

    new_time = whenever.ZonedDateTime(
        year=2025, month=9, day=25, hour=21, minute=51, tz="America/New_York"
    )

    assert time_source.get_current_time_zone_name() != new_time.tz
    assert time_source.get_current_time() != new_time
    time_source.set_current_time(new_time)
    assert time_source.get_current_time_zone_name() == new_time.tz
    assert time_source.get_current_time() == new_time
