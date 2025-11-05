"""Tests settings."""

import pathlib

import pytest

import sandman_main.setting as setting


def test_settings_initialization() -> None:
    """Test settings initialization."""
    settings = setting.Settings()
    assert settings.time_zone_name == ""

    with pytest.raises(TypeError):
        settings.time_zone_name = 1
    with pytest.raises(ValueError):
        settings.time_zone_name = ""
    with pytest.raises(ValueError):
        settings.time_zone_name = "America"

    settings.time_zone_name = "America/Chicago"
    assert settings.time_zone_name == "America/Chicago"


def test_settings_bootstrap(tmp_path: pathlib.Path) -> None:
    """Test setting bootstrapping."""
    settings_path = tmp_path / "settings.cfg"
    assert settings_path.exists() == False

    setting.bootstrap_settings(str(tmp_path) + "/")
    # assert settings_path.exists() == True
