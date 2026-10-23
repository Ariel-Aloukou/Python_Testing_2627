def test_points_route_is_public(client):
    response = client.get("/points")

    assert response.status_code == 200
    assert b"Simply Lift" in response.data
    assert b"13" in response.data
    assert b"john@simplylift.co" not in response.data


def test_points_page_displays_a_table(client):
    response = client.get("/points")

    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "<table>" in html
    assert "Simply Lift" in html
    assert "She Lifts" in html
    assert "Iron Temple" in html
    positions = [
        html.index("Simply Lift"),
        html.index("She Lifts"),
        html.index("Iron Temple"),
    ]
    assert positions == sorted(positions)


def test_points_page_is_linked_from_index(client):
    response = client.get("/")

    assert response.status_code == 200
    assert 'href="/points"' in response.get_data(as_text=True)


def test_points_page_is_linked_from_welcome(simply_lift_client):
    response = simply_lift_client.post(
        "/showSummary",
        data={"email": "john@simplylift.co"},
    )

    assert response.status_code == 200
    assert 'href="/points"' in response.get_data(as_text=True)
