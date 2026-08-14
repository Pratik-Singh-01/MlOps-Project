"""
Test Configuration — Shared Fixtures
Provides a test client with SQLite in-memory DB and auth helpers.
"""

import os
import sys
import pytest

# Ensure the project root is on the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Override config BEFORE importing app modules
os.environ["APP_ENV"] = "test"
os.environ["DATABASE_URL"] = "sqlite:///file:testdb?mode=memory&cache=shared"
os.environ["SECRET_KEY"] = "test-secret-key"
os.environ["ADMIN_USERNAME"] = "admin"
os.environ["ADMIN_PASSWORD"] = "admin123"
os.environ["VIEWER_USERNAME"] = "viewer"
os.environ["VIEWER_PASSWORD"] = "viewer123"
os.environ["API_KEYS"] = "dev-api-key-001"

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, engine as app_engine
from app.main import app, get_db


# ──────────────────────────────────────────────────────────
# TEST DATABASE (SQLite in-memory)
# ──────────────────────────────────────────────────────────

SQLALCHEMY_TEST_URL = "sqlite:///file:testdb?mode=memory&cache=shared"

test_engine = create_engine(
    SQLALCHEMY_TEST_URL,
    connect_args={"check_same_thread": False, "uri": True},
    poolclass=StaticPool,
)

TestSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=test_engine,
)


def override_get_db():
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()


# Override the DB dependency
app.dependency_overrides[get_db] = override_get_db


# ──────────────────────────────────────────────────────────
# FIXTURES
# ──────────────────────────────────────────────────────────

@pytest.fixture(scope="session", autouse=True)
def setup_database():
    """Create all tables before tests, drop after."""
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)
    test_engine.dispose()
    app_engine.dispose()


@pytest.fixture()
def client():
    """Provide a test client for the FastAPI app."""
    return TestClient(app, raise_server_exceptions=False)


@pytest.fixture()
def admin_token(client):
    """Get a JWT token for admin user."""
    response = client.post(
        "/auth/token",
        json={"username": "admin", "password": "admin123"},
    )
    return response.json()["access_token"]


@pytest.fixture()
def viewer_token(client):
    """Get a JWT token for viewer user."""
    response = client.post(
        "/auth/token",
        json={"username": "viewer", "password": "viewer123"},
    )
    return response.json()["access_token"]


@pytest.fixture()
def admin_headers(admin_token):
    """Auth headers for admin user."""
    return {"Authorization": f"Bearer {admin_token}"}


@pytest.fixture()
def viewer_headers(viewer_token):
    """Auth headers for viewer user."""
    return {"Authorization": f"Bearer {viewer_token}"}


@pytest.fixture()
def api_key_headers():
    """Auth headers using API key."""
    return {"X-API-Key": "dev-api-key-001"}
