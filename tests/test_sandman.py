"""Tests initialization."""

import sandman_main.sandman as sandman


def test_create() -> None:
    """Test app creation."""
    assert sandman.create_app({"BASE_DIR": "tests/data/"})
    assert (
        sandman.create_app({"BASE_DIR": "tests/data/"}).is_testing() == False
    )
    assert (
        sandman.create_app(
            {"BASE_DIR": "tests/data/", "TESTING": True}
        ).is_testing()
        == True
    )
