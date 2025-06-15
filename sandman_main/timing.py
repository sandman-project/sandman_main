"""Encapsulates timing behavior."""

import time


class Timer:
    """An interface to measure differences in time."""

    def __init__(self) -> None:
        """Initialize the instance."""
        pass

    def get_current_time_ns(self) -> int:
        """Get the current point in time in nanoseconds."""
        return time.perf_counter_ns()

    def get_time_since_ms(self, other_time_ns: int) -> int:
        """Get the time in milliseconds since another point in time.

        `other_time_ns` is in nanoseconds.
        """
        current_time_ns = self.get_current_time_ns()
        return (current_time_ns - other_time_ns) // 1000000
