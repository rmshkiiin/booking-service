import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.config import settings
from app.database import Base, get_db
from app.main import app
from tests.helpers import auth_headers

# Отдельная база в памяти: тесты не трогают настоящие данные.
test_engine = create_engine(
    "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
)
TestingSession = sessionmaker(bind=test_engine, autoflush=False)


def override_get_db():
    db = TestingSession()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def client():
    Base.metadata.create_all(test_engine)
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()
    Base.metadata.drop_all(test_engine)


@pytest.fixture
def admin_headers(client, monkeypatch):
    monkeypatch.setattr(settings, "admin_email", "admin@example.com")
    return auth_headers(client, "admin@example.com")


@pytest.fixture
def user_headers(client):
    return auth_headers(client, "user@example.com")


@pytest.fixture
def resource(client, admin_headers):
    response = client.post(
        "/resources", json={"name": "Переговорка", "capacity": 6}, headers=admin_headers
    )
    return response.json()
