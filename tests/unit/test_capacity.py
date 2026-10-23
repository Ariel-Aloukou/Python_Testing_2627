import server


def test_decrement_competition_places_subtracts_places():
    competition = {"numberOfPlaces": "5"}

    server.decrement_competition_places(competition, 2)

    assert competition["numberOfPlaces"] == 3


def test_decrement_competition_places_never_goes_negative():
    competition = {"numberOfPlaces": "5"}

    server.decrement_competition_places(competition, 6)

    assert competition["numberOfPlaces"] == 0
