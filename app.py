#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, jsonify
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from sqlalchemy.dialects.postgresql import JSON

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migreate = Migrate(app, db)

# DONE: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(JSON)
    seeking_talent = db.Column(db.Boolean, nullable=False, default=False)
    seeking_description = db.Column(db.String(120))
    website = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    shows = db.relationship('Show', backref='venue', lazy=True)

    def get_venue(self):
        return {
        'id' : self.id,
        'name': self.name
        }

class Artist(db.Model):
    __tablename__ = 'Artist'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(JSON)
    seeking_venue = db.Column(db.Boolean, nullable=False, default=False)
    seeking_description = db.Column(db.String(120))
    website = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    shows = db.relationship('Show', backref='artist', lazy=True)

class Show(db.Model):
    __tablename__ = 'Show'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable = False)


    # DONE: implement any missing fields, as a database migration using Flask-Migrate

# DONE Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#


def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format)


app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#


@app.route('/')
def index():
    return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
    # DONE: replace with real venues data.
    #       num_shows should be aggregated based on number of upcoming shows per venue.
    areas = Venue.query.distinct('city', 'state').all();
    venues_list = []
    for area in areas:
      venues = Venue.query.filter(Venue.city == area.city, Venue.state == area.state).all()
      record = {
        'city': area.city,
        'state': area.state,
        'venues': [venue.get_venue() for venue in venues],
      }
      venues_list.append(record)
    return render_template('pages/venues.html', areas=venues_list)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    # DONE: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
    search_term = request.form.get('search_term')
    search_results =  Venue.query.filter(Venue.name.ilike('%{}%'.format(search_term))).all()
    response = {
        "count": len(search_results),
        "data": search_results
        }
    return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # shows the venue page with the given venue_id
    # DONE: replace with real venue data from the venues table, using venue_id
    venue = Venue.query.get(venue_id)
    past_shows = []
    upcoming_shows = []
    for show in venue.shows:
        if show.start_time < datetime.now():
            past_shows.append({
            'artist_id': show.artist_id,
            'artist_name': show.artist.name,
            'artist_image_link': show.artist.image_link,
            'start_time': str(show.start_time)
            })
        else:
            upcoming_shows.append({
            'artist_id': show.artist_id,
            'artist_name': show.artist.name,
            'artist_image_link': show.artist.image_link,
            'start_time': str(show.start_time)
            })

    venue_dic = {
        'id': venue.id,
        'name': venue.name,
        'genres': venue.genres,
        'address': venue.address,
        'city': venue.city,
        'state': venue.state,
        'phone': venue.phone,
        'website': venue.website,
        'facebook_link': venue.facebook_link,
        'seeking_talent': venue.seeking_talent,
        'seeking_description': venue.seeking_description,
        'image_link': venue.image_link,
        'past_shows': past_shows,
        'upcoming_shows': upcoming_shows,
        'past_shows_count': len(past_shows),
        'upcoming_shows_count': len(upcoming_shows)
    }

    return render_template('pages/show_venue.html', venue=venue_dic)

#  Create Venue
#  ----------------------------------------------------------------


@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    # DONE: insert form data as a new Venue record in the db, instead
    # DONE: modify data to be the data object returned from db insertion
    error = False
    try:
        name = request.form['name']
        city = request.form['city']
        state = request.form['state']
        address = request.form['address']
        phone = request.form['phone']
        genres = request.form.getlist('genres')
        if 'seeking_talent' in request.form:
            seeking_talent = True
        else:
            seeking_talent = False
        seeking_description = request.form['seeking_description']
        website = request.form['website']
        image_link = request.form['image_link']
        facebook_link = request.form['facebook_link']
        venue = Venue(name=name, city=city, state=state, address=address, phone=phone, genres=genres, seeking_talent=seeking_talent, seeking_description=seeking_description, website=website, image_link=image_link, facebook_link=facebook_link)
        db.session.add(venue)
        db.session.commit()
    except:
        db.session.rollback()
    finally:
        db.session.close()
        if error:
            # DONE: on unsuccessful db insert, flash an error instead.
            flash('An error occurred. Venue ' +
                  name + ' could not be listed.')
            return render_template('pages/home.html')
        if not error:
            flash('Venue ' + name + ' was successfully listed!')
            return render_template('pages/home.html')
        else:
            abort(500)

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    # DONE: Complete this endpoint for taking a venue_id, and using
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

    try:
        Venue.query.filter_by(id=venue_id).delete()
        db.session.commit()
    except:
        db.session.rollback()
        return jsonify({ 'success': FALSE })
    finally:
        db.session.close()
    return jsonify({ 'success': True })


    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage


