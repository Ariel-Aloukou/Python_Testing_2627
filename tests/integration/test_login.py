def test_valid_email_logs_in(client):
    response = client.post(
        "/showSummary",
        data={"email": "john@simplylift.co"},
    )

    assert response.status_code == 200
    assert b"Welcome, john@simplylift.co" in response.data
    assert b"Points available: 13" in response.data


def test_unknown_email_shows_an_error_instead_of_crashing(client):
    response = client.post(
        "/showSummary",
        data={"email": "unknown@example.com"},
    )

    assert response.status_code == 200
    assert b"Adresse email inconnue" in response.data
    assert b"Welcome," not in response.data


def test_missing_email_field_shows_an_error(client):
    response = client.post("/showSummary", data={})

    assert response.status_code == 200
    assert b"Adresse email inconnue" in response.data
