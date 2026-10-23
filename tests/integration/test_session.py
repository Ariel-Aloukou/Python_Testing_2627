import server


def test_login_stores_the_club_in_session(client):
    client.post(
        "/showSummary",
        data={"email": "john@simplylift.co"},
    )

    with client.session_transaction() as flask_session:
        assert flask_session["club_name"] == "Simply Lift"


def test_booking_page_requires_authentication(client):
    response = client.get("/book/Spring%20Festival/Simply%20Lift")

    assert response.status_code == 401
    html = response.get_data(as_text=True)
    assert "Veuillez vous connecter" in html


def test_purchase_requires_authentication(client):
    response = client.post(
        "/purchasePlaces",
        data={
            "competition": "Spring Festival",
            "club": "Simply Lift",
            "places": "1",
        },
    )

    assert response.status_code == 401
    assert server.clubs[0]["points"] == "13"
    assert server.competitions[0]["numberOfPlaces"] == "25"


def test_authenticated_club_can_open_booking_page(simply_lift_client):
    response = simply_lift_client.get(
        "/book/Spring%20Festival/Simply%20Lift"
    )

    assert response.status_code == 200
    assert "How many places?" in response.get_data(as_text=True)


def test_club_cannot_open_another_club_booking_page(simply_lift_client):
    response = simply_lift_client.get(
        "/book/Spring%20Festival/Iron%20Temple"
    )

    assert response.status_code == 403
    assert "Accès non autorisé" in response.get_data(as_text=True)


def test_club_cannot_purchase_for_another_club(simply_lift_client):
    response = simply_lift_client.post(
        "/purchasePlaces",
        data={
            "competition": "Spring Festival",
            "club": "Iron Temple",
            "places": "1",
        },
    )

    assert response.status_code == 403
    assert "Accès non autorisé" in response.get_data(as_text=True)
    assert server.clubs[0]["points"] == "13"
    assert server.clubs[1]["points"] == "4"
    assert server.competitions[0]["numberOfPlaces"] == "25"


def test_purchase_uses_the_session_club(simply_lift_client):
    response = simply_lift_client.post(
        "/purchasePlaces",
        data={
            "competition": "Spring Festival",
            "places": "1",
        },
    )

    assert response.status_code == 200
    assert server.clubs[0]["points"] == "12"
    assert server.competitions[0]["numberOfPlaces"] == 24


def test_logout_clears_the_session(simply_lift_client):
    response = simply_lift_client.get("/logout")

    assert response.status_code == 302
    assert response.headers["Location"] == "/"

    with simply_lift_client.session_transaction() as flask_session:
        assert "club_name" not in flask_session


def test_protected_page_requires_authentication_after_logout(
    simply_lift_client,
):
    simply_lift_client.get("/logout")

    response = simply_lift_client.get(
        "/book/Spring%20Festival/Simply%20Lift"
    )

    assert response.status_code == 401
