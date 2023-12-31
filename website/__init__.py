from flask import Flask
from .config import Config
from .database import initializeDB

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix = '/')
    app.register_blueprint(auth, url_prefix = '/')

    initializeDB()

    return app