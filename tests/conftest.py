"""Home for test fixtures, etc."""

from collections.abc import Generator

import pytest

from sandman_main.sandman import Sandman, create_app


@pytest.fixture
def sandman() -> Generator[Sandman]:
    """Return a test app."""
    app = create_app({"BASE_DIR": "tests/data/", "TESTING": True})
    if app is None:
        raise ValueError("failed to create app")
    yield app
