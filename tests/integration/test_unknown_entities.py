import server


def test_unknown_club_returns_404_for_anonymous_user(client):
    response = client.get("/book/Spring%20Festival/Unknown%20Club")

    assert response.status_code == 404


def test_unknown_club_returns_404_for_logged_in_club(simply_lift_client):
    response = simply_lift_client.get("/book/Spring%20Festival/Unknown%20Club")

    assert response.status_code == 404


def test_unknown_competition_returns_404_for_anonymous_user(client):
    response = client.get("/book/Unknown%20Competition/Simply%20Lift")

    assert response.status_code == 404


def test_unknown_competition_returns_404_for_logged_in_club(
    simply_lift_client,
):
    response = simply_lift_client.get(
        "/book/Unknown%20Competition/Simply%20Lift"
    )

    assert response.status_code == 404


def test_unknown_competition_in_purchase_returns_404(simply_lift_client):
    response = simply_lift_client.post(
        "/purchasePlaces",
        data={
            "competition": "Unknown Competition",
            "club": "Simply Lift",
            "places": "1",
        },
    )

    assert response.status_code == 404
    assert server.clubs[0]["points"] == "13"
    assert server.competitions[0]["numberOfPlaces"] == "25"
