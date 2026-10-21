"""Shared pytest fixtures.

The tests run against a throw away SQLite database that is seeded from the
dataset files that ship with the server - they never touch a developer
database and never need a network connection.
"""

import os
import pathlib
import sys
import tempfile

SERVER_DIR = pathlib.Path(__file__).resolve().parents[1]
if str(SERVER_DIR) not in sys.path:
    sys.path.insert(0, str(SERVER_DIR))

TEST_DB = pathlib.Path(tempfile.gettempdir()) / "nutrimitra_test_suite.db"
if TEST_DB.exists():
    TEST_DB.unlink()

os.environ["DATABASE_URL"] = f"sqlite:///{TEST_DB}"
os.environ["DATA_DIR"] = str(SERVER_DIR / "data")
os.environ["SECRET_KEY"] = "test-secret-key"

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.core.database import Base, engine  # noqa: E402
from app.main import app  # noqa: E402
from app.models.food_item import FoodItem  # noqa: E402


@pytest.fixture(scope="session", autouse=True)
def prepared_database():
    """Create the schema and import the dataset once for the whole session."""
    Base.metadata.create_all(bind=engine)
    yield
    engine.dispose()
    try:
        TEST_DB.unlink()
    except OSError:
        # The file is still held by a connection on Windows - it lives in the
        # temp folder, so it is cleaned up by the operating system.
        pass


@pytest.fixture()
def client():
    """A client that runs the application lifespan (dataset import included)."""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture()
def food_count():
    with engine.connect() as connection:
        return connection.execute(
            FoodItem.__table__.select().with_only_columns(FoodItem.id)
        ).rowcount


def register_and_login(client: TestClient, email: str = "tester@example.com") -> str:
    """Create a user and return its access token."""
    response = client.post(
        "/v1/auth/register",
        json={"email": email, "password": "s3cret-pass", "name": "Test User"},
    )
    assert response.status_code == 201, response.text
    response = client.post(
        "/v1/auth/login", json={"email": email, "password": "s3cret-pass"}
    )
    assert response.status_code == 200, response.text
    return response.json()["access_token"]


PROFILE = {
    "age": 30,
    "gender": "male",
    "height_cm": 175,
    "weight_kg": 70,
    "activity_level": "moderate",
    "diet_type": "balanced",
}
