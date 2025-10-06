"""Everything needed to support reports.

Reports are automatically generated based on activity.
"""

import logging
import pathlib
import typing

from . import time_util

_logger = logging.getLogger("sandman.report")


class ReportManager:
    """Manages recording events into per day report files."""

    def __init__(
        self, time_source: time_util.TimeSource, base_dir: str
    ) -> None:
        """Initialize the instance."""
        self.__time_source = time_source
        self.__reports_dir = base_dir + "reports/"
        # Eventually this should be configurable.
        self.__report_start_hour = 17
        self.__report_name = self._get_desired_report_name()
        self.__report_file: None | typing.TextIO = None

    def process(self) -> None:
        """Process reports."""
        pass

    def _get_desired_report_name(self) -> str:
        """Get the desired report name based on current date and time."""
        report_time = self.__time_source.get_current_time()

        if report_time.hour < self.__report_start_hour:
            report_time.add(days=-1)

        return (
            f"sandman{report_time.year}-{report_time.month:02}-"
            + f"{report_time.day:02}"
        )


def bootstrap_reports(base_dir: str) -> None:
    """Handle bootstrapping for reports."""
    report_path = pathlib.Path(base_dir + "reports/")

    if report_path.exists() == True:
        return

    _logger.info("Creating missing report directory '%s'.", str(report_path))

    try:
        report_path.mkdir()

    except Exception:
        _logger.warning(
            "Failed to create report directory '%s'.", str(report_path)
        )
        return
