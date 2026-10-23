import server


def test_load_bookings_returns_empty_dict_when_file_is_missing(
    monkeypatch,
    tmp_path,
):
    monkeypatch.setattr(
        server,
        "BOOKINGS_FILE",
        tmp_path / "missing-bookings.json",
    )

    assert server.loadBookings() == {}
