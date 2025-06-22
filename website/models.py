from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    username = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    balance = db.Column(db.Float, default=0.0)


class Bike(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), unique=True)
    Manufacturer = db.Column(db.String(150))
    Description = db.Column(db.String(500))
    image_url = db.Column(db.String(200))
    rental_price = db.Column(db.Float)
    available = db.Column(db.Boolean, default=True)

class RentalHistory(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    bike_id = db.Column(db.Integer, db.ForeignKey('bike.id'))
    payment = db.Column(db.Float)
    rental_date = db.Column(db.DateTime)
    return_date = db.Column(db.DateTime)
    
    user = db.relationship('User', backref='rentals')
    bike = db.relationship('Bike', backref='rentals')
       