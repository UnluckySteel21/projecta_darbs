"""FLASK CONFIG"""

from os import environ, path
from dotenv import load_dotenv

basedir = path.abspath(path.dirname(__file__))
load_dotenv(path.join(basedir, ".env"))

class Config:
    SECRET_KEY = environ.get("SECRET_KEY")
    if environ.get('MAINTENANCE_MODE') == 'True':
        MAINTENANCE_MODE = True
    else:
        MAINTENANCE_MODE = False
    FLASK_ENV = environ.get("FLASK_ENV")

class DevConfig(Config):
    ...

class ProConfig(Config):
    ...