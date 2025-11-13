import pytest
from fastapi.testclient import TestClient
from app.core.security import create_access_token
from unittest.mock import MagicMock, patch

import bcrypt

# Patch bcrypt to accept longer passwords by hashing first
bcrypt.hashpw = lambda pw, salt: bcrypt._bcrypt.hashpw(pw[:72], salt)


# IMPORTANT: import app only inside the fixture after we patched the collections
@pytest.fixture
def mock_db():
    """Patch the collections on the route modules so endpoints use these mocks."""
    mock_notes = MagicMock()
    mock_users = MagicMock()

    # Patch the exact attributes used by the route modules
    notes_patch = patch("app.routes.notes.notes_collection", mock_notes)
    auth_patch = patch("app.routes.auth.users_collection", mock_users)

    notes_patch.start()
    auth_patch.start()

    yield mock_notes, mock_users

    notes_patch.stop()
    auth_patch.stop()


@pytest.fixture
def client():
    """Return a TestClient for the real app."""
    from app.main import app

    return TestClient(app)


# helper fixture that generates a valid-ish mock token (if you use create_access_token)
@pytest.fixture
def mock_token():
    return "fake-token-for-tests"
