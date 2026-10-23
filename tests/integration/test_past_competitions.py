import server


def test_past_competition_cannot_be_booked(client):
    response = client.post(
        "/purchasePlaces",
        data={
            "competition": "Past Festival",
            "club": "Simply Lift",
            "places": "1",
        },
    )

    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "compétition est passée" in html
    assert server.clubs[0]["points"] == "13"
    assert server.competitions[3]["numberOfPlaces"] == "20"
    assert server.get_booked_places(
        "Simply Lift",
        "Past Festival",
    ) == 0