#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
    # DONE: replace with real data returned from querying the database
    artists = Artist.query.with_entities(Artist.id, Artist.name).all()
    return render_template('pages/artists.html', artists=artists)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    # DONE: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".
    search_term = request.form.get('search_term')
    search_results =  Artist.query.filter(Artist.name.ilike('%{}%'.format(search_term))).all()
    response = {
        "count": len(search_results),
        "data": search_results
    }

    return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # shows the artist page with the given venue_id
    # DONE: replace with real artist data from the artist table, using artist_id
    artist = Artist.query.get(artist_id)
    past_shows = []
    upcoming_shows = []
    for show in artist.shows:
        if show.start_time < datetime.now():
            past_shows.append({
            'venue_id': show.venue_id,
            'venue_name': show.venue.name,
            'venue_image_link': show.venue.image_link,
            'start_time': str(show.start_time)
            })
        else:
            upcoming_shows.append({
            'venue_id': show.venue_id,
            'venue_name': show.venue.name,
            'venue_image_link': show.venue.image_link,
            'start_time': str(show.start_time)
            })

    artist_dic = {
        'id': artist.id,
        'name': artist.name,
        'genres': artist.genres,
        'city': artist.city,
        'state': artist.state,
        'phone': artist.phone,
        'website': artist.website,
        'facebook_link': artist.facebook_link,
        'seeking_venue': artist.seeking_venue,
        'seeking_description': artist.seeking_description,
        'image_link': artist.image_link,
        'past_shows': past_shows,
        'upcoming_shows': upcoming_shows,
        'past_shows_count': len(past_shows),
        'upcoming_shows_count': len(upcoming_shows)
    }

    return render_template('pages/show_artist.html', artist=artist_dic)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm()
    artist = Artist.query.get(artist_id)
    form.name.data = artist.name
    form.city.data = artist.city
    form.state.data = artist.state
    form.phone.data = artist.phone
    form.genres.data = artist.genres
    form.seeking_venue.data = artist.seeking_venue
    form.seeking_description.data = artist.seeking_description
    form.website.data = artist.website
    form.image_link.data = artist.image_link
    form.facebook_link.data = artist.facebook_link
    # DONE: populate form with fields from artist with ID <artist_id>
    return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    # DONE: take values from the form submitted, and update existing
    # artist record with ID <artist_id> using the new attributes
    try:
        artist = Artist.query.get(artist_id)
        artist.name = request.form['name']
        artist.city = request.form['city']
        artist.state = request.form['state']
        artist.phone = request.form['phone']
        artist.genres = request.form.getlist('genres')
        if 'seeking_venue' in request.form:
            artist.seeking_venue = True
        else:
            artist.seeking_venue = False
        artist.seeking_description = request.form['seeking_description']
        artist.website = request.form['website']
        artist.image_link = request.form['image_link']
        artist.facebook_link = request.form['facebook_link']
        db.session.commit()
    except:
        db.session.rollback()
    finally:
        db.session.close()

    return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    print('edit_venue called')
    form = VenueForm()
    venue = Venue.query.get(venue_id)
    form.name.data = venue.name
    form.city.data = venue.city
    form.state.data = venue.state
    form.address.data = venue.address
    form.phone.data = venue.phone
    form.genres.data = venue.genres
    form.seeking_talent.data = venue.seeking_talent
    form.seeking_description.data = venue.seeking_description
    form.website.data = venue.website
    form.image_link.data = venue.image_link
    form.facebook_link.data = venue.facebook_link

    # DONE: populate form with values from venue with ID <venue_id>
    return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    # DONE: take values from the form submitted, and update existing
    # venue record with ID <venue_id> using the new attributes
    try:
        venue = Venue.query.get(venue_id)
        venue.name = request.form['name']
        venue.city = request.form['city']
        venue.state = request.form['state']
        venue.address = request.form['address']
        venue.phone = request.form['phone']
        venue.genres = request.form.getlist('genres')
        if 'seeking_talent' in request.form:
            venue.seeking_talent = True
        else:
            venue.seeking_talent = False
        venue.seeking_description = request.form['seeking_description']
        venue.website = request.form['website']
        venue.image_link = request.form['image_link']
        venue.facebook_link = request.form['facebook_link']
        db.session.commit()
    except:
        db.session.rollback()
    finally:
        db.session.close()

    return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------


