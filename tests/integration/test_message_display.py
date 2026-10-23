def test_login_error_is_displayed_as_alert(client):
    response = client.post(
        "/showSummary",
        data={"email": "inconnu@example.com"},
    )

    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "Adresse email inconnue." in html
    assert 'class="error"' in html
    assert 'role="alert"' in html


def test_booking_error_is_displayed_as_alert(simply_lift_client):
    response = simply_lift_client.post(
        "/purchasePlaces",
        data={
            "competition": "Spring Festival",
            "club": "Simply Lift",
            "places": "13",
        },
    )

    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "La limite de 12 places par compétition est dépassée." in html
    assert 'class="error"' in html
    assert 'role="alert"' in html


def test_login_required_error_is_displayed_as_alert(client):
    response = client.get("/book/Spring%20Festival/Simply%20Lift")

    assert response.status_code == 401
    html = response.get_data(as_text=True)
    assert "Veuillez vous connecter" in html
    assert 'class="error"' in html
    assert 'role="alert"' in html
