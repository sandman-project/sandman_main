"""Tests initialization."""

import sandman_main.sandman as sandman


def test_create() -> None:
    """Test app creation."""
    assert sandman.create_app({"BASE_DIR": "tests/data/"})

    regular_app = sandman.create_app({"BASE_DIR": "tests/data/"})
    assert regular_app is not None
    assert regular_app.is_testing() == False

    testing_app = sandman.create_app({"BASE_DIR": "tests/data/", "TESTING": True})
    assert testing_app is not None
    assert testing_app.is_testing() == True
