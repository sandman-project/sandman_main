"""Tests reports."""

import json
import pathlib

import whenever

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

    assert _get_num_files_in_dir(reports_path) == 0
    report_manager = report.ReportManager(time_source, str(tmp_path) + "/")

    # Processing should create an empty report file based on the current date.
    assert _get_num_files_in_dir(reports_path) == 0
    report_manager.process()
    assert _get_num_files_in_dir(reports_path) == 1

    # Check the file name and header.
    first_report_path = reports_path / "sandman2025-09-27.rpt"
    first_report_lines = _check_file_and_read_lines(first_report_path)

    assert len(first_report_lines) == 1

    header = json.loads(first_report_lines[0])
    assert header["version"] == 4

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
    assert header["version"] == 4
    assert header["start"] == first_start_time.format_common_iso()

    second_report_path = reports_path / "sandman2025-09-28.rpt"
    second_report_lines = _check_file_and_read_lines(second_report_path)

    assert len(second_report_lines) == 1

    header = json.loads(second_report_lines[0])
    assert header["version"] == 4

    second_start_time = second_time.replace_time(whenever.Time(17, 0))
    assert header["start"] == second_start_time.format_common_iso()


def test_report_bootstrap(tmp_path: pathlib.Path) -> None:
    """Test report bootstrapping."""
    reports_path = tmp_path / "reports/"
    assert reports_path.exists() == False

    report.bootstrap_reports(str(tmp_path) + "/")
    assert reports_path.exists() == True
