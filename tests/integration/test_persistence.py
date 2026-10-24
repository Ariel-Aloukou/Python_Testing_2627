import json

import server


def test_successful_booking_is_persisted(simply_lift_client):
    response = simply_lift_client.post(
        "/purchasePlaces",
        data={
            "competition": "Spring Festival",
            "club": "Simply Lift",
            "places": "2",
        },
    )

    assert response.status_code == 200
    assert server.loadClubs()[0]["points"] == "11"
    assert server.loadCompetitions()[0]["numberOfPlaces"] == "23"
    assert server.loadBookings() == {
        ("Simply Lift", "Spring Festival"): 2,
    }

    with open(server.BOOKINGS_FILE) as bookings_file:
        payload = json.load(bookings_file)
    assert payload == {
        "bookings": [
            {
                "club": "Simply Lift",
                "competition": "Spring Festival",
                "places": 2,
            }
        ]
    }


def test_saved_booking_can_be_reloaded_from_json(
    simply_lift_client,
    monkeypatch,
):
    simply_lift_client.post(
        "/purchasePlaces",
        data={
            "competition": "Spring Festival",
            "club": "Simply Lift",
            "places": "2",
        },
    )

    monkeypatch.setattr(server, "bookings", {})
    monkeypatch.setattr(server, "clubs", [])
    monkeypatch.setattr(server, "competitions", [])

    assert server.loadBookings() == {
        ("Simply Lift", "Spring Festival"): 2,
    }
    assert server.loadClubs()[0]["points"] == "11"
    assert server.loadCompetitions()[0]["numberOfPlaces"] == "23"
