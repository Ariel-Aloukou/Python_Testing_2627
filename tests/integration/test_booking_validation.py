import server


def test_non_numeric_places_are_refused(simply_lift_client):
    response = simply_lift_client.post(
        "/purchasePlaces",
        data={
            "competition": "Spring Festival",
            "club": "Simply Lift",
            "places": "deux",
        },
    )

    assert response.status_code == 200
    assert "Le nombre de places doit être un nombre entier." in (
        response.get_data(as_text=True)
    )
    assert server.clubs[0]["points"] == "13"
    assert server.competitions[0]["numberOfPlaces"] == "25"
    assert server.get_booked_places(
        "Simply Lift",
        "Spring Festival",
    ) == 0


def test_missing_places_are_refused(simply_lift_client):
    response = simply_lift_client.post(
        "/purchasePlaces",
        data={
            "competition": "Spring Festival",
            "club": "Simply Lift",
        },
    )

    assert response.status_code == 200
    assert "Les champs du formulaire sont incomplets." in (
        response.get_data(as_text=True)
    )
    assert server.clubs[0]["points"] == "13"
    assert server.competitions[0]["numberOfPlaces"] == "25"
    assert server.get_booked_places(
        "Simply Lift",
        "Spring Festival",
    ) == 0


def test_missing_competition_is_refused(simply_lift_client):
    response = simply_lift_client.post(
        "/purchasePlaces",
        data={
            "club": "Simply Lift",
            "places": "1",
        },
    )

    assert response.status_code == 200
    assert "Les champs du formulaire sont incomplets." in (
        response.get_data(as_text=True)
    )
    assert server.clubs[0]["points"] == "13"
    assert server.competitions[0]["numberOfPlaces"] == "25"
    assert server.get_booked_places(
        "Simply Lift",
        "Spring Festival",
    ) == 0


def test_empty_places_are_refused(simply_lift_client):
    response = simply_lift_client.post(
        "/purchasePlaces",
        data={
            "competition": "Spring Festival",
            "club": "Simply Lift",
            "places": "",
        },
    )

    assert response.status_code == 200
    assert "Les champs du formulaire sont incomplets." in (
        response.get_data(as_text=True)
    )
    assert server.clubs[0]["points"] == "13"
    assert server.competitions[0]["numberOfPlaces"] == "25"


def test_zero_places_are_refused(simply_lift_client):
    response = simply_lift_client.post(
        "/purchasePlaces",
        data={
            "competition": "Spring Festival",
            "club": "Simply Lift",
            "places": "0",
        },
    )

    assert response.status_code == 200
    assert "Le nombre de places doit être au moins 1." in (
        response.get_data(as_text=True)
    )
    assert server.clubs[0]["points"] == "13"
    assert server.competitions[0]["numberOfPlaces"] == "25"
    assert server.get_booked_places(
        "Simply Lift",
        "Spring Festival",
    ) == 0


def test_booking_form_has_native_validation(simply_lift_client):
    response = simply_lift_client.get(
        "/book/Spring%20Festival/Simply%20Lift"
    )

    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert 'min="1"' in html
    assert 'max="12"' in html
    assert 'step="1"' in html
    assert "required" in html
