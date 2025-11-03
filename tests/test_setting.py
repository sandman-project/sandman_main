"""Tests settings."""

import pathlib


def test_setting_bootstrap(tmp_path: pathlib.Path) -> None:
    """Test setting bootstrapping."""
    setting_path = tmp_path / "settings.cfg"
    assert setting_path.exists() == False
