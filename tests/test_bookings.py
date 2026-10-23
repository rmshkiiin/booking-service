from tests.helpers import book


def test_create_booking(client, user_headers, resource):
    response = book(client, user_headers, resource["id"], 10, 11)
    assert response.status_code == 201
    assert response.json()["status"] == "active"


def test_end_before_start_rejected(client, user_headers, resource):
    assert book(client, user_headers, resource["id"], 11, 10).status_code == 422


def test_booking_in_past_rejected(client, user_headers, resource):
    assert book(client, user_headers, resource["id"], -24, -23).status_code == 422


def test_unknown_resource(client, user_headers):
    assert book(client, user_headers, 999, 10, 11).status_code == 404


def test_overlapping_booking_conflicts(client, user_headers, admin_headers, resource):
    assert book(client, user_headers, resource["id"], 10, 12).status_code == 201
    assert book(client, admin_headers, resource["id"], 11, 13).status_code == 409


def test_adjacent_bookings_are_allowed(client, user_headers, resource):
    assert book(client, user_headers, resource["id"], 10, 11).status_code == 201
    assert book(client, user_headers, resource["id"], 11, 12).status_code == 201


def test_cancel_frees_the_slot(client, user_headers, resource):
    created = book(client, user_headers, resource["id"], 10, 11).json()
    assert client.delete(f"/bookings/{created['id']}", headers=user_headers).status_code == 204
    assert book(client, user_headers, resource["id"], 10, 11).status_code == 201


def test_cannot_cancel_other_users_booking(client, user_headers, admin_headers, resource):
    created = book(client, user_headers, resource["id"], 10, 11).json()
    assert client.delete(f"/bookings/{created['id']}", headers=admin_headers).status_code == 404
    # бронь осталась активной, значит время всё ещё занято
    assert book(client, admin_headers, resource["id"], 10, 11).status_code == 409


def test_my_bookings_shows_only_own(client, user_headers, admin_headers, resource):
    book(client, user_headers, resource["id"], 10, 11)
    book(client, admin_headers, resource["id"], 12, 13)
    mine = client.get("/bookings", headers=user_headers).json()
    assert len(mine) == 1


def test_admin_sees_all_bookings_with_stats(client, user_headers, admin_headers, resource):
    first = book(client, user_headers, resource["id"], 10, 11).json()
    book(client, user_headers, resource["id"], 12, 13)
    client.delete(f"/bookings/{first['id']}", headers=user_headers)
    body = client.get("/admin/bookings", headers=admin_headers).json()
    assert body["stats"] == {"total": 2, "active": 1, "cancelled": 1}
    assert len(body["bookings"]) == 2


def test_regular_user_cannot_see_admin_bookings(client, user_headers):
    assert client.get("/admin/bookings", headers=user_headers).status_code == 403
