import json

from datetime import datetime

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


def loadClubs():
    with open('clubs.json') as c:
        listOfClubs = json.load(c)['clubs']
        return listOfClubs


def loadCompetitions():
    with open('competitions.json') as comps:
        listOfCompetitions = json.load(comps)['competitions']
        return listOfCompetitions


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
bookings = {}


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/points')
def points():
    return {
        'clubs': [
            {
                'name': club['name'],
                'points': int(club['points']),
            }
            for club in clubs
        ]
    }


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
    booked_places = get_booked_places(club['name'], competition['name'])
    if booked_places + placesRequired > MAX_PLACES_PER_COMPETITION:
        flash_error("La limite de 12 places par compétition est dépassée.")
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
    bookings[(club['name'], competition['name'])] = (
        booked_places + placesRequired
    )
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
