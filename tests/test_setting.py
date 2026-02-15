"""Tests settings."""

import pathlib

import pytest

import sandman_main.setting as setting

_default_time_zone_name = ""
_default_startup_delay_sec = -1


def _check_default_settings(test_settings: setting.Settings) -> None:
    assert test_settings.time_zone_name == _default_time_zone_name
    assert test_settings.startup_delay_sec == _default_startup_delay_sec
    assert test_settings.is_valid() == False


def test_settings_initialization() -> None:
    """Test settings initialization."""
    test_settings = setting.Settings()
    _check_default_settings(test_settings)

    with pytest.raises(TypeError):
        test_settings.time_zone_name = 1
    _check_default_settings(test_settings)

    with pytest.raises(ValueError):
        test_settings.time_zone_name = ""
    _check_default_settings(test_settings)

    with pytest.raises(ValueError):
        test_settings.time_zone_name = "America"
    _check_default_settings(test_settings)

    intended_time_zone_name = "America/Chicago"

    test_settings.time_zone_name = intended_time_zone_name
    assert test_settings.time_zone_name == intended_time_zone_name
    assert test_settings.startup_delay_sec == _default_startup_delay_sec
    assert test_settings.is_valid() == False

    with pytest.raises(ValueError):
        test_settings.time_zone_name = ""
    assert test_settings.time_zone_name == intended_time_zone_name
    assert test_settings.startup_delay_sec == _default_startup_delay_sec
    assert test_settings.is_valid() == False

    with pytest.raises(TypeError):
        test_settings.startup_delay_sec = ""
    assert test_settings.time_zone_name == intended_time_zone_name
    assert test_settings.startup_delay_sec == _default_startup_delay_sec
    assert test_settings.is_valid() == False

    with pytest.raises(ValueError):
        test_settings.startup_delay_sec = -2
    assert test_settings.time_zone_name == intended_time_zone_name
    assert test_settings.startup_delay_sec == _default_startup_delay_sec
    assert test_settings.is_valid() == False

    intended_startup_delay_sec = 2

    test_settings.startup_delay_sec = intended_startup_delay_sec
    assert test_settings.time_zone_name == intended_time_zone_name
    assert test_settings.startup_delay_sec == intended_startup_delay_sec
    assert test_settings.is_valid() == True

    with pytest.raises(ValueError):
        test_settings.startup_delay_sec = -1
    assert test_settings.time_zone_name == intended_time_zone_name
    assert test_settings.startup_delay_sec == intended_startup_delay_sec
    assert test_settings.is_valid() == True


def test_settings_loading() -> None:
    """Test settings loading."""
    settings_dir: str = "tests/data/settings/"

    with pytest.raises(FileNotFoundError):
        test_settings = setting.Settings.parse_from_file(settings_dir + "a")

    # Empty files cannot be parsed.
    test_settings = setting.Settings.parse_from_file(
        settings_dir + "settings_empty.cfg"
    )
    _check_default_settings(test_settings)

    # Files with improperly formed JSON cannot be parsed.
    test_settings = setting.Settings.parse_from_file(
        settings_dir + "settings_invalid.cfg"
    )
    _check_default_settings(test_settings)

    intended_time_zone_name = "America/Chicago"
    intended_startup_delay_sec = 2

    test_settings = setting.Settings.parse_from_file(
        settings_dir + "settings_missing_time_zone.cfg"
    )
    assert test_settings.time_zone_name == _default_time_zone_name
    assert test_settings.startup_delay_sec == intended_startup_delay_sec
    assert test_settings.is_valid() == False

    test_settings = setting.Settings.parse_from_file(
        settings_dir + "settings_type_time_zone.cfg"
    )
    assert test_settings.time_zone_name == _default_time_zone_name
    assert test_settings.startup_delay_sec == intended_startup_delay_sec
    assert test_settings.is_valid() == False

    test_settings = setting.Settings.parse_from_file(
        settings_dir + "settings_invalid_time_zone.cfg"
    )
    assert test_settings.time_zone_name == _default_time_zone_name
    assert test_settings.startup_delay_sec == intended_startup_delay_sec
    assert test_settings.is_valid() == False

    test_settings = setting.Settings.parse_from_file(
        settings_dir + "settings_missing_startup_delay.cfg"
    )
    assert test_settings.time_zone_name == intended_time_zone_name
    assert test_settings.startup_delay_sec == _default_startup_delay_sec
    assert test_settings.is_valid() == False

    test_settings = setting.Settings.parse_from_file(
        settings_dir + "settings_type_startup_delay.cfg"
    )
    assert test_settings.time_zone_name == intended_time_zone_name
    assert test_settings.startup_delay_sec == _default_startup_delay_sec
    assert test_settings.is_valid() == False

    test_settings = setting.Settings.parse_from_file(
        settings_dir + "settings_invalid_startup_delay.cfg"
    )
    assert test_settings.time_zone_name == intended_time_zone_name
    assert test_settings.startup_delay_sec == _default_startup_delay_sec
    assert test_settings.is_valid() == False

    test_settings = setting.Settings.parse_from_file(
        settings_dir + "settings_valid.cfg"
    )
    assert test_settings.time_zone_name == intended_time_zone_name
    assert test_settings.startup_delay_sec == intended_startup_delay_sec
    assert test_settings.is_valid() == True


def test_settings_saving(tmp_path: pathlib.Path) -> None:
    """Test settings saving."""
    # Don't write invalid settings.
    original_settings = setting.Settings()
    assert original_settings.is_valid() == False

    filename = tmp_path / "test_invalid.cfg"
    assert filename.exists() == False

    original_settings.save_to_file(str(filename))
    assert filename.exists() == False

    # After writing valid settings, they should be the same when read back in.
    original_settings = setting.Settings.parse_from_file(
        "tests/data/settings/settings_valid.cfg"
    )
    assert original_settings.is_valid() == True

    filename = tmp_path / "test_valid.cfg"
    assert filename.exists() == False

    original_settings.save_to_file(str(filename))
    assert filename.exists() == True

    written_settings = setting.Settings.parse_from_file(str(filename))
    assert written_settings.is_valid() == True
    assert written_settings == original_settings

    with pytest.raises(OSError):
        original_settings.save_to_file("")


def test_settings_bootstrap(tmp_path: pathlib.Path) -> None:
    """Test setting bootstrapping."""
    settings_path = tmp_path / "settings.cfg"
    assert settings_path.exists() == False

    setting.bootstrap_settings(str(tmp_path) + "/")
    assert settings_path.exists() == True

    # Check that the settings are as expected.
    expected_time_zone_name = "America/Chicago"
    expected_startup_delay_sec = 4

    written_settings = setting.Settings.parse_from_file(str(settings_path))
    assert written_settings.is_valid() == True
    assert written_settings.time_zone_name == expected_time_zone_name
    assert written_settings.startup_delay_sec == expected_startup_delay_sec

    # Bootstrap should not overwrite existing settings.
    expected_time_zone_name = "America/New_York"
    expected_startup_delay_sec = 2
    updated_settings = written_settings
    updated_settings.time_zone_name = expected_time_zone_name
    updated_settings.startup_delay_sec = expected_startup_delay_sec
    updated_settings.save_to_file(str(settings_path))

    setting.bootstrap_settings(str(tmp_path) + "/")

    written_settings = setting.Settings.parse_from_file(str(settings_path))
    assert written_settings.is_valid() == True
    assert written_settings.time_zone_name == expected_time_zone_name
    assert written_settings.startup_delay_sec == expected_startup_delay_sec
