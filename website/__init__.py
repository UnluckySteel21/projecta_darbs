from flask import Flask
from .config import Config
from flask_sqlalchemy import SQLAlchemy
from .database import initializeDB
#from os import path

""" db = SQLAlchemy()
DB_NAME = "database.db" """

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    #db.init_app(app)

    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix = '/')
    app.register_blueprint(auth, url_prefix = '/')

    #from .models import Person, Car, LoginData

    initializeDB()

    return app

""" def create_database(app):
    if not path.exists('website/' + DB_NAME):
        db.create_all(app=app) """