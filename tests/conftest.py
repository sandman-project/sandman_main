"""Home for test fixtures, etc."""

import collections.abc

import pytest

import sandman_main.sandman as sandman_module


@pytest.fixture
def sandman() -> collections.abc.Generator[sandman_module.Sandman]:
    """Return a test app."""
    app = sandman_module.create_app(
        {"BASE_DIR": "tests/data/", "TESTING": True}
    )
    if app is None:
        raise ValueError("failed to create app")
    yield app
