from datetime import datetime

import server


def test_is_competition_past_for_an_old_date():
    competition = {"date": "2026-10-22 13:30:00"}
    now = datetime(2026, 10, 23, 12, 0, 0)

    assert server.is_competition_past(competition, now) is True


def test_is_competition_past_for_a_future_date():
    competition = {"date": "2026-10-24 13:30:00"}
    now = datetime(2026, 10, 23, 12, 0, 0)

    assert server.is_competition_past(competition, now) is False
