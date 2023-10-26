from flask import Blueprint, render_template, request, flash
from uuid import uuid4
from datetime import datetime

views = Blueprint('views', __name__)

@views.route('/')
@views.route('/home')
def home():
    return render_template("home.html")

@views.route('/new_client', methods = ['GET', 'POST'])
def new_client():
    if request.method == 'POST':
        k_name = request.form.get('client_name')
        k_surname = request.form.get('client_surname')
        k_email = request.form.get('client_email')
        k_num = request.form.get('client_number')
        c_brand = request.form.get('car_brand')
        c_make = request.form.get('car_make')
        c_num = request.form.get('car_number')
        c_vin = request.form.get('car_vin')
        flash('Success', category='error')
        print("works")
        return render_template("new_client.html")
    else:
        now = datetime.now()
        now = now.strftime("%Y-%m-%d %H:%M:%S")
        return render_template("new_client.html", date=now)

@views.route('/pending_page')
def pending_page():

    fixID = uuid4()
    return render_template("pending_page.html", fixID=fixID)

@views.route('/admin_home_161660')
def admin_home():
    return render_template("admin_home.html")