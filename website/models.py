
# models.py
# Importing necessary modules
from . import db
from flask_login import UserMixin
from sqlalchemy import text
from sqlalchemy import Table, Column, Integer, ForeignKey
from sqlalchemy.orm import relationship

# User class representing the User table in the database
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(255), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(255))
    location = db.Column(db.String(255))
    role = db.Column(db.String(50), default='user')
    permission = db.Column(db.String(50), default='blacklist')

# Playlist class representing the Playlist table in the database
class Playlist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(255), nullable=False)

    # Define relationship with Song table
    songs = db.relationship('Song', backref='playlist', lazy=True)

# Song class representing the Song table in the database
class Song(db.Model):
    Songid = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Song_name = db.Column(db.String, nullable=False)
    Song_Lyrics = db.Column(db.String, nullable=False)
    Song_Artist = db.Column(db.String, nullable=False)
    Song_genre = db.Column(db.String, nullable=False)
    Song_rating = db.Column(db.Float, default=0)  # Change to Float for more precise average
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    album_id = db.Column(db.Integer, db.ForeignKey('album.album_id'))
    flag = db.Column(db.String, default='green')
    playlist_id = db.Column(db.Integer, db.ForeignKey('playlist.id'))

    # Define relationship with Rating table
    ratings = db.relationship('Rating', backref='song', lazy=True)

# Rating class representing the Rating table in the database
class Rating(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    song_id = db.Column(db.Integer, db.ForeignKey('song.Songid'))
    rating = db.Column(db.Float, default=0.0)

# Album class representing the Album table in the database
class Album(db.Model):
    album_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    album_title = db.Column(db.String(255))
    album_artist = db.Column(db.String, db.ForeignKey('user.username'), nullable=False)
    # Define relationship with Song table
    songs = db.relationship('Song', backref='album', lazy=True)
    flag = db.Column(db.String, default='green')


