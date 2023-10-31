from flask import Blueprint, render_template, request, flash
from uuid import uuid4
from datetime import datetime
from .database import startWorkDB, endWrokDB
from .verification import login_required, admin_login_required, replace_special_chars

views = Blueprint('views', __name__)

@views.route('/')
@views.route('/home')
def home():
    return render_template("home.html")

@views.route('/new_client', methods = ['GET', 'POST'])
@admin_login_required
def new_client():
    now = datetime.now()
    now = now.strftime("%Y-%m-%d %H:%M:%S")
    if request.method == 'POST':
        k_id = replace_special_chars(str(uuid4()))
        c_id = replace_special_chars(str(uuid4()))
        k_name = replace_special_chars(request.form.get('client_name').upper())
        k_surname = replace_special_chars(request.form.get('client_surname').upper())
        k_email = replace_special_chars(request.form.get('client_email'))
        k_num = replace_special_chars(request.form.get('client_number').upper())
        c_brand = replace_special_chars(request.form.get('car_brand').upper())
        c_make = replace_special_chars(request.form.get('car_make').upper())
        c_num = replace_special_chars(request.form.get('car_number').upper())
        c_vin = replace_special_chars(request.form.get('car_vin').upper())
        c_desc = replace_special_chars(request.form.get('repair_specification'))

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
@admin_login_required
def all_users():
    return render_template("all_users.html")

@views.route('/pending_page')
@admin_login_required
def pending_page():
    car_data = []
    person_data = []
    try:
        conn, cur = startWorkDB()
        cur.execute("SELECT brand, model, carNum, carVin, date, id, person_id FROM car WHERE status = false")
        car_data = cur.fetchall()
        for row in car_data:
            person_id = row[6]
            cur.execute("SELECT name, surname, email, phoneNumber FROM person WHERE id = %s", (person_id,))
            person_data.append(cur.fetchone())
    
    except Exception as e:
        flash(f'Kaut kas nogāja greizi: {e}', category='error')

    finally:
        endWrokDB(conn)

    data = zip(person_data, car_data)

    return render_template("pending_page.html", data = data)

@views.route('/admin_home_161660')
@admin_login_required
def admin_home():
    return render_template("admin_home.html")

@views.route('/user_home')
@login_required
def user_home():
    return render_template("user_home.html")