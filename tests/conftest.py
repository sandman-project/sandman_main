"""Home for test fixtures, etc."""

import pytest

import sandman_main.sandman as sandman


@pytest.fixture
def sandman() -> sandman.Sandman:
    """Return a test app."""
    app = sandman.create_app({"BASE_DIR": "tests/data/", "TESTING": True})

    yield app
