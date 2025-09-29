"""Everything needed to support reports.

Reports are automatically generated based on activity.
"""

import logging
import pathlib

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
