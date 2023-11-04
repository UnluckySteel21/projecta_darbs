from flask import Blueprint, render_template, request, flash, redirect, url_for
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
    # Mapping form values to database column names
    column_mapping = {
        "name": "person.name",
        "surname": "person.surname",
        "phoneNumber": "person.phoneNumber",
        "brand": "car.brand",
        "model": "car.model",
        "carNum": "car.carNum",
        "carVin": "car.carVin",
        "date": "car.date"
    }

    search_field = request.args.get('search_field', None)
    search_value = request.args.get('search_value', None)

    # Check if the search field exists in the column mapping
    if search_field in column_mapping:
        search_field = column_mapping[search_field]
    else:
        flash('Nepareizs ievades lauks', category='error')
        return redirect(url_for('views.all_users'))

    if search_value != None:
        search_value = replace_special_chars(search_value.upper())
    
    data = []
    try:
        conn, cur = startWorkDB()

        if search_field and search_value:
            query = f"""SELECT person.name, person.surname, person.email, person.phoneNumber, 
                       car.brand, car.model, car.carNum, car.carVin, car.id, car.date, car.status, car.description
                       FROM person 
                       INNER JOIN car ON person.id = car.person_id
                       WHERE {search_field} LIKE %s
                       ORDER BY car.date DESC"""
            cur.execute(query, (f"%{search_value}%",))
        else:
            query = """SELECT person.name, person.surname, person.email, person.phoneNumber, 
                       car.brand, car.model, car.carNum, car.carVin, car.id, car.date, car.status, car.description 
                       FROM person 
                       INNER JOIN car ON person.id = car.person_id
                       ORDER BY car.date DESC"""
            cur.execute(query)

        data = cur.fetchall()

    except Exception as e:
        flash(f'Kaut kas nogāja greizi: {e}', category='error')

    finally:
        endWrokDB(conn)

    return render_template("all_users.html", data=data)

@views.route('/pending_page', methods = ['GET'])
@admin_login_required
def pending_page():
    # Mapping form values to database column names
    column_mapping = {
        "name": "person.name",
        "surname": "person.surname",
        "phoneNumber": "person.phoneNumber",
        "brand": "car.brand",
        "model": "car.model",
        "carNum": "car.carNum",
        "carVin": "car.carVin",
        "date": "car.date"
    }

    search_field = request.args.get('search_field', None)
    search_value = request.args.get('search_value', None)

    # Check if the search field exists in the column mapping
    if search_field in column_mapping:
        search_field = column_mapping[search_field]
    else:
        flash('Invalid search field', category='error')
        return redirect(url_for('pending_page'))

    if search_value != None:
        search_value = replace_special_chars(search_value.upper())
    
    data = []
    try:
        conn, cur = startWorkDB()

        if search_field and search_value:
            query = f"""SELECT person.name, person.surname, person.email, person.phoneNumber, 
                       car.brand, car.model, car.carNum, car.carVin, car.id, car.date, car.status, car.description
                       FROM person 
                       INNER JOIN car ON person.id = car.person_id
                       WHERE {search_field} LIKE %s AND car.status = false
                       ORDER BY car.date DESC"""
            cur.execute(query, (f"%{search_value}%",))
        else:
            query = """SELECT person.name, person.surname, person.email, person.phoneNumber, 
                       car.brand, car.model, car.carNum, car.carVin, car.id, car.date, car.status, car.description 
                       FROM person 
                       INNER JOIN car ON person.id = car.person_id
                       WHERE car.status = false
                       ORDER BY car.date DESC"""
            cur.execute(query)

        data = cur.fetchall()

    except Exception as e:
        flash(f'Kaut kas nogāja greizi: {e}', category='error')

    finally:
        endWrokDB(conn)

    return render_template("pending_page.html", data = data)

@views.route('/delete_car', methods=['POST'])
def delete_car():
    car_id = request.form.get('car_id')
    try:
        conn, cur = startWorkDB()
        cur.execute("DELETE FROM car WHERE id = %s", (car_id,))
        conn.commit()
        flash('Ieraksts veiksmīgi dzēsts', category='success')
    except Exception as e:
        flash(f'Kaut kas nogāja greizi: {e}', category='error')
    finally:
        endWrokDB(conn)
    return redirect(url_for('views.pending_page'))

@views.route('/update_car_status', methods=['POST'])
@admin_login_required
def update_car_status():
    car_id = request.form.get('car_id')

    try:
        conn, cur = startWorkDB()
        cur.execute("UPDATE car SET status = true WHERE id = %s", (car_id,))
        conn.commit()
    except Exception as e:
        flash(f'Something went wrong: {e}', category='error')
    finally:
        endWrokDB(conn)

    return redirect(url_for('views.pending_page'))

@views.route('/admin_home_161660')
@admin_login_required
def admin_home():
    return render_template("admin_home.html")

@views.route('/user_home')
@login_required
def user_home():
    return render_template("user_home.html")