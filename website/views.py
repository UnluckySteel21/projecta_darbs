from flask import Blueprint, render_template

views = Blueprint('views', __name__)

@views.route('/')
@views.route('/home')
def home():
    return render_template("home.html")

@views.route('/new_client')
def new_client():
    return render_template("new_client.html")

@views.route('/admin_home_161660')
def admin_home():
    return render_template("admin_home.html")