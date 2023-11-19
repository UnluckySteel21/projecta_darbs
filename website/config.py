"""FLASK CONFIG"""

from os import environ, path
from dotenv import load_dotenv

basedir = path.abspath(path.dirname(__file__))
load_dotenv(path.join(basedir, ".env"))

class Config:
    SECRET_KEY = environ.get("SECRET_KEY")
    MAINTENANCE_MODE = True if environ.get('MAINTENANCE_MODE') == 'True' else False
    FLASK_ENV = environ.get("FLASK_ENV")
    RECAPTCHA_ENABLED = True
    RECAPTCHA_SITE_KEY = environ.get("RECAPTCHA_SITE_KEY")
    RECAPTCHA_SECRET_KEY = environ.get("RECAPTCHA_SECRET_KEY")

class DevConfig(Config):
    ...

class ProConfig(Config):
    ...