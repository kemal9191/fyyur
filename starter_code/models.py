from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
from sqlalchemy import ForeignKey, distinct

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------# 

class Venue(db.Model):
    __tablename__ = 'venues'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    genres = db.Column(db.ARRAY(db.String()), nullable=False)
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String(), nullable=False)
    seeking_talent = db.Column(db.Boolean(), default=False)
    seeking_description = db.Column(db.String(), nullable=False)
    shows = db.relationship('Show', backref='venue', lazy=True, cascade="all, delete-orphan")

# TODO: implement any missing fields, as a database migration using Flask-Migrate (DONE)

class Artist(db.Model):
    __tablename__ = 'artists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String(), nullable=False)
    seeking_venue = db.Column(db.Boolean(), default=False)
    seeking_description = db.Column(db.String(), nullable=False)
    shows = db.relationship('Show', backref='artist', lazy=True)


# TODO: implement any missing fields, as a database migration using Flask-Migrate (DONE)

class Show(db.Model):
    __tablename__ = 'shows'
    
    id = db.Column(db.Integer, primary_key=True)
    venue_id = db.Column(db.Integer, ForeignKey('venues.id'))
    artist_id = db.Column(db.Integer, ForeignKey('artists.id'))
    start_time = db.Column(db.DateTime, nullable=False)

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration (DONE).
