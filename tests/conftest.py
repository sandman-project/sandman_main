"""Home for test fixtures, etc."""

import collections.abc

import pytest

import sandman_main.sandman as sandman


@pytest.fixture
def sandman_instance() -> collections.abc.Generator[sandman.Sandman]:
    """Return a test app."""
    app = sandman.create_app(
        {"BASE_DIR": "tests/data/", "TESTING": True}
    )
    if app is None:
        raise ValueError("failed to create app")
    yield app
