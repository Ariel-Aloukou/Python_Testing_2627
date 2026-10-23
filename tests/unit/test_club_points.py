import server


def test_debit_club_points_subtracts_points():
    club = {"name": "Simply Lift", "points": "13"}

    assert server.debit_club_points(club, 2) is True
    assert club["points"] == "11"


def test_debit_club_points_refuses_insufficient_balance():
    club = {"name": "Iron Temple", "points": "4"}

    assert server.debit_club_points(club, 5) is False
    assert club["points"] == "4"


def test_debit_club_points_can_spend_all_points():
    club = {"name": "Iron Temple", "points": "4"}

    assert server.debit_club_points(club, 4) is True
    assert club["points"] == "0"
