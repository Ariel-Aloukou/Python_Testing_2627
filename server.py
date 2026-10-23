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


app = Flask(__name__)
app.secret_key = 'something_special'
app.jinja_env.globals['is_competition_past'] = is_competition_past

competitions = loadCompetitions()
clubs = loadClubs()
bookings = {}


@app.route('/')
def index():
    return render_template('index.html')


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
    foundCompetition = [c for c in competitions if c['name'] == competition][0]
    logged_in_club = get_logged_in_club()
    if logged_in_club is None:
        return render_login_required()
    if logged_in_club['name'] != foundClub['name']:
        flash("Accès non autorisé pour ce club.")
        return render_template(
            'welcome.html',
            club=logged_in_club,
            competitions=competitions,
        ), 403
    if is_competition_past(foundCompetition):
        flash("Cette compétition est passée.")
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
        flash("Accès non autorisé pour ce club.")
        return render_template(
            'welcome.html',
            club=club,
            competitions=competitions,
        ), 403
    competition = [
        c for c in competitions if c['name'] == request.form['competition']
    ][0]
    if is_competition_past(competition):
        flash("Cette compétition est passée.")
        return render_template(
            'welcome.html',
            club=club,
            competitions=competitions,
        )
    placesRequired = int(request.form['places'])
    if placesRequired < 1:
        flash("Le nombre de places doit être au moins 1.")
        return render_template(
            'welcome.html',
            club=club,
            competitions=competitions,
        )
    booked_places = get_booked_places(club['name'], competition['name'])
    if booked_places + placesRequired > MAX_PLACES_PER_COMPETITION:
        flash("La limite de 12 places par compétition est dépassée.")
        return render_template(
            'welcome.html',
            club=club,
            competitions=competitions,
        )
    if placesRequired > int(competition['numberOfPlaces']):
        flash("Capacité insuffisante pour cette réservation.")
        return render_template(
            'welcome.html',
            club=club,
            competitions=competitions,
        )
    if not debit_club_points(club, placesRequired):
        flash("Solde de points insuffisant pour cette réservation.")
        return render_template(
            'welcome.html',
            club=club,
            competitions=competitions,
        )
    decrement_competition_places(competition, placesRequired)
    bookings[(club['name'], competition['name'])] = (
        booked_places + placesRequired
    )
    flash('Great-booking complete!')
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
