def test_index_page_is_available(client):
    response = client.get("/")

    assert response.status_code == 200
    assert b"GUDLFT Registration" in response.data
