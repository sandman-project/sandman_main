"""Tests settings."""

import pathlib

import pytest

import sandman_main.settings as settings

_default_time_zone_name = ""


def _check_default_settings(test_settings: settings.Settings) -> None:
    assert test_settings.time_zone_name == _default_time_zone_name


def test_settings_initialization() -> None:
    """Test settings initialization."""
    test_settings = settings.Settings()
    _check_default_settings(test_settings)

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


def test_settings_loading() -> None:
    """Test settings loading."""
    path: str = "tests/data/settings/"

    with pytest.raises(FileNotFoundError):
        test_settings = settings.Settings.parse_from_file(path + "a")

    # Empty files cannot be parsed.
    test_settings = settings.Settings.parse_from_file(
        path + "settings_empty.cfg"
    )
    _check_default_settings(test_settings)

    # Files with improperly formed JSON cannot be parsed.
    test_settings = settings.Settings.parse_from_file(
        path + "settings_invalid.cfg"
    )
    _check_default_settings(test_settings)


def test_settings_bootstrap(tmp_path: pathlib.Path) -> None:
    """Test setting bootstrapping."""
    settings_path = tmp_path / "settings.cfg"
    assert settings_path.exists() == False

    settings.bootstrap_settings(str(tmp_path) + "/")
    # assert settings_path.exists() == True