@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    # called upon submitting the new artist listing form
    # DONE: insert form data as a new Venue record in the db, instead
    # DONE: modify data to be the data object returned from db insertion
    error = False
    try:
        name = request.form['name']
        city = request.form['city']
        state = request.form['state']
        phone = request.form['phone']
        genres = request.form.getlist('genres')
        if 'seeking_venue' in request.form:
            seeking_venue = True
        else:
            seeking_venue = False
        seeking_description = request.form['seeking_description']
        website = request.form['website']
        image_link = request.form['image_link']
        facebook_link = request.form['facebook_link']
        artist = Artist(name=name, city=city, state=state, phone=phone, genres=genres, seeking_venue=seeking_venue, seeking_description=seeking_description, website=website, image_link=image_link, facebook_link=facebook_link)
        db.session.add(artist)
        db.session.commit()
    except:
        db.session.rollback()
    finally:
        db.session.close()
        if error:
            # DONE: on unsuccessful db insert, flash an error instead.
            flash('An error occurred. Artist ' +
                  name + ' could not be listed.')
            return render_template('pages/home.html')
        if not error:
            flash('Artist ' + name + ' was successfully listed!')
            return render_template('pages/home.html')
        else:
            abort(500)

#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    # displays list of shows at /shows
    # DONE: replace with real venues data.
    #       num_shows should be aggregated based on number of upcoming shows per venue.

    shows = Show.query.order_by(Show.start_time).all()
    showlist = []
    for show in shows:
        showlist.append({
        'venue_id': show.venue_id,
        'venue_name': show.venue.name,
        'artist_id': show.artist_id,
        'artist_name': show.artist.name,
        'artist_image_link': show.artist.image_link,
        'start_time': str(show.start_time)
        })

    return render_template('pages/shows.html', shows=showlist)


@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    # called to create new shows in the db, upon submitting new show listing form
    # DONE: insert form data as a new Show record in the db, instead

    error = False
    try:
        artist_id = request.form['artist_id']
        venue_id = request.form['venue_id']
        start_time = request.form['start_time']

        if artist_id == '' or Artist.query.get(artist_id) == None:
            flash('An error occurred. Artist doesn\'t exist')
            return render_template('pages/home.html')

        if venue_id == '' or Venue.query.get(venue_id) == None:
            flash('An error occurred. Venue doesn\'t exist')
            return render_template('pages/home.html')

        print('about to commit')
        show = Show(start_time=start_time)
        artist = Artist.query.get(artist_id)
        venue = Venue.query.get(venue_id)
        show.artist = artist
        show.venue = venue
        db.session.add(show)
        db.session.commit()
    except:
        print('except')
        db.session.rollback()
    finally:
        db.session.close()
        if error:
            # DONE: on unsuccessful db insert, flash an error instead.
            flash('An error occurred. Show could not be listed.')
            return render_template('pages/home.html')
        if not error:
            flash('Show was successfully listed!')
            return render_template('pages/home.html')
        else:
            abort(500)

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
