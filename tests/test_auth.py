from app.config import settings


def register(client, email="a@example.com", password="password123"):
    return client.post("/auth/register", json={"email": email, "password": password})


def test_register_creates_user(client):
    response = register(client)
    assert response.status_code == 201
    body = response.json()
    assert body["email"] == "a@example.com"
    assert body["role"] == "user"
    assert "password" not in body and "password_hash" not in body


def test_register_duplicate_email(client):
    register(client)
    assert register(client).status_code == 409


def test_register_short_password(client):
    assert register(client, password="123").status_code == 422


def test_admin_email_gets_admin_role(client, monkeypatch):
    monkeypatch.setattr(settings, "admin_email", "boss@example.com")
    assert register(client, email="boss@example.com").json()["role"] == "admin"


def test_login_returns_token(client):
    register(client)
    response = client.post("/auth/login", json={"email": "a@example.com", "password": "password123"})
    assert response.status_code == 200
    assert response.json()["access_token"]


def test_login_wrong_password(client):
    register(client)
    response = client.post("/auth/login", json={"email": "a@example.com", "password": "wrong-pass"})
    assert response.status_code == 401


def test_protected_endpoint_requires_token(client):
    assert client.get("/resources").status_code == 401
    bad = {"Authorization": "Bearer not-a-real-token"}
    assert client.get("/resources", headers=bad).status_code == 401
