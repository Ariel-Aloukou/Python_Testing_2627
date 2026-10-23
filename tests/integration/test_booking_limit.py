import server


def test_booking_form_limits_places_to_12(client):
    response = client.get("/book/Spring%20Festival/Simply%20Lift")

    assert response.status_code == 200
    assert b'max="12"' in response.data


def test_booking_more_than_12_places_is_refused_by_server(client):
    response = client.post(
        "/purchasePlaces",
        data={
            "competition": "Spring Festival",
            "club": "Simply Lift",
            "places": "13",
        },
    )

    assert response.status_code == 200
    assert b"limite de 12 places" in response.data
    assert server.clubs[0]["points"] == "13"
    assert server.competitions[0]["numberOfPlaces"] == "25"


def test_booking_exactly_12_places_is_accepted(client):
    response = client.post(
        "/purchasePlaces",
        data={
            "competition": "Spring Festival",
            "club": "Simply Lift",
            "places": "12",
        },
    )

    assert response.status_code == 200
    assert server.clubs[0]["points"] == "1"
    assert server.competitions[0]["numberOfPlaces"] == 13
