import server


def test_find_club_by_email_matches_an_existing_email(
    monkeypatch,
    sample_clubs,
):
    monkeypatch.setattr(server, "clubs", sample_clubs)

    club = server.find_club_by_email("john@simplylift.co")

    assert club is not None
    assert club["name"] == "Simply Lift"


def test_find_club_by_email_returns_none_for_unknown_email(
    monkeypatch,
    sample_clubs,
):
    monkeypatch.setattr(server, "clubs", sample_clubs)

    assert server.find_club_by_email("unknown@example.com") is None
