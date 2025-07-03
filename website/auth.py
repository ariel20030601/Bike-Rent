from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User, Bike
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask_login import login_user, login_required, logout_user, current_user

auth = Blueprint('auth', __name__)

@auth.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()
        if user:
            if check_password_hash(user.password, password):
                flash('Logged in successfully!', category='success')
                login_user(user, remember=True)
                return redirect(url_for('views.home'))
            else:
                flash('Incorrect password, try again.', category='error')
        else:
            flash('Username does not exist.', category='error')

    return render_template("login.html")

@auth.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@auth.route("/add-bike", methods=['GET', 'POST'])
def add_bike():
    if request.method == 'POST':
        name = request.form.get('name')
        Manufacturer = request.form.get('manufacturer')
        Description = request.form.get('description')
        image_url = request.form.get('image_url')
        rental_price = request.form.get('rental_price')

        bike = Bike.query.filter_by(name=name).first()
        if bike:
            flash('Bike already exists.', category='error')
        else:
            new_bike = Bike(name=name, Manufacturer=Manufacturer, Description=Description, image_url=image_url, rental_price=rental_price, available=True)
            db.session.add(new_bike)
            db.session.commit()
            flash('Bike added successfully!', category='success')
            return redirect(url_for('views.home'))
        
    return render_template("bike_addition.html")


@auth.route("/sign-up", methods=['GET', 'POST'])
def register():
    if request.method =='POST':
        email = request.form.get('email')
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        if user:
            flash('email or username already exists.', category='error')
        elif len(email) < 4:
            flash('Email must be greater than 3 characters.', category='error')
        elif len(username) < 2:
            flash('Username must be greater than 1 character.', category='error')
        elif len(password) < 5:
            flash('Password must be greater than 4 character.', category='error')
        else:
            new_user = User(email=email, username=username, password=generate_password_hash(password, method='pbkdf2:sha256'))
            db.session.add(new_user)
            db.session.commit()
            flash('Account created!', category='success')
            return redirect(url_for('auth.login'))
        
    return render_template("sign_up.html")