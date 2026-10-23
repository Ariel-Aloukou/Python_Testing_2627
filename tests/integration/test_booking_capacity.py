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
