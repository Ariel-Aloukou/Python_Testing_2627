import copy
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import server as server_module  # noqa: E402


SAMPLE_CLUBS = [
    {
        "name": "Simply Lift",
        "email": "john@simplylift.co",
        "points": "13",
    },
    {
        "name": "Iron Temple",
        "email": "admin@irontemple.com",
        "points": "4",
    },
    {
        "name": "She Lifts",
        "email": "kate@shelifts.co.uk",
        "points": "12",
    },
]

SAMPLE_COMPETITIONS = [
    {
        "name": "Spring Festival",
        "date": "2030-03-27 10:00:00",
        "numberOfPlaces": "25",
    },
    {
        "name": "Fall Classic",
        "date": "2030-10-22 13:30:00",
        "numberOfPlaces": "13",
    },
]


@pytest.fixture
def sample_clubs():
    return copy.deepcopy(SAMPLE_CLUBS)


@pytest.fixture
def sample_competitions():
    return copy.deepcopy(SAMPLE_COMPETITIONS)


@pytest.fixture
def app(monkeypatch, sample_clubs, sample_competitions):
    monkeypatch.setattr(server_module, "clubs", sample_clubs)
    monkeypatch.setattr(server_module, "competitions", sample_competitions)
    monkeypatch.setattr(server_module, "bookings", {})
    server_module.app.config.update(
        TESTING=True,
        SECRET_KEY="test-secret-key",
    )
    return server_module.app


@pytest.fixture
def client(app):
    return app.test_client()
