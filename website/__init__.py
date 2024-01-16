# __init__.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager

# Create SQLAlchemy and LoginManager instances
db = SQLAlchemy()
login_manager = LoginManager()

# Database name
DB_NAME = "database.db"

# Function to create the Flask app
def create_app():
    # Initialize the Flask app
    app = Flask(__name__, static_url_path='/static', static_folder='static')
    
    # Secret key for securing the app
    app.config['SECRET_KEY'] = 'hjshjhdjah kjshkjdhjs'
    
    # Database configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    db.init_app(app)

    # Importing views, auth, and models blueprints
    
    from .auth import auth
    from .models import User, Song, Album, Playlist

    # Register blueprints with the app
    
    app.register_blueprint(auth, url_prefix='/')
    
    # Create database tables within the app context
    with app.app_context():
        db.create_all()

    # Configure LoginManager
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    # User loader function for LoginManager
    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    return app




# Function to create the database
def create_database(app):
    if not path.exists('website/' + DB_NAME):
        db.create_all(app=app)
        print('Created Database!')
