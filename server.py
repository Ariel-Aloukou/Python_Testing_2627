import json
import os
import threading

from datetime import datetime
from functools import wraps

from flask import (
    Flask,
    abort,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)


MAX_PLACES_PER_COMPETITION = 12
COMPETITION_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
CLUBS_FILE = 'clubs.json'
COMPETITIONS_FILE = 'competitions.json'
BOOKINGS_FILE = 'bookings.json'
DATA_LOCK = threading.RLock()


def serialized(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        with DATA_LOCK:
            return func(*args, **kwargs)
    return wrapper


def loadClubs():
    try:
        with open(CLUBS_FILE) as c:
            data = json.load(c)
    except FileNotFoundError:
        raise FileNotFoundError(
            f"Fichier de données introuvable : {CLUBS_FILE}"
        )
    except json.JSONDecodeError as exc:
        raise ValueError(f"JSON invalide dans {CLUBS_FILE} : {exc}")
    if not isinstance(data, dict):
        raise ValueError(
            "Schéma invalide pour clubs.json : attendu un objet JSON."
        )
    listOfClubs = data.get('clubs')
    if not isinstance(listOfClubs, list):
        raise ValueError(
            "Schéma invalide pour clubs.json : 'clubs' doit être une liste."
        )
    for club in listOfClubs:
        if not isinstance(club, dict):
            raise ValueError(
                "Schéma invalide pour clubs.json : "
                "chaque club doit être un objet."
            )
        for key in ('name', 'email', 'points'):
            if key not in club:
                raise ValueError(
                    f"Schéma invalide pour clubs.json : champ '{key}' manquant."
                )
        try:
            points = int(club['points'])
        except (TypeError, ValueError):
            raise ValueError(
                "Schéma invalide pour clubs.json : "
                "'points' doit être un entier."
            )
        club['points'] = str(points)
    return listOfClubs


def loadCompetitions():
    try:
        with open(COMPETITIONS_FILE) as comps:
            data = json.load(comps)
    except FileNotFoundError:
        raise FileNotFoundError(
            f"Fichier de données introuvable : {COMPETITIONS_FILE}"
        )
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"JSON invalide dans {COMPETITIONS_FILE} : {exc}"
        )
    if not isinstance(data, dict):
        raise ValueError(
            "Schéma invalide pour competitions.json : attendu un objet JSON."
        )
    listOfCompetitions = data.get('competitions')
    if not isinstance(listOfCompetitions, list):
        raise ValueError(
            "Schéma invalide pour competitions.json : "
            "'competitions' doit être une liste."
        )
    for competition in listOfCompetitions:
        if not isinstance(competition, dict):
            raise ValueError(
                "Schéma invalide pour competitions.json : "
                "chaque compétition doit être un objet."
            )
        for key in ('name', 'date', 'numberOfPlaces'):
            if key not in competition:
                raise ValueError(
                    "Schéma invalide pour competitions.json : "
                    f"champ '{key}' manquant."
                )
        try:
            places = int(competition['numberOfPlaces'])
        except (TypeError, ValueError):
            raise ValueError(
                "Schéma invalide pour competitions.json : "
                "'numberOfPlaces' doit être un entier."
            )
        competition['numberOfPlaces'] = str(places)
    return listOfCompetitions


def loadBookings():
    try:
        with open(BOOKINGS_FILE) as b:
            data = json.load(b)
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError as exc:
        raise ValueError(f"JSON invalide dans {BOOKINGS_FILE} : {exc}")
    if not isinstance(data, dict):
        raise ValueError(
            "Schéma invalide pour bookings.json : attendu un objet JSON."
        )
    listOfBookings = data.get('bookings')
    if listOfBookings is None:
        return {}
    if not isinstance(listOfBookings, list):
        raise ValueError(
            "Schéma invalide pour bookings.json : "
            "'bookings' doit être une liste."
        )
    bookings_loaded = {}
    for booking in listOfBookings:
        if not isinstance(booking, dict):
            raise ValueError(
                "Schéma invalide pour bookings.json : "
                "chaque réservation doit être un objet."
            )
        for key in ('club', 'competition', 'places'):
            if key not in booking:
                raise ValueError(
                    f"Schéma invalide pour bookings.json : champ '{key}' manquant."
                )
        bookings_loaded[
            (booking['club'], booking['competition'])
        ] = int(booking['places'])
    return bookings_loaded


def writeJson(path, payload):
    temporary_path = f"{path}.tmp"
    with open(temporary_path, 'w') as file:
        json.dump(payload, file, indent=4)
    os.replace(temporary_path, path)


def saveBookings():
    payload = {
        'bookings': [
            {
                'club': club_name,
                'competition': competition_name,
                'places': places,
            }
            for (club_name, competition_name), places in bookings.items()
        ]
    }
    writeJson(BOOKINGS_FILE, payload)


def saveData():
    with DATA_LOCK:
        writeJson(CLUBS_FILE, {'clubs': clubs})
        writeJson(COMPETITIONS_FILE, {'competitions': competitions})
        saveBookings()


def normalize_email(email):
    return str(email or '').strip().lower()


def is_competition_past(competition, now=None):
    competition_date = datetime.strptime(
        competition['date'],
        COMPETITION_DATE_FORMAT,
    )
    current_time = now or datetime.now()
    return competition_date < current_time


def find_club_by_email(email):
    normalized_email = normalize_email(email)
    if not normalized_email:
        return None
    for club in clubs:
        if normalize_email(club.get('email')) == normalized_email:
            return club
    return None


