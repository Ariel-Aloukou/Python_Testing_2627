import server


def test_parse_places_accepts_positive_value():
    assert server.parse_places("2") == (2, None)


def test_parse_places_refuses_negative_value():
    assert server.parse_places("-1") == (
        None,
        "Le nombre de places doit être au moins 1.",
    )


def test_parse_places_refuses_zero():
    assert server.parse_places("0") == (
        None,
        "Le nombre de places doit être au moins 1.",
    )


def test_parse_places_refuses_non_numeric_value():
    assert server.parse_places("deux") == (
        None,
        "Le nombre de places doit être un nombre entier.",
    )
