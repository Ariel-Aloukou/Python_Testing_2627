def test_unknown_club_returns_404_for_anonymous_user(client):
    response = client.get("/book/Spring%20Festival/Unknown%20Club")

    assert response.status_code == 404


def test_unknown_club_returns_404_for_logged_in_club(simply_lift_client):
    response = simply_lift_client.get("/book/Spring%20Festival/Unknown%20Club")

    assert response.status_code == 404
