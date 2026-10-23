import server


def test_booking_more_than_remaining_places_is_refused(client):
    response = client.post(
        "/purchasePlaces",
        data={
            "competition": "Small Festival",
            "club": "Simply Lift",
            "places": "6",
        },
    )

    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "Capacité insuffisante" in html
    assert "Great-booking complete!" not in html
    assert server.competitions[2]["numberOfPlaces"] == "5"


def test_booking_all_remaining_places_leaves_zero(client):
    response = client.post(
        "/purchasePlaces",
        data={
            "competition": "Small Festival",
            "club": "Simply Lift",
            "places": "5",
        },
    )

    assert response.status_code == 200
    assert server.competitions[2]["numberOfPlaces"] == 0


def test_negative_places_are_refused(client):
    response = client.post(
        "/purchasePlaces",
        data={
            "competition": "Spring Festival",
            "club": "Simply Lift",
            "places": "-1",
        },
    )

    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "au moins 1" in html
    assert server.clubs[0]["points"] == "13"
    assert server.competitions[0]["numberOfPlaces"] == "25"
    assert server.get_booked_places(
        "Simply Lift",
        "Spring Festival",
    ) == 0


def test_capacity_is_validated_before_points_are_debited(client):
    response = client.post(
        "/purchasePlaces",
        data={
            "competition": "Small Festival",
            "club": "Simply Lift",
            "places": "6",
        },
    )

    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "Capacité insuffisante" in html
    assert server.clubs[0]["points"] == "13"
    assert server.competitions[2]["numberOfPlaces"] == "5"
    assert server.get_booked_places(
        "Simply Lift",
        "Small Festival",
    ) == 0
