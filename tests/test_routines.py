"""Tests routines."""

import pathlib

import sandman_main.routines as routines


def test_routine_bootstrap(tmp_path: pathlib.Path) -> None:
    """Test routine bootstrapping."""
    reports_path = tmp_path / "routines/"
    assert reports_path.exists() == False

    routines.bootstrap_routines(str(tmp_path) + "/")
    assert reports_path.exists() == True