def find_club_by_name(club_name):
    for club in clubs:
        if club['name'] == club_name:
            return club
    return None


def find_competition_by_name(competition_name):
    for competition in competitions:
        if competition['name'] == competition_name:
            return competition
    return None


def parse_places(value):
    try:
        places = int(value)
    except (TypeError, ValueError):
        return None, "Le nombre de places doit être un nombre entier."
    if places < 1:
        return None, "Le nombre de places doit être au moins 1."
    if places > MAX_PLACES_PER_COMPETITION:
        return None, (
            f"La limite de {MAX_PLACES_PER_COMPETITION} places "
            "par compétition est dépassée."
        )
    return places, None


def debit_club_points(club, places):
    current_points = int(club['points'])
    if current_points < places:
        return False
    club['points'] = str(current_points - places)
    return True


def get_booked_places(club_name, competition_name):
    return bookings.get((club_name, competition_name), 0)


def decrement_competition_places(competition, places):
    remaining_places = int(competition['numberOfPlaces']) - places
    competition['numberOfPlaces'] = max(0, remaining_places)


def get_logged_in_club():
    club_name = session.get('club_name')
    if not club_name:
        return None
    for club in clubs:
        if club['name'] == club_name:
            return club
    return None


def render_login_required():
    return render_template(
        'index.html',
        error="Veuillez vous connecter pour accéder à cette page.",
    ), 401


def flash_error(message):
    flash(message, 'error')


def flash_success(message):
    flash(message, 'success')


app = Flask(__name__)
app.secret_key = 'something_special'
app.jinja_env.globals['is_competition_past'] = is_competition_past

competitions = loadCompetitions()
clubs = loadClubs()
bookings = loadBookings()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/points')
def points():
    sorted_clubs = sorted(
        clubs,
        key=lambda club: (-int(club['points']), club['name']),
    )
    return render_template('points.html', clubs=sorted_clubs)


@app.route('/showSummary', methods=['POST'])
def showSummary():
    email = request.form.get('email', '')
    club = find_club_by_email(email)

    if club is None:
        if not normalize_email(email):
            error = "Veuillez saisir une adresse email."
        else:
            error = (
                "Adresse email inconnue. "
                "Vérifiez votre adresse et réessayez."
            )
        return render_template('index.html', error=error)

    session['club_name'] = club['name']
    return render_template('welcome.html', club=club, competitions=competitions)


@app.route('/book/<competition>/<club>')
def book(competition, club):
    foundClub = find_club_by_name(club)
    if foundClub is None:
        abort(404)
    foundCompetition = find_competition_by_name(competition)
    if foundCompetition is None:
        abort(404)
    logged_in_club = get_logged_in_club()
    if logged_in_club is None:
        return render_login_required()
    if logged_in_club['name'] != foundClub['name']:
        flash_error("Accès non autorisé pour ce club.")
        return render_template(
            'welcome.html',
            club=logged_in_club,
            competitions=competitions,
        ), 403
    if is_competition_past(foundCompetition):
        flash_error("Cette compétition est passée.")
        return render_template(
            'welcome.html',
            club=foundClub,
            competitions=competitions,
        )
    return render_template(
        'booking.html',
        club=foundClub,
        competition=foundCompetition,
    )


@app.route('/purchasePlaces', methods=['POST'])
@serialized
def purchasePlaces():
    club = get_logged_in_club()
    if club is None:
        return render_login_required()
    submitted_club = request.form.get('club')
    if submitted_club and submitted_club != club['name']:
        flash_error("Accès non autorisé pour ce club.")
        return render_template(
            'welcome.html',
            club=club,
            competitions=competitions,
        ), 403
    competition_name = request.form.get('competition')
    places_value = request.form.get('places')
    if not competition_name or not places_value:
        flash_error("Les champs du formulaire sont incomplets.")
        return render_template(
            'welcome.html',
            club=club,
            competitions=competitions,
        )
    competition = find_competition_by_name(competition_name)
    if competition is None:
        abort(404)
    if is_competition_past(competition):
        flash_error("Cette compétition est passée.")
        return render_template(
            'welcome.html',
            club=club,
            competitions=competitions,
        )
    placesRequired, places_error = parse_places(places_value)
    if places_error:
        flash_error(places_error)
        return render_template(
            'welcome.html',
            club=club,
            competitions=competitions,
        )
    if (club['name'], competition['name']) in bookings:
        flash_error("Vous avez déjà réservé cette compétition.")
        return render_template(
            'welcome.html',
            club=club,
            competitions=competitions,
        )
    if placesRequired > int(competition['numberOfPlaces']):
        flash_error("Capacité insuffisante pour cette réservation.")
        return render_template(
            'welcome.html',
            club=club,
            competitions=competitions,
        )
    if not debit_club_points(club, placesRequired):
        flash_error("Solde de points insuffisant pour cette réservation.")
        return render_template(
            'welcome.html',
            club=club,
            competitions=competitions,
        )
    decrement_competition_places(competition, placesRequired)
    bookings[(club['name'], competition['name'])] = placesRequired
    saveData()
    place_word = "place" if placesRequired == 1 else "places"
    flash_success(
        f"Réservation confirmée : {placesRequired} {place_word} "
        f"pour {competition['name']}."
    )
    return render_template(
        'welcome.html',
        club=club,
        competitions=competitions,
    )


# TODO: Add route for points display


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))
