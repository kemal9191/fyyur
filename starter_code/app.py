#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
from re import I
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from sqlalchemy import ForeignKey, distinct
from forms import *
import datetime
from flask_migrate import Migrate
from models import Venue, Show, Artist

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

migrate = Migrate(app, db)

# TODO: connect to a local postgresql database (DONE)


#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  if isinstance(value, str):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format="EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format="EE MM, dd, y h:mma"
  else:
    date = value
    if format == 'full':
        format="EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format="EE MM, dd, y h:mma"
    
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#------------------------------------------------------------------#
#  Venues
#  ----------------------------------------------------------------#

@app.route('/venues')
def venues():
  # TODO (DONE): replace with real venues data.
  # num_upcoming_shows should be aggregated based on number of upcoming shows per venue. 


  locations = db.session.query(distinct(Venue.city), Venue.state).all()
  today = datetime.datetime.now()
  data = []

  try:
    for location in locations:
      city = location[0]
      state = location[1]
      location_data = {
        "city": city,
        "state": state,
        "venues": []
      }

      venues = Venue.query.filter_by(city=city, state=state).all()

      for venue in venues:
        upcoming_shows = (Show.query.filter_by(venue_id=venue.id).filter(Show.start_time>today).all())
        venue_data = {
          "id": venue.id,
          "name": venue.name,
          "num_upcoming_shows": len(upcoming_shows)
        }
        location_data["venues"].append(venue_data)

      data.append(location_data)

  except:
    db.session.rollback()
    flash("Something is wrong, please try again later!")
    return render_template("pages.home.html")
  finally:
    return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO (DONE): implement search on venues with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"

  search_term = request.form.get("search_term", "")
  results = Venue.query.filter(Venue.name.ilike(f"%{search_term}%")).all()
  data = []

  for result in results:
    data.append({
      "id":result.id,
      "name":result.name,
      "num_upcoming_shows": len(Show.query.filter(Show.venue_id==result.id).filter(Show.start_time> datetime.datetime.now()).all())
    })
  
  response={
    "count": len(results),
    "data": data
  }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO (DONE): replace with real venue data from the venues table, using venue_id
  venue = Venue.query.filter(Venue.id==venue_id).first()
  past_shows = []
  upcoming_shows = []
  shows = Show.query.filter(Show.venue_id==venue_id).all()
  today = datetime.datetime.now()
  for show in shows:
    show_data = {
      "artist_id": show.artist.id,
      "artist_name": show.artist.name,
      "artist_image_link": show.artist.image_link,
      "start_time": str(show.start_time)
    }
    if (show.start_time>today):
      upcoming_shows.append(show_data)
    
    if (show.start_time<today):
      past_shows.append(show_data)


  data = {
    "id": venue.id,
    "name": venue.name,
    "genres": venue.genres,
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website": venue.website_link,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description": venue.seeking_description,
    "image_link": venue.image_link,
    "past_shows": past_shows,
    "upcoming_shows":upcoming_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows),
  }

  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  form = VenueForm(request.form)
  if form.validate_on_submit():
    genres = form.genres.data
    name = form.name.data
    city = form.city.data
    state = form.state.data
    address = form.address.data
    phone = form.phone.data
    image_link = form.image_link.data
    facebook_link = form.facebook_link.data
    website_link = form.website_link.data
    seeking_talent = form.seeking_talent.data
    seeking_description = form.seeking_description.data
    venue = Venue(name=name, city=city, state=state, address=address, phone=phone,
            image_link=image_link, genres=genres, facebook_link=facebook_link, 
            website_link=website_link, seeking_talent=seeking_talent,
            seeking_description=seeking_description)
    db.session.add(venue)
    db.session.commit()
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  else:
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
    db.session.rollback()
  return render_template('pages/home.html')

  # TODO (DONE): insert form data as a new Venue record in the db, instead
  # TODO (DONE): modify data to be the data object returned from db insertion

  # on successful db insert, flash success
  # TODO (DONE): on unsuccessful db insert, flash an error instead.
  # e.g., 
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/ 

@app.route('/venues/<venue_id>/delete', methods=['DELETE', 'POST', 'GET'])
def delete_venue(venue_id):
  try:
    venue = db.session.query(Venue).get(venue_id)
    db.session.delete(venue)
    db.session.commit()
    flash('Venue is succesfully deleted')
  except:
    db.session.rollback()
    flash('This venue cannot be deleted')
  finally:
    return render_template('pages/home.html')
  # TODO (DONE): Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage (DONE)

#------------------------------------------------------------------
#  Artists
#------------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO (DONE): replace with real data returned from querying the database
  raw_data = Artist.query.all()
  data=[]
  for item in raw_data:
    data.append({
      "id":item.id,
      "name":item.name
    })
  
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO (DONE): implement search on artists with partial string search. Ensure it is case-insensitive.
  # search for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band" 
  search_term=request.form.get("search_term", "")
  results = Artist.query.filter(Artist.name.ilike(f"%{search_term}%")).all()
  data = []

  for result in results:
    data.append({
      "id": result.id,
      "name": result.name,
      "num_upcoming_shows":len(Show.query.filter(Show.artist_id==result.id).filter(Show.start_time>datetime.datetime.now()).all())
    })

  response={
    "count": len(results),
    "data": data
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO (DONE): replace with real artist data from the artist table, using artist_id
  artist = db.session.query(Artist).get(artist_id)
  shows = Show.query.filter(Show.artist_id==artist_id).all()
  today = datetime.datetime.now()
  past_shows=[]
  upcoming_shows=[]

  for show in shows:
    venue = db.session.query(Venue).get(show.venue_id)
    show_data = {
      "venue_id": show.venue_id,
      "venue_name":venue.name,
      "venue_image_link":venue.image_link,
      "start_time":show.start_time
    }
    if (show.start_time>today):
      upcoming_shows.append(show_data)
    else:
      past_shows.append(show_data)

  data={
    "id": artist.id,
    "name": artist.name,
    "genres": artist.genres,
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website": artist.website_link,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.seeking_venue,
    "seeking_description": artist.seeking_description,
    "image_link": artist.image_link,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows),
  }
  
  return render_template('pages/show_artist.html', artist=data)

