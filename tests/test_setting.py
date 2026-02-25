"""Tests settings."""

import pathlib
import shutil

import pytest

import sandman_main.setting as setting


def _check_default_settings(test_settings: setting.Settings) -> None:
    assert (
        test_settings.time_zone_name == setting.Settings.DEFAULT_TIME_ZONE_NAME
    )
    assert (
        test_settings.startup_delay_sec
        == setting.Settings.DEFAULT_STARTUP_DELAY_SEC
    )
    assert test_settings.is_valid() == True


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

    with pytest.raises(TypeError):
        test_settings.startup_delay_sec = ""
    _check_default_settings(test_settings)

    with pytest.raises(ValueError):
        test_settings.startup_delay_sec = -2
    _check_default_settings(test_settings)

    intended_time_zone_name = "America/New_York"

    test_settings.time_zone_name = intended_time_zone_name
    assert test_settings.time_zone_name == intended_time_zone_name
    assert (
        test_settings.startup_delay_sec
        == setting.Settings.DEFAULT_STARTUP_DELAY_SEC
    )
    assert test_settings.is_valid() == True

    intended_startup_delay_sec = 2

    test_settings.startup_delay_sec = intended_startup_delay_sec
    assert test_settings.time_zone_name == intended_time_zone_name
    assert test_settings.startup_delay_sec == intended_startup_delay_sec
    assert test_settings.is_valid() == True

    with pytest.raises(ValueError):
        test_settings.time_zone_name = ""
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

    intended_time_zone_name = "America/New_York"
    intended_startup_delay_sec = 2

    test_settings = setting.Settings.parse_from_file(
        settings_dir + "settings_missing_time_zone.cfg"
    )
    assert (
        test_settings.time_zone_name == setting.Settings.DEFAULT_TIME_ZONE_NAME
    )
    assert test_settings.startup_delay_sec == intended_startup_delay_sec
    assert test_settings.was_any_missing_on_load == True
    assert test_settings.was_any_invalid_on_load == False
    assert test_settings.is_valid() == True

    test_settings = setting.Settings.parse_from_file(
        settings_dir + "settings_type_time_zone.cfg"
    )
    assert (
        test_settings.time_zone_name == setting.Settings.DEFAULT_TIME_ZONE_NAME
    )
    assert test_settings.startup_delay_sec == intended_startup_delay_sec
    assert test_settings.was_any_missing_on_load == False
    assert test_settings.was_any_invalid_on_load == True
    assert test_settings.is_valid() == True

    test_settings = setting.Settings.parse_from_file(
        settings_dir + "settings_invalid_time_zone.cfg"
    )
    assert (
        test_settings.time_zone_name == setting.Settings.DEFAULT_TIME_ZONE_NAME
    )
    assert test_settings.startup_delay_sec == intended_startup_delay_sec
    assert test_settings.was_any_missing_on_load == False
    assert test_settings.was_any_invalid_on_load == True
    assert test_settings.is_valid() == True

    test_settings = setting.Settings.parse_from_file(
        settings_dir + "settings_missing_startup_delay.cfg"
    )
    assert test_settings.time_zone_name == intended_time_zone_name
    assert (
        test_settings.startup_delay_sec
        == setting.Settings.DEFAULT_STARTUP_DELAY_SEC
    )
    assert test_settings.was_any_missing_on_load == True
    assert test_settings.was_any_invalid_on_load == False
    assert test_settings.is_valid() == True

    test_settings = setting.Settings.parse_from_file(
        settings_dir + "settings_type_startup_delay.cfg"
    )
    assert test_settings.time_zone_name == intended_time_zone_name
    assert (
        test_settings.startup_delay_sec
        == setting.Settings.DEFAULT_STARTUP_DELAY_SEC
    )
    assert test_settings.was_any_missing_on_load == False
    assert test_settings.was_any_invalid_on_load == True
    assert test_settings.is_valid() == True

    test_settings = setting.Settings.parse_from_file(
        settings_dir + "settings_invalid_startup_delay.cfg"
    )
    assert test_settings.time_zone_name == intended_time_zone_name
    assert (
        test_settings.startup_delay_sec
        == setting.Settings.DEFAULT_STARTUP_DELAY_SEC
    )
    assert test_settings.was_any_missing_on_load == False
    assert test_settings.was_any_invalid_on_load == True
    assert test_settings.is_valid() == True

    test_settings = setting.Settings.parse_from_file(
        settings_dir + "settings_valid.cfg"
    )
    assert test_settings.time_zone_name == intended_time_zone_name
    assert test_settings.startup_delay_sec == intended_startup_delay_sec
    assert test_settings.was_any_missing_on_load == False
    assert test_settings.was_any_invalid_on_load == False
    assert test_settings.is_valid() == True


