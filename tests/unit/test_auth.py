import server


def test_normalize_email_trims_spaces_and_lowercases():
    assert server.normalize_email("  John@SimplyLift.CO  ") == (
        "john@simplylift.co"
    )


def test_normalize_email_handles_none_and_empty_values():
    assert server.normalize_email(None) == ""
    assert server.normalize_email("   ") == ""


def test_find_club_by_email_matches_an_existing_email(
    monkeypatch,
    sample_clubs,
):
    monkeypatch.setattr(server, "clubs", sample_clubs)

    club = server.find_club_by_email("john@simplylift.co")

    assert club is not None
    assert club["name"] == "Simply Lift"


def test_find_club_by_email_matches_case_insensitively(
    monkeypatch,
    sample_clubs,
):
    monkeypatch.setattr(server, "clubs", sample_clubs)

    club = server.find_club_by_email("  JOHN@SIMPLYLIFT.CO ")

    assert club is not None
    assert club["name"] == "Simply Lift"


def test_find_club_by_email_returns_none_for_unknown_email(
    monkeypatch,
    sample_clubs,
):
    monkeypatch.setattr(server, "clubs", sample_clubs)

    assert server.find_club_by_email("unknown@example.com") is None


def test_find_club_by_email_returns_none_for_empty_email(
    monkeypatch,
    sample_clubs,
):
    monkeypatch.setattr(server, "clubs", sample_clubs)

    assert server.find_club_by_email("   ") is None
