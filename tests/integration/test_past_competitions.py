import re

import server


def test_past_competition_cannot_be_booked(simply_lift_client):
    response = simply_lift_client.post(
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


def test_past_competition_is_visible_but_not_bookable(simply_lift_client):
    response = simply_lift_client.post(
        "/showSummary",
        data={"email": "john@simplylift.co"},
    )

    assert response.status_code == 200
    html = response.get_data(as_text=True)
    # Find the li element that contains Past Festival
    for match in re.finditer(r"<li[^>]*>.*?</li>", html, re.S):
        if "Past Festival" in match.group(0):
            past_block = match
            break
    else:
        past_block = None

    assert past_block is not None
    assert "Compétition passée" in past_block.group(0)
    assert "Book Places" not in past_block.group(0)


def test_booking_page_is_refused_for_past_competition(simply_lift_client):
    response = simply_lift_client.get("/book/Past%20Festival/Simply%20Lift")

    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "compétition est passée" in html
    assert "How many places?" not in html
