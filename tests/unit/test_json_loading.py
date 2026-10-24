import json

import server


def test_load_clubs_raises_when_file_missing(monkeypatch, tmp_path):
    monkeypatch.setattr(server, "CLUBS_FILE", tmp_path / "missing.json")
    try:
        server.loadClubs()
    except FileNotFoundError as exc:
        assert "Fichier de données introuvable" in str(exc)
    else:
        assert False


def test_load_competitions_raises_when_file_missing(monkeypatch, tmp_path):
    monkeypatch.setattr(server, "COMPETITIONS_FILE", tmp_path / "missing.json")
    try:
        server.loadCompetitions()
    except FileNotFoundError as exc:
        assert "Fichier de données introuvable" in str(exc)
    else:
        assert False


def test_load_clubs_raises_when_json_invalid(monkeypatch, tmp_path):
    path = tmp_path / "clubs.json"
    path.write_text("{")
    monkeypatch.setattr(server, "CLUBS_FILE", path)
    try:
        server.loadClubs()
    except ValueError as exc:
        assert "JSON invalide" in str(exc)
    else:
        assert False


def test_load_competitions_raises_when_json_invalid(monkeypatch, tmp_path):
    path = tmp_path / "competitions.json"
    path.write_text("{")
    monkeypatch.setattr(server, "COMPETITIONS_FILE", path)
    try:
        server.loadCompetitions()
    except ValueError as exc:
        assert "JSON invalide" in str(exc)
    else:
        assert False


def test_load_clubs_raises_when_schema_invalid(monkeypatch, tmp_path):
    path = tmp_path / "clubs.json"
    path.write_text(json.dumps({"clubs": [{"name": "x"}]}))
    monkeypatch.setattr(server, "CLUBS_FILE", path)
    try:
        server.loadClubs()
    except ValueError as exc:
        assert "Schéma invalide" in str(exc)
    else:
        assert False


def test_load_competitions_raises_when_schema_invalid(monkeypatch, tmp_path):
    path = tmp_path / "competitions.json"
    path.write_text(json.dumps({"competitions": [{"name": "x"}]}))
    monkeypatch.setattr(server, "COMPETITIONS_FILE", path)
    try:
        server.loadCompetitions()
    except ValueError as exc:
        assert "Schéma invalide" in str(exc)
    else:
        assert False


def test_load_clubs_raises_when_not_dict(monkeypatch, tmp_path):
    path = tmp_path / "clubs.json"
    path.write_text(json.dumps([]))
    monkeypatch.setattr(server, "CLUBS_FILE", path)
    try:
        server.loadClubs()
    except ValueError as exc:
        assert "Schéma invalide" in str(exc)
    else:
        assert False


def test_load_clubs_raises_when_clubs_not_list(monkeypatch, tmp_path):
    path = tmp_path / "clubs.json"
    path.write_text(json.dumps({"clubs": {}}))
    monkeypatch.setattr(server, "CLUBS_FILE", path)
    try:
        server.loadClubs()
    except ValueError as exc:
        assert "Schéma invalide" in str(exc)
    else:
        assert False


def test_load_clubs_raises_when_club_not_dict(monkeypatch, tmp_path):
    path = tmp_path / "clubs.json"
    path.write_text(json.dumps({"clubs": ["x"]}))
    monkeypatch.setattr(server, "CLUBS_FILE", path)
    try:
        server.loadClubs()
    except ValueError as exc:
        assert "Schéma invalide" in str(exc)
    else:
        assert False


def test_load_competitions_raises_when_not_dict(monkeypatch, tmp_path):
    path = tmp_path / "competitions.json"
    path.write_text(json.dumps([]))
    monkeypatch.setattr(server, "COMPETITIONS_FILE", path)
    try:
        server.loadCompetitions()
    except ValueError as exc:
        assert "Schéma invalide" in str(exc)
    else:
        assert False


def test_load_competitions_raises_when_competitions_not_list(monkeypatch, tmp_path):
    path = tmp_path / "competitions.json"
    path.write_text(json.dumps({"competitions": {}}))
    monkeypatch.setattr(server, "COMPETITIONS_FILE", path)
    try:
        server.loadCompetitions()
    except ValueError as exc:
        assert "Schéma invalide" in str(exc)
    else:
        assert False


def test_load_competitions_raises_when_competition_not_dict(monkeypatch, tmp_path):
    path = tmp_path / "competitions.json"
    path.write_text(json.dumps({"competitions": ["x"]}))
    monkeypatch.setattr(server, "COMPETITIONS_FILE", path)
    try:
        server.loadCompetitions()
    except ValueError as exc:
        assert "Schéma invalide" in str(exc)
    else:
        assert False


def test_load_bookings_raises_when_json_invalid(monkeypatch, tmp_path):
    path = tmp_path / "bookings.json"
    path.write_text("{")
    monkeypatch.setattr(server, "BOOKINGS_FILE", path)
    try:
        server.loadBookings()
    except ValueError as exc:
        assert "JSON invalide" in str(exc)
    else:
        assert False


def test_load_bookings_raises_when_not_dict(monkeypatch, tmp_path):
    path = tmp_path / "bookings.json"
    path.write_text(json.dumps([]))
    monkeypatch.setattr(server, "BOOKINGS_FILE", path)
    try:
        server.loadBookings()
    except ValueError as exc:
        assert "Schéma invalide" in str(exc)
    else:
        assert False


def test_load_bookings_raises_when_bookings_not_list(monkeypatch, tmp_path):
    path = tmp_path / "bookings.json"
    path.write_text(json.dumps({"bookings": {}}))
    monkeypatch.setattr(server, "BOOKINGS_FILE", path)
    try:
        server.loadBookings()
    except ValueError as exc:
        assert "Schéma invalide" in str(exc)
    else:
        assert False


def test_load_bookings_raises_when_booking_not_dict(monkeypatch, tmp_path):
    path = tmp_path / "bookings.json"
    path.write_text(json.dumps({"bookings": ["x"]}))
    monkeypatch.setattr(server, "BOOKINGS_FILE", path)
    try:
        server.loadBookings()
    except ValueError as exc:
        assert "Schéma invalide" in str(exc)
    else:
        assert False


def test_load_bookings_returns_empty_when_key_missing(monkeypatch, tmp_path):
    path = tmp_path / "bookings.json"
    path.write_text(json.dumps({}))
    monkeypatch.setattr(server, "BOOKINGS_FILE", path)
    assert server.loadBookings() == {}


def test_load_bookings_raises_when_schema_invalid(monkeypatch, tmp_path):
    path = tmp_path / "bookings.json"
    path.write_text(json.dumps({"bookings": [{"club": "x"}]}))
    monkeypatch.setattr(server, "BOOKINGS_FILE", path)
    try:
        server.loadBookings()
    except ValueError as exc:
        assert "Schéma invalide" in str(exc)
    else:
        assert False