#------------------------------------------------------------------
#  Update
#------------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = db.session.query(Artist).get(artist_id)
  artist_data={
    "id": artist.id,
    "name": artist.name,
    "genres": artist.genres,
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website": artist.website_link,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.seeking_venue,
    "seeking_description": artist.seeking_description,
    "image_link": artist.image_link
  }

  form.name.data = artist.name
  form.city.data = artist.city
  form.state.data = artist.state
  form.phone.data = artist.phone
  form.image_link.data = artist.image_link
  form.genres.data = artist.genres
  form.facebook_link.data = artist.facebook_link
  form.website_link.data = artist.website_link
  form.seeking_venue.data = artist.seeking_venue
  form.seeking_description.data = artist.seeking_description
  return render_template('forms/edit_artist.html', form=form, artist=artist_data)

  # TODO (DONE): populate form with fields from artist with ID <artist_id>


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  form = ArtistForm(request.form)
  artist = db.session.query(Artist).get(artist_id)
  
  artist.name = form.name.data
  artist.city = form.city.data
  artist.state = form.state.data
  artist.phone = form.phone.data
  artist.image_link = form.image_link.data
  artist.genres = form.genres.data
  artist.facebook_link = form.facebook_link.data
  artist.website_link = form.website_link.data
  artist.seekin_venue = form.seeking_venue.data
  artist.seeking_decription = form.seeking_description.data

  db.session.add(artist)
  db.session.commit()
  return redirect(url_for('show_artist', artist_id=artist_id))

  # TODO (DONE): take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue= db.session.query(Venue).get(venue_id)
  venue_data={
    "id": venue.id,
    "name": venue.name,
    "genres": venue.genres,
    "city": venue.city,
    "state": venue.state,
    "address": venue.address,
    "phone": venue.phone,
    "website": venue.website_link,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description": venue.seeking_description,
    "image_link": venue.image_link
  }

  form.name.data = venue.name
  form.city.data = venue.city
  form.state.data = venue.state
  form.phone.data = venue.phone
  form.address.data = venue.address
  form.image_link.data = venue.image_link
  form.genres.data = venue.genres
  form.facebook_link.data = venue.facebook_link
  form.website_link.data = venue.website_link
  form.seeking_talent.data = venue.seeking_talent
  form.seeking_description.data = venue.seeking_description
  return render_template('forms/edit_venue.html', form=form, venue=venue_data)

  # TODO (DONE): populate form with values from venue with ID <venue_id>

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  form = VenueForm(request.form)
  venue = db.session.query(Venue).get(venue_id)
  venue.name = form.name.data
  venue.city = form.city.data
  venue.state = form.state.data
  venue.address = form.address.data
  venue.phone = form.phone.data
  venue.image_link = form.image_link.data
  venue.genres = form.genres.data
  venue.facebook_link = form.facebook_link.data
  venue.website_link = form.website_link.data
  venue.seeking_talent = form.seeking_talent.data
  venue.seekin_description = form.seeking_description.data

  db.session.add(venue)
  db.session.commit()
  return redirect(url_for('show_venue', venue_id=venue_id))

  # TODO (DONE): take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes

#------------------------------------------------------------------
#  Create Artist
#------------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO (DONE): insert form data as a new Venue record in the db, instead
  # TODO (DONE): modify data to be the data object returned from db insertion
  # on successful db insert, flash success
  form = ArtistForm(request.form)
  try:
    artist = Artist(name=form.name.data, city=form.city.data, state=form.state.data,
                    phone=form.phone.data, image_link=form.image_link.data, 
                    genres=form.genres.data, facebook_link=form.facebook_link.data,
                    website_link=form.website_link.data, seeking_venue=form.seeking_venue.data,
                    seeking_description=form.seeking_description.data)
    db.session.add(artist)
    db.session.commit()
    flash('Artist ' + request.form['name'] + ' was successfully listed!')

  except:
    db.session.rollback()
    flash('Artist ' + request.form['name'] + ' cannot be listed!')
  finally:
    db.session.close()
    return render_template('pages/home.html')
  # TODO (DONE): on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')

#------------------------------------------------------------------
#  Shows
#------------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO (DONE): replace with real venues data.

  raw_data = Show.query.all()
  data = []
  for item in raw_data:
    venue = db.session.query(Venue).get(item.venue_id)
    artist = db.session.query(Artist).get(item.artist_id)
    data_item = {
      "venue_id": venue.id,
      "venue_name": venue.name,
      "artist_id":artist.id,
      "artist_name":artist.name,
      "artist_image_link":artist.image_link,
      "start_time":item.start_time
    }
    data.append(data_item)

  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  form =ShowForm(request.form)
  # called to create new shows in the db, upon submitting new show listing form
  # TODO (DONE): insert form data as a new Show record in the db, instead
  try:
    show = Show(artist_id=form.artist_id.data, venue_id=form.venue_id.data, 
                start_time=form.start_time.data)
    db.session.add(show)
    db.session.commit()
    flash('Show was successfully listed!')
  except:
    db.session.rollback()
    flash('An error occurred. Show could not be listed.')
  finally:
    db.session.close()
    return render_template('pages/home.html')

  # on successful db insert, flash success
  # TODO (DONE): on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
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
