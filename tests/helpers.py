from datetime import datetime, timedelta, timezone


def at(hour: int) -> str:
    """Время завтра в UTC: at(10) = завтра 10:00. Отрицательные часы дают прошлое."""
    tomorrow = datetime.now(timezone.utc) + timedelta(days=1)
    base = tomorrow.replace(hour=0, minute=0, second=0, microsecond=0)
    return (base + timedelta(hours=hour)).isoformat()


def auth_headers(client, email: str, password: str = "password123") -> dict:
    client.post("/auth/register", json={"email": email, "password": password})
    response = client.post("/auth/login", json={"email": email, "password": password})
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def book(client, headers: dict, resource_id: int, start_hour: int, end_hour: int):
    return client.post(
        "/bookings",
        json={"resource_id": resource_id, "start_time": at(start_hour), "end_time": at(end_hour)},
        headers=headers,
    )
