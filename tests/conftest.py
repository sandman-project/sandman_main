"""Home for test fixtures, etc."""

from collections.abc import Generator
import pytest

import sandman_main.sandman as sandman_


@pytest.fixture
def sandman() -> Generator[sandman_.Sandman]:
    """Return a test app."""
    app = sandman_.create_app({"BASE_DIR": "tests/data/", "TESTING": True})
    if app is None: raise ValueError("failed to create app")
    yield app
