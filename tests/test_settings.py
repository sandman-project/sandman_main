"""Tests settings."""

import pathlib

import pytest

import sandman_main.settings as settings


def test_settings_initialization() -> None:
    """Test settings initialization."""
    test_settings = settings.Settings()
    assert test_settings.time_zone_name == ""

    with pytest.raises(TypeError):
        test_settings.time_zone_name = 1
    with pytest.raises(ValueError):
        test_settings.time_zone_name = ""
    with pytest.raises(ValueError):
        test_settings.time_zone_name = "America"

    test_settings.time_zone_name = "America/Chicago"
    assert test_settings.time_zone_name == "America/Chicago"

    with pytest.raises(ValueError):
        test_settings.time_zone_name = ""
    assert test_settings.time_zone_name == "America/Chicago"


def test_settings_bootstrap(tmp_path: pathlib.Path) -> None:
    """Test setting bootstrapping."""
    settings_path = tmp_path / "settings.cfg"
    assert settings_path.exists() == False

    settings.bootstrap_settings(str(tmp_path) + "/")
    # assert settings_path.exists() == True
