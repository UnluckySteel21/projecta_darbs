from flask import Blueprint, render_template, request, flash
from uuid import uuid4
from datetime import datetime
import psycopg2
from .database import startWorkDB, endWrokDB

views = Blueprint('views', __name__)

@views.route('/')
@views.route('/home')
def home():
    return render_template("home.html")

@views.route('/new_client', methods = ['GET', 'POST'])
def new_client():
    now = datetime.now()
    now = now.strftime("%Y-%m-%d %H:%M:%S")
    if request.method == 'POST':
        k_id = str(uuid4())
        c_id = str(uuid4())
        k_name = request.form.get('client_name')
        k_surname = request.form.get('client_surname')
        k_email = request.form.get('client_email')
        k_num = request.form.get('client_number')
        c_brand = request.form.get('car_brand')
        c_make = request.form.get('car_make')
        c_num = request.form.get('car_number')
        c_vin = request.form.get('car_vin')
        c_desc = request.form.get('repair_specification')

        try:
            conn, cur = startWorkDB()
            cur.execute("SELECT * FROM person WHERE email LIKE %s", (k_email, ))
            dataPerson = cur.fetchone()
            if dataPerson != None:
                try:
                    cur.execute("""INSERT
                                INTO car (id, brand, model, carNum, carVin, date, description, person_id, status)
                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                                """, (c_id, c_brand, c_make, c_num, c_vin, now, c_desc, dataPerson[0], "no"))
                    
                    flash('Klients veiksmīgi pievonts!', category='succes')
            
                except Exception as e:
                    flash(f'Kaut kas nogāja greizi: {e}', category='error')

            else:
                try:
                    cur.execute("""INSERT 
                                INTO person (id, name, surname, email, phoneNumber) 
                                VALUES (%s, %s, %s, %s, %s)
                                """, (k_id, k_name, k_surname, k_email, k_num))
            
                    cur.execute("""INSERT
                                INTO car (id, brand, model, carNum, carVin, date, description, person_id, status)
                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                                """, (c_id, c_brand, c_make, c_num, c_vin, now, c_desc, k_id, "no"))

                    flash('Klients veiksmīgi pievonts!', category='succes')
            
                except Exception as e:
                    flash(f'Kaut kas nogāja greizi: {e}', category='error')

        except Exception as e:
            flash(f'Kaut kas nogāja greizi: {e}', category='error')
        
        finally:
            endWrokDB(conn)

        return render_template("new_client.html")
    else:
        
        return render_template("new_client.html", date=now)
    
@views.route('/all_users')
def all_users():
    return render_template("all_users.html")

@views.route('/pending_page')
def pending_page():

    fixID = uuid4()
    return render_template("pending_page.html", fixID=fixID)

@views.route('/admin_home_161660')
def admin_home():
    return render_template("admin_home.html")

@views.route('/user_home')
def user_home():
    return render_template("user_home.html")