"""A timer for use during testing."""

import typing

import sandman_main.timing as timing


class TestTimer(timing.Timer):
    """A special-purpose timer for use with testing."""

    # Despite its name, this class should not be collected for testing.
    __test__ = False

    @typing.override
    def __init__(self) -> None:
        """Initialize the instance."""
        super().__init__()
        self.__current_time_ns = 0

    @typing.override
    def get_current_time_ns(self) -> int:
        """Get the current point in time."""
        return self.__current_time_ns

    def set_current_time_ms(self, curr_time_ms: int) -> None:
        """Set the current point in time in milliseconds."""
        self.__current_time_ns = curr_time_ms * 1000000


def test_timer() -> None:
    """Test the test timer."""
    test_timer = TestTimer()
    assert test_timer.get_current_time_ns() == 0

    # The time since initialization should be zero.
    initial_time = test_timer.get_current_time_ns()
    duration_ms = test_timer.get_time_since_ms(initial_time)
    assert duration_ms == 0

    # Advance the time the duration should reflect that.
    test_timer.set_current_time_ms(15)
    duration_ms = test_timer.get_time_since_ms(initial_time)
    assert duration_ms == 15

    # Advance again.
    second_time = test_timer.get_current_time_ns()
    test_timer.set_current_time_ms(16)
    duration_ms = test_timer.get_time_since_ms(initial_time)
    assert duration_ms == 16
    duration_ms = test_timer.get_time_since_ms(second_time)
    assert duration_ms == 1
