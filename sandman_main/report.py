"""Everything needed to support reports.

Reports are automatically generated based on activity.
"""

import dataclasses
import json
import logging
import pathlib
import typing

import whenever

from . import time_util

_logger = logging.getLogger("sandman.report")


@dataclasses.dataclass
class _ReportEvent:
    """An event for a report file."""

    when: whenever.ZonedDateTime
    info: typing.Any


class ReportManager:
    """Manages recording events into per day report files."""

    REPORT_VERSION = 4

    def __init__(
        self, time_source: time_util.TimeSource, base_dir: str
    ) -> None:
        """Initialize the instance."""
        self.__time_source = time_source
        self.__reports_dir = base_dir + "reports/"
        # Eventually this should be configurable.
        self.__report_start_hour = 17

    def process(self) -> None:
        """Process reports."""
        self.__maybe_create_report_file()

    def add_status_event(self) -> None:
        """Add a status event at the current time."""
        info = {"type": "status"}
        self.__add_event(info)

    def __get_start_time_from_time(
        self, time: whenever.ZonedDateTime
    ) -> whenever.ZonedDateTime:
        """Get the appropriate start time based on the given time."""
        start_time = time

        if start_time.hour < self.__report_start_hour:
            start_time = start_time.add(days=-1)

        start_time = start_time.replace_time(
            whenever.Time(self.__report_start_hour)
        )
        return start_time

    def __get_desired_report_name(self) -> str:
        """Get the desired report name based on current date and time."""
        curr_time = self.__time_source.get_current_time()
        start_time = self.__get_start_time_from_time(curr_time)

        return (
            f"sandman{start_time.year}-{start_time.month:02}-"
            + f"{start_time.day:02}"
        )

    def __maybe_create_report_file(self) -> None:
        """Create the desired report if it doesn't exist."""
        report_name = self.__get_desired_report_name()
        report_file_name = self.__reports_dir + report_name + ".rpt"

        report_path = pathlib.Path(report_file_name)

        if report_path.exists():
            return

        # Get the start time string for the header.
        curr_time = self.__time_source.get_current_time()
        start_time = self.__get_start_time_from_time(curr_time)
        start_time_string = start_time.format_common_iso()

        header = {
            "version": self.REPORT_VERSION,
            "start": start_time_string,
        }

        # Add the header.
        with open(report_file_name, "w", encoding="utf-8") as file:
            header_line = json.dumps(header) + "\n"
            file.write(header_line)

    def __add_event(self, info: typing.Any) -> None:
        """Add an event with the given info at the current time."""
        pass


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
