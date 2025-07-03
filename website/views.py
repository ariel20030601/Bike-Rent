from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from .models import Bike, User, RentalHistory
from . import db
from datetime import datetime, timedelta

views = Blueprint("views", __name__)

@views.route("/")
@login_required
def home():
    bikes = Bike.query.all()
    return render_template("home.html", user=current_user, bikes=bikes)

@views.route("/profile")
@login_required
def profile():
    user_rentals = current_user.rentals
    owned_bikes = {r.bike for r in user_rentals}
    return render_template("profile.html", user=current_user, user_rentals=user_rentals, owned_bikes=owned_bikes, now=datetime.utcnow())

@views.route("/extend_rental/<int:rental_id>", methods=['POST'])
@login_required
def extend_rental(rental_id):
    rental = RentalHistory.query.get_or_404(rental_id)
    days = int(request.form.get('days', 0))
    cost = days * rental.bike.rental_price

    if current_user.balance < cost:
        flash("Insufficient balance to extend", "error")
        return redirect(url_for('views.profile'))

    current_user.balance -= cost
    rental.return_date += timedelta(days=days)
    rental.payment += cost
    db.session.commit()

    flash("Rental extended successfully", "success")
    return redirect(url_for('views.profile'))

@views.route("/add-balance", methods=['POST'])
@login_required
def add_balance():
    amount = request.form.get('amount', type=float)
    current_user.balance += amount
    db.session.commit()
    flash(f"Balance updated successfully! New balance: ${current_user.balance}", "success")
    return redirect(url_for('views.profile'))

@views.route("/edit_profile", methods=['POST'])
@login_required
def edit_profile():
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        password2 = request.form.get('password2')
        if not name or not email:
            flash("Name and email are required", "error")
            return redirect(url_for('views.profile'))
        if password and password != password2:  
            flash("Passwords do not match", "error")
            return redirect(url_for('views.profile'))
        current_user.name = name
        current_user.email = email
        current_user.password = password if password else current_user.password
        db.session.commit()
        flash("Profile updated successfully", "success")
        return redirect(url_for('views.profile'))

@views.route("/Bikes/<bike_name>", methods=['GET', 'POST'])
@login_required
def bike_details(bike_name):
    if request.method == 'POST':
        days = request.form.get('days')
        user_id = current_user.id
        bike = Bike.query.filter_by(name=bike_name).first()
        payment = bike.rental_price * int(days)
        if (current_user.balance < payment):
            flash("Insufficient balance to rent this bike.", category="error")
            return redirect(url_for('views.bike_details', bike_name=bike_name))
        current_user.balance -= payment
        bike_id = bike.id
        rental = RentalHistory(user_id=user_id, bike_id=bike_id, payment=payment, rental_date=datetime.utcnow(), return_date=datetime.utcnow() + timedelta(days=int(days)))
        bike.available = False
        db.session.add(rental)
        db.session.commit()
        flash("Bike rented successfully!", category="success")
        return redirect(url_for('views.home'))

    bike = Bike.query.filter_by(name=bike_name).first()
    if bike:
        return render_template("bike_details.html", user=current_user, bike=bike)
    else:
        flash("Bike not found.", category="error")

@views.route("/manage-bikes")
@login_required
def manage_bikes():
    bikes = Bike.query.all()
    return render_template("bikes_manage.html", user=current_user, bikes=bikes)

@views.route("/delete_bike/<int:bike_id>", methods=['POST'])
@login_required
def delete_bike(bike_id):
    bike = Bike.query.get_or_404(bike_id)
    if bike.available:
        db.session.delete(bike)
        db.session.commit()
        flash("Bike deleted successfully", "success")
        return redirect(url_for('views.manage_bikes'))
    else:
        flash("Cannot delete a rented bike", "error")
        return redirect(url_for('views.manage_bikes'))

@views.route("/modify_bike/<int:bike_id>", methods=['GET', 'POST'])
@login_required
def modify_bike(bike_id):
    bike = Bike.query.get_or_404(bike_id)
    if request.method == 'POST':
        bike.name = request.form.get('name')
        bike.Manufacturer = request.form.get('manufacturer')
        bike.Description = request.form.get('description')        
        bike.rental_price = request.form.get('rental_price', type=float)
        db.session.commit()
        flash("Bike details updated successfully", "success")
        return redirect(url_for('views.manage_bikes'))
    
@views.route("/about")
def about():
    return render_template("AboutUs.html", user=current_user)

@views.route("/contact", methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        message = request.form.get('message')
        if not name or not email or not message:
            flash("All fields are required", "error")
            return redirect(url_for('views.contact'))
        # Here you would typically send the message via email or store it
        flash("Message sent successfully!", "success")
        return redirect(url_for('views.contact'))
    return render_template("ContactUs.html", user=current_user)