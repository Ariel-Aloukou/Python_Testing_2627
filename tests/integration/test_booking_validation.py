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
