"""Tests initialization."""

import sandman_main.sandman as sandman


def test_create() -> None:
    """Test app creation."""
    assert sandman.create_app({"BASE_DIR": "tests/data/"})
