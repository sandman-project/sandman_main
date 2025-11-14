"""Tests initialization."""

import pathlib

import sandman_main.sandman as sandman


def test_create(tmp_path: pathlib.Path) -> None:
    """Test app creation."""
    base_dir = str(tmp_path) + "/"

    assert sandman.create_app({"BASE_DIR": base_dir})

    regular_app = sandman.create_app({"BASE_DIR": base_dir})
    assert regular_app is not None
    assert regular_app.is_testing() == False

    testing_app = sandman.create_app({"BASE_DIR": base_dir, "TESTING": True})
    assert testing_app is not None
    assert testing_app.is_testing() == True
