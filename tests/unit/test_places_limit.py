import server


def test_get_booked_places_returns_zero_for_unknown_booking(monkeypatch):
    monkeypatch.setattr(server, "bookings", {})

    assert server.get_booked_places("Simply Lift", "Spring Festival") == 0


def test_get_booked_places_returns_recorded_total(monkeypatch):
    monkeypatch.setattr(
        server,
        "bookings",
        {("Simply Lift", "Spring Festival"): 7},
    )

    assert server.get_booked_places("Simply Lift", "Spring Festival") == 7
