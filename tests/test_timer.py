"""A timer for use during testing."""

import sandman_main.timer as timer


class TestTimer(timer.Timer):
    """A special-purpose timer for use with testing."""

    # Despite its name, this class should not be collected for testing.
    __test__ = False

    def __init__(self) -> None:
        """Initialize the instance."""
        super().__init__()
        self.__curr_time_ns = 0

    def get_current_time(self) -> int:
        """Get the current point in time."""
        return self.__curr_time_ns

    def set_current_time_ms(self, curr_time_ms: int) -> None:
        """Set the current point in time in milliseconds."""
        self.__curr_time_ns = curr_time_ms * 1000


def test_timer() -> None:
    """Test the test timer."""
    test_timer = TestTimer()
    assert test_timer.get_current_time() == 0

    # The time since initialization should be zero.
    initial_time = test_timer.get_current_time()
    duration_ms = test_timer.get_time_since_ms(initial_time)
    assert duration_ms == 0

    test_timer.set_current_time_ms(15)
