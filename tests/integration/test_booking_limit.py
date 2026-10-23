import server


def test_booking_form_limits_places_to_12(simply_lift_client):
    response = simply_lift_client.get("/book/Spring%20Festival/Simply%20Lift")

    assert response.status_code == 200
    assert b'max="12"' in response.data


def test_booking_more_than_12_places_is_refused_by_server(simply_lift_client):
    response = simply_lift_client.post(
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


def test_booking_exactly_12_places_is_accepted(simply_lift_client):
    response = simply_lift_client.post(
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


def test_second_booking_for_same_competition_is_refused(simply_lift_client):
    first = simply_lift_client.post(
        "/purchasePlaces",
        data={
            "competition": "Spring Festival",
            "club": "Simply Lift",
            "places": "6",
        },
    )
    second = simply_lift_client.post(
        "/purchasePlaces",
        data={
            "competition": "Spring Festival",
            "club": "Simply Lift",
            "places": "1",
        },
    )

    assert first.status_code == 200
    assert second.status_code == 200
    assert "Vous avez déjà réservé cette compétition." in (
        second.get_data(as_text=True)
    )
    assert server.clubs[0]["points"] == "7"
    assert server.competitions[0]["numberOfPlaces"] == 19
    assert server.get_booked_places(
        "Simply Lift",
        "Spring Festival",
    ) == 6


def test_refused_duplicate_booking_is_not_recorded(simply_lift_client):
    simply_lift_client.post(
        "/purchasePlaces",
        data={
            "competition": "Spring Festival",
            "club": "Simply Lift",
            "places": "6",
        },
    )

    refused = simply_lift_client.post(
        "/purchasePlaces",
        data={
            "competition": "Spring Festival",
            "club": "Simply Lift",
            "places": "7",
        },
    )

    assert refused.status_code == 200
    assert "Vous avez déjà réservé cette compétition." in (
        refused.get_data(as_text=True)
    )
    assert server.clubs[0]["points"] == "7"
    assert server.competitions[0]["numberOfPlaces"] == 19
    assert server.get_booked_places(
        "Simply Lift",
        "Spring Festival",
    ) == 6


def test_booking_limit_is_per_club(simply_lift_client):
    simply_lift_client.post(
        "/purchasePlaces",
        data={
            "competition": "Spring Festival",
            "club": "Simply Lift",
            "places": "12",
        },
    )

    simply_lift_client.post(
        "/showSummary",
        data={"email": "admin@irontemple.com"},
    )

    response = simply_lift_client.post(
        "/purchasePlaces",
        data={
            "competition": "Spring Festival",
            "club": "Iron Temple",
            "places": "4",
        },
    )

    assert response.status_code == 200
    assert b"limite de 12 places" not in response.data
    assert server.clubs[0]["points"] == "1"
    assert server.clubs[1]["points"] == "0"
    assert server.competitions[0]["numberOfPlaces"] == 9


def test_booking_limit_is_per_competition(simply_lift_client):
    simply_lift_client.post(
        "/purchasePlaces",
        data={
            "competition": "Spring Festival",
            "club": "Simply Lift",
            "places": "12",
        },
    )

    response = simply_lift_client.post(
        "/purchasePlaces",
        data={
            "competition": "Fall Classic",
            "club": "Simply Lift",
            "places": "1",
        },
    )

    assert response.status_code == 200
    assert b"limite de 12 places" not in response.data
    assert server.clubs[0]["points"] == "0"
    assert server.competitions[0]["numberOfPlaces"] == 13
    assert server.competitions[1]["numberOfPlaces"] == 12
