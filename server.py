import json

from flask import Flask, flash, redirect, render_template, request, url_for


MAX_PLACES_PER_COMPETITION = 12


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


def find_club_by_email(email):
    normalized_email = normalize_email(email)
    if not normalized_email:
        return None
    for club in clubs:
        if normalize_email(club.get('email')) == normalized_email:
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


app = Flask(__name__)
app.secret_key = 'something_special'

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

    return render_template('welcome.html', club=club, competitions=competitions)


@app.route('/book/<competition>/<club>')
def book(competition, club):
    foundClub = [c for c in clubs if c['name'] == club][0]
    foundCompetition = [c for c in competitions if c['name'] == competition][0]
    if foundClub and foundCompetition:
        return render_template(
            'booking.html',
            club=foundClub,
            competition=foundCompetition,
        )
    else:
        flash("Something went wrong-please try again")
        return render_template(
            'welcome.html',
            club=club,
            competitions=competitions,
        )


@app.route('/purchasePlaces', methods=['POST'])
def purchasePlaces():
    competition = [
        c for c in competitions if c['name'] == request.form['competition']
    ][0]
    club = [c for c in clubs if c['name'] == request.form['club']][0]
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
    return redirect(url_for('index'))
