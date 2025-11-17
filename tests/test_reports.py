"""Tests reports."""

import json
import pathlib

import whenever

import sandman_main.controls as controls
import sandman_main.report as report
import tests.test_time_util as test_time_util


def _get_num_files_in_dir(path: pathlib.Path) -> int:
    """Get the number of files in a given directory."""
    num_files = 0

    for child in path.iterdir():
        if child.is_file():
            num_files += 1

    return num_files


def _check_file_and_read_lines(report_path: pathlib.Path) -> list[str]:
    """Check that a report file exists and read all of its lines."""
    report_exists = report_path.exists()
    assert report_exists == True

    lines = []

    if report_exists == False:
        return lines

    with open(str(report_path)) as file:
        lines = file.readlines()

    return lines


def test_report_file_creation(tmp_path: pathlib.Path) -> None:
    """Test the creation of report files."""
    reports_path = tmp_path / "reports/"
    report.bootstrap_reports(str(tmp_path) + "/")
    assert reports_path.exists() == True

    time_source = test_time_util.TestTimeSource()

    assert _get_num_files_in_dir(reports_path) == 0
    report_manager = report.ReportManager(time_source, str(tmp_path) + "/")

    # Processing should not result in any files being created, because the time
    # source doesn't have a valid time zone yet.
    assert _get_num_files_in_dir(reports_path) == 0
    report_manager.process()
    assert _get_num_files_in_dir(reports_path) == 0

    first_time = whenever.ZonedDateTime(
        year=2025,
        month=9,
        day=28,
        hour=16,
        minute=59,
        second=59,
        tz="America/Chicago",
    )
    time_source.set_current_time(first_time)
    assert time_source.get_current_time() == first_time

    # Processing should create an empty report file based on the current date.
    assert _get_num_files_in_dir(reports_path) == 0
    report_manager.process()
    assert _get_num_files_in_dir(reports_path) == 1

    # Check the file name and header.
    first_report_path = reports_path / "sandman2025-09-27.rpt"
    first_report_lines = _check_file_and_read_lines(first_report_path)

    assert len(first_report_lines) == 1

    header = json.loads(first_report_lines[0])
    assert header["version"] == report.ReportManager.REPORT_VERSION

    first_start_time = first_time.add(days=-1)
    first_start_time = first_start_time.replace_time(whenever.Time(17, 0))
    assert header["start"] == first_start_time.format_common_iso()

    # Processing again without changing time or adding events should not create
    # new files.
    report_manager.process()
    assert _get_num_files_in_dir(reports_path) == 1

    # Add one second to cross into the next report day.
    second_time = first_time.add(seconds=1)
    time_source.set_current_time(second_time)

    report_manager.process()
    assert _get_num_files_in_dir(reports_path) == 2

    # Check the file name and header.
    first_report_lines = _check_file_and_read_lines(first_report_path)

    assert len(first_report_lines) == 1

    header = json.loads(first_report_lines[0])
    assert header["version"] == report.ReportManager.REPORT_VERSION
    assert header["start"] == first_start_time.format_common_iso()

    second_report_path = reports_path / "sandman2025-09-28.rpt"
    second_report_lines = _check_file_and_read_lines(second_report_path)

    assert len(second_report_lines) == 1

    header = json.loads(second_report_lines[0])
    assert header["version"] == report.ReportManager.REPORT_VERSION

    second_start_time = second_time.replace_time(whenever.Time(17, 0))
    assert header["start"] == second_start_time.format_common_iso()


