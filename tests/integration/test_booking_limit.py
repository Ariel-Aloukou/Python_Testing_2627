def test_booking_form_limits_places_to_12(client):
    response = client.get("/book/Spring%20Festival/Simply%20Lift")

    assert response.status_code == 200
    assert b'max="12"' in response.data