def test_settings_saving(tmp_path: pathlib.Path) -> None:
    """Test settings saving."""
    # We want to test that you cannot write an invalid set of settings, but we
    # don't have a way to produce an invalid set.

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
    assert written_settings.was_any_missing_on_load == False
    assert written_settings.was_any_invalid_on_load == False
    assert written_settings.is_valid() == True
    assert written_settings == original_settings

    with pytest.raises(OSError):
        original_settings.save_to_file("")


def test_settings_load_or_create(tmp_path: pathlib.Path) -> None:
    """Test loading or creating settings."""
    settings_path = tmp_path / "settings.cfg"
    assert settings_path.exists() == False

    created_settings = setting.load_or_create_settings(str(tmp_path) + "/")
    assert settings_path.exists() == True

    # Check that the settings are as expected.
    expected_settings = setting.Settings()
    assert expected_settings.is_valid() == True

    assert created_settings == expected_settings

    written_settings = setting.Settings.parse_from_file(str(settings_path))
    assert written_settings == expected_settings
    assert written_settings.was_any_missing_on_load == False
    assert written_settings.was_any_invalid_on_load == False

    # Load or create should not overwrite valid existing settings.
    updated_settings = setting.Settings()
    updated_settings.time_zone_name = "America/New_York"
    updated_settings.startup_delay_sec = 2
    updated_settings.save_to_file(str(settings_path))

    loaded_settings = setting.load_or_create_settings(str(tmp_path) + "/")
    assert loaded_settings == updated_settings
    assert loaded_settings.was_any_missing_on_load == False
    assert loaded_settings.was_any_invalid_on_load == False

    written_settings = setting.Settings.parse_from_file(str(settings_path))
    assert written_settings == updated_settings
    assert written_settings.was_any_missing_on_load == False
    assert written_settings.was_any_invalid_on_load == False

    # Test repair of missing values.
    repair_path = tmp_path / "repair_missing"
    repair_path.mkdir()

    source_settings = pathlib.Path(
        "tests/data/settings/settings_missing_startup_delay.cfg"
    )

    # Replace this once we are on Python 3.14 where pathlib has file copy
    # operations.
    shutil.copyfile(str(source_settings), str(repair_path / "settings.cfg"))

    # The startup delay is missing, so should be the default value.
    expected_settings = setting.Settings()
    expected_settings.time_zone_name = "America/New_York"

    loaded_settings = setting.load_or_create_settings(str(repair_path) + "/")
    assert loaded_settings == expected_settings
    assert loaded_settings.was_any_missing_on_load == True
    assert loaded_settings.was_any_invalid_on_load == False

    written_settings = setting.Settings.parse_from_file(
        str(repair_path) + "/settings.cfg"
    )
    assert written_settings == expected_settings
    assert written_settings.was_any_missing_on_load == False
    assert written_settings.was_any_invalid_on_load == False

    # Test repair of invalid values.
    repair_path = tmp_path / "repair_invalid"
    repair_path.mkdir()

    source_settings = pathlib.Path(
        "tests/data/settings/settings_invalid_time_zone.cfg"
    )

    # Replace this once we are on Python 3.14 where pathlib has file copy
    # operations.
    shutil.copyfile(str(source_settings), str(repair_path / "settings.cfg"))

    # The time zone is invalid, so should be the default value.
    expected_settings = setting.Settings()
    expected_settings.startup_delay_sec = 2

    loaded_settings = setting.load_or_create_settings(str(repair_path) + "/")
    assert loaded_settings == expected_settings
    assert loaded_settings.was_any_missing_on_load == False
    assert loaded_settings.was_any_invalid_on_load == True

    written_settings = setting.Settings.parse_from_file(
        str(repair_path) + "/settings.cfg"
    )
    assert written_settings == expected_settings
    assert written_settings.was_any_missing_on_load == False
    assert written_settings.was_any_invalid_on_load == False
