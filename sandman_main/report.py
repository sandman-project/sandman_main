"""Everything needed to support reports.

Reports are automatically generated based on activity.
"""

import collections
import dataclasses
import json
import logging
import pathlib
import typing

import whenever

from . import time_util

_logger = logging.getLogger("sandman.report")


type _ReportEventInfo = typing.Mapping[
    str, typing.Mapping[str, int | str] | int | str
]


@dataclasses.dataclass
class _ReportEvent:
    """An event for a report file."""

    when: whenever.ZonedDateTime
    info: _ReportEventInfo


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
        self.__pending_events = collections.deque[_ReportEvent]()

    def process(self) -> None:
        """Process reports."""
        # Even if there are no events, we want to make sure that we are
        # creating empty report files.
        self.__maybe_create_report_file(self.__time_source.get_current_time())

        event = self.__pop_event()

        while event is not None:
            self.__write_event(event)

            event = self.__pop_event()

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

    def __get_report_name_from_time(self, time: whenever.ZonedDateTime) -> str:
        """Get the report name based on given time."""
        start_time = self.__get_start_time_from_time(time)

        return (
            f"sandman{start_time.year}-{start_time.month:02}-"
            + f"{start_time.day:02}"
        )

    def __maybe_create_report_file(self, time: whenever.ZonedDateTime) -> None:
        """Create the desired report if it doesn't exist."""
        report_name = self.__get_report_name_from_time(time)
        report_file_name = self.__reports_dir + report_name + ".rpt"

        report_path = pathlib.Path(report_file_name)

        if report_path.exists():
            return

        # Get the start time string for the header.
        start_time = self.__get_start_time_from_time(time)
        start_time_string = start_time.format_common_iso()

        header = {
            "version": self.REPORT_VERSION,
            "start": start_time_string,
        }
        header_line = json.dumps(header) + "\n"

        # Add the header.
        with open(report_file_name, "w", encoding="utf-8") as file:
            file.write(header_line)

        _logger.info("Created report file '%s'.", str(report_file_name))

    def __add_event(self, info: _ReportEventInfo) -> None:
        """Add an event with the given info at the current time."""
        event = _ReportEvent(self.__time_source.get_current_time(), info)
        self.__pending_events.append(event)

    def __pop_event(self) -> _ReportEvent | None:
        """Pop an event from the queue if there is one.

        Returns the event or None if the queue is empty.
        """
        try:
            event = self.__pending_events.popleft()

        except IndexError:
            return None

        return event

    def __write_event(self, event: _ReportEvent) -> None:
        """Write the event to the appropriate file."""
        self.__maybe_create_report_file(event.when)

        report_name = self.__get_report_name_from_time(event.when)
        report_file_name = self.__reports_dir + report_name + ".rpt"

        report_path = pathlib.Path(report_file_name)

        if report_path.exists() == False:
            _logger.error(
                "Failed to add event to '%s' - file doesn't exist.",
                report_file_name,
            )
            return

        event_json = {
            "when": event.when.format_common_iso(),
            "info": event.info,
        }
        event_line = json.dumps(event_json) + "\n"

        with open(report_file_name, "a", encoding="utf-8") as file:
            file.write(event_line)


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
