import server


def test_booking_debits_club_points(client):
    response = client.post(
        "/purchasePlaces",
        data={
            "competition": "Spring Festival",
            "club": "Simply Lift",
            "places": "2",
        },
    )

    assert response.status_code == 200
    assert server.clubs[0]["points"] == "11"
    assert server.competitions[0]["numberOfPlaces"] == 23


def test_booking_with_insufficient_points_is_refused(client):
    response = client.post(
        "/purchasePlaces",
        data={
            "competition": "Spring Festival",
            "club": "Iron Temple",
            "places": "5",
        },
    )

    assert response.status_code == 200
    assert b"Solde de points insuffisant" in response.data
    assert server.clubs[1]["points"] == "4"
    assert server.competitions[0]["numberOfPlaces"] == "25"


def test_booking_updates_points_on_welcome_page(client):
    response = client.post(
        "/purchasePlaces",
        data={
            "competition": "Spring Festival",
            "club": "Simply Lift",
            "places": "2",
        },
    )

    assert response.status_code == 200
    assert b"Points available: 11" in response.data


def test_points_remain_updated_on_next_login(client):
    client.post(
        "/purchasePlaces",
        data={
            "competition": "Spring Festival",
            "club": "Simply Lift",
            "places": "2",
        },
    )

    response = client.post(
        "/showSummary",
        data={"email": "john@simplylift.co"},
    )

    assert response.status_code == 200
    assert b"Points available: 11" in response.data
