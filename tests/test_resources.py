from tests.helpers import at, book


def create(client, headers, name, capacity):
    return client.post("/resources", json={"name": name, "capacity": capacity}, headers=headers)


def test_regular_user_cannot_create_resource(client, user_headers):
    assert create(client, user_headers, "Зал", 10).status_code == 403


def test_admin_creates_resource(client, admin_headers):
    response = create(client, admin_headers, "Зал", 10)
    assert response.status_code == 201
    assert response.json()["is_active"] is True


def test_list_filters_by_capacity(client, admin_headers, user_headers):
    create(client, admin_headers, "Малая", 2)
    create(client, admin_headers, "Большая", 10)
    response = client.get("/resources", params={"min_capacity": 5}, headers=user_headers)
    assert [r["name"] for r in response.json()] == ["Большая"]


def test_list_pagination(client, admin_headers, user_headers):
    for i in range(3):
        create(client, admin_headers, f"Зал {i}", 4)
    first = client.get("/resources", params={"limit": 2}, headers=user_headers).json()
    rest = client.get("/resources", params={"limit": 2, "offset": 2}, headers=user_headers).json()
    assert len(first) == 2 and len(rest) == 1


def test_admin_updates_resource(client, admin_headers, resource):
    response = client.patch(f"/resources/{resource['id']}", json={"capacity": 12}, headers=admin_headers)
    assert response.status_code == 200
    assert response.json()["capacity"] == 12


def test_delete_hides_resource(client, admin_headers, user_headers, resource):
    assert client.delete(f"/resources/{resource['id']}", headers=admin_headers).status_code == 204
    assert client.get("/resources", headers=user_headers).json() == []


def test_free_filter_excludes_booked_resource(client, admin_headers, user_headers, resource):
    other = create(client, admin_headers, "Свободная", 4).json()
    book(client, user_headers, resource["id"], 10, 11)
    params = {"free_from": at(10), "free_to": at(11)}
    response = client.get("/resources", params=params, headers=user_headers)
    assert [r["id"] for r in response.json()] == [other["id"]]


def test_free_filter_needs_both_dates(client, user_headers):
    response = client.get("/resources", params={"free_from": at(10)}, headers=user_headers)
    assert response.status_code == 422
