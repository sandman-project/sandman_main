"""Encapsulates timing behavior."""

import time


class Timer:
    """An interface to measure differences in time."""

    def __init__(self) -> None:
        """Initialize the instance."""
        pass

    def get_current_time(self) -> int:
        """Get the current point in time."""
        return time.perf_counter_ns()

    def get_time_since_ms(self, other_time: int) -> int:
        """Get the time in milliseconds since another point in time."""
        current_time_ns = self.get_current_time()
        return (current_time_ns - other_time) // 1000000
