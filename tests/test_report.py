"""Tests reports."""

import pathlib

import sandman_main.report as report


def test_report_bootstrap(tmp_path: pathlib.Path) -> None:
    """Test report bootstrapping."""
    report_path = tmp_path / "reports/"
    assert report_path.exists() == False

    report.bootstrap_reports(str(tmp_path) + "/")
    assert report_path.exists() == True
