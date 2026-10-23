def test_points_route_is_public(client):
    response = client.get("/points")

    assert response.status_code == 200
    assert b"Simply Lift" in response.data
    assert b"13" in response.data
    assert b"john@simplylift.co" not in response.data
