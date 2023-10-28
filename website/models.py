""" from . import db
from sqlalchemy.dialects.postgresql import UUID
import uuid
from flask_login import UserMixin
from sqlalchemy.sql import func

class Car(db.Model):
    id = db.Column(UUID(as_uuid=True), primary_key = True, default = uuid.uuid4)
    brand = db.Column(db.String(50))
    model = db.Column(db.String(50))
    car_num = db.Column(db.String(50))
    car_vin = db.Column(db.String(50))
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    description = db.Column(db.String(50))
    person_id = db.Column(UUID(as_uuid=True), db.ForeignKey('person.id'))
    status = db.Column(db.Boolean)

class LoginData(db.Model, UserMixin):
    id = db.Column(UUID(as_uuid=True), primary_key = True, default = uuid.uuid4)
    email = db.Column(db.String(50), db.ForeignKey('person.email'))
    password = db.Column(db.String(150))

class Person(db.Model, UserMixin):
    id = db.Column(UUID(as_uuid=True), primary_key=True, default = uuid.uuid4)
    name = db.Column(db.String(100))
    surname = db.Column(db.String(100))
    email = db.Column(db.String(50), unique=True)
    phone_number = db.Column(db.String(30))
    cars = db.relationship('Car')
 """