def test_report_events(tmp_path: pathlib.Path) -> None:
    """Test the addition of events to report files."""
    reports_path = tmp_path / "reports/"
    report.bootstrap_reports(str(tmp_path) + "/")
    assert reports_path.exists() == True

    time_source = test_time_util.TestTimeSource()
    report_manager = report.ReportManager(time_source, str(tmp_path) + "/")

    # Events should be ignored if there is no valid time zone.
    report_manager.add_status_event()

    first_time = whenever.ZonedDateTime(
        year=2025,
        month=9,
        day=28,
        hour=16,
        minute=59,
        second=59,
        tz="America/Chicago",
    )
    time_source.set_current_time(first_time)
    assert time_source.get_current_time() == first_time

    # Adding an event before processing does not cause a file to get created.
    report_manager.add_status_event()
    assert _get_num_files_in_dir(reports_path) == 0

    # Once processed, the event should show up in the appropriate file
    report_manager.process()
    assert _get_num_files_in_dir(reports_path) == 1

    first_report_path = reports_path / "sandman2025-09-27.rpt"
    first_report_lines = _check_file_and_read_lines(first_report_path)

    assert len(first_report_lines) == 2

    header = json.loads(first_report_lines[0])
    assert header["version"] == report.ReportManager.REPORT_VERSION

    first_event = json.loads(first_report_lines[1])
    first_event_time = whenever.ZonedDateTime.parse_common_iso(
        first_event["when"]
    )
    assert first_event_time == first_time
    assert first_event["info"] == {"type": "status"}

    # Adding events that belong in different files, even out of order, will
    # put them in the correct files.
    second_time = first_time.add(seconds=1)
    time_source.set_current_time(second_time)
    report_manager.add_routine_event("start")

    time_source.set_current_time(first_time)
    report_manager.add_routine_event("stop")

    assert _get_num_files_in_dir(reports_path) == 1
    report_manager.process()
    assert _get_num_files_in_dir(reports_path) == 2

    first_report_lines = _check_file_and_read_lines(first_report_path)

    assert len(first_report_lines) == 3

    header = json.loads(first_report_lines[0])
    assert header["version"] == report.ReportManager.REPORT_VERSION

    first_event = json.loads(first_report_lines[1])
    first_event_time = whenever.ZonedDateTime.parse_common_iso(
        first_event["when"]
    )
    assert first_event_time == first_time
    assert first_event["info"] == {"type": "status"}

    second_event = json.loads(first_report_lines[2])
    second_event_time = whenever.ZonedDateTime.parse_common_iso(
        second_event["when"]
    )
    assert second_event_time == first_time
    assert second_event["info"] == {"type": "routine", "action": "stop"}

    # Check the second file.
    second_report_path = reports_path / "sandman2025-09-28.rpt"
    second_report_lines = _check_file_and_read_lines(second_report_path)

    assert len(second_report_lines) == 2

    header = json.loads(second_report_lines[0])
    assert header["version"] == report.ReportManager.REPORT_VERSION

    first_event = json.loads(second_report_lines[1])
    first_event_time = whenever.ZonedDateTime.parse_common_iso(
        first_event["when"]
    )
    assert first_event_time == second_time
    assert first_event["info"] == {"type": "routine", "action": "start"}

    # Add some control events.
    third_time = second_time.add(seconds=5)
    time_source.set_current_time(third_time)
    control_name = "test_control"
    move_up_string = controls.Control.State.MOVE_UP.as_string()
    source_name = "test"
    report_manager.add_control_event(control_name, move_up_string, source_name)

    fourth_time = third_time.add(seconds=9)
    time_source.set_current_time(fourth_time)
    move_down_string = controls.Control.State.MOVE_DOWN.as_string()
    report_manager.add_control_event(
        control_name, move_down_string, source_name
    )

    second_report_lines = _check_file_and_read_lines(second_report_path)
    assert len(second_report_lines) == 2

    report_manager.process()
    second_report_lines = _check_file_and_read_lines(second_report_path)

    assert len(second_report_lines) == 4

    header = json.loads(second_report_lines[0])
    assert header["version"] == report.ReportManager.REPORT_VERSION

    first_event = json.loads(second_report_lines[1])
    first_event_time = whenever.ZonedDateTime.parse_common_iso(
        first_event["when"]
    )
    assert first_event_time == second_time
    assert first_event["info"] == {"type": "routine", "action": "start"}

    second_event = json.loads(second_report_lines[2])
    second_event_time = whenever.ZonedDateTime.parse_common_iso(
        second_event["when"]
    )
    assert second_event_time == third_time
    assert second_event["info"] == {
        "type": "control",
        "control": control_name,
        "action": move_up_string,
        "source": source_name,
    }

    third_event = json.loads(second_report_lines[3])
    third_event_time = whenever.ZonedDateTime.parse_common_iso(
        third_event["when"]
    )
    assert third_event_time == fourth_time
    assert third_event["info"] == {
        "type": "control",
        "control": control_name,
        "action": move_down_string,
        "source": source_name,
    }


def test_report_bootstrap(tmp_path: pathlib.Path) -> None:
    """Test report bootstrapping."""
    reports_path = tmp_path / "reports/"
    assert reports_path.exists() == False

    report.bootstrap_reports(str(tmp_path) + "/")
    assert reports_path.exists() == True
