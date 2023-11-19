from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from uuid import uuid4
from datetime import datetime
from .database import startWorkDB, endWorkDB
from .verification import login_required, admin_login_required, sanitize_and_replace
from .viewsFunctions import get_users, get_pending_users, writeToDoc

views = Blueprint('views', __name__)

@views.route('/')
@views.route('/home')
def home():
    return render_template("home.html")

@views.route('/new_client', methods = ['GET', 'POST'])
@admin_login_required
def new_client():
    # Fetching time and date
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if request.method == 'POST':
        # Sanitizing user input and making it mostly uppercase for easier search function
        k_id = sanitize_and_replace(str(uuid4()))  # Generate a unique ID
        c_id = sanitize_and_replace(str(uuid4()))  # Generate a unique ID
        k_name = sanitize_and_replace(request.form.get('client_name').upper())
        k_surname = sanitize_and_replace(request.form.get('client_surname').upper())
        k_email = sanitize_and_replace(request.form.get('client_email'))
        k_num = sanitize_and_replace(request.form.get('client_number').upper())
        c_brand = sanitize_and_replace(request.form.get('car_brand').upper())
        c_make = sanitize_and_replace(request.form.get('car_make').upper())
        c_num = sanitize_and_replace(request.form.get('car_number').upper())
        c_vin = sanitize_and_replace(request.form.get('car_vin').upper())
        c_desc = sanitize_and_replace(request.form.get('repair_specification'))

        try:
            conn, cur = startWorkDB()
            cur.execute("SELECT * FROM person WHERE email LIKE %s", (k_email, ))
            dataPerson = cur.fetchone()

            if dataPerson != None:
                try:
                    cur.execute("""INSERT INTO car 
                                (id, brand, model, carNum, carVin, date, description, person_id, status)
                                VALUES
                                (%s, %s, %s, %s, %s, %s, %s, %s, %s)""", 
                                (c_id, c_brand, c_make, c_num, c_vin, now, c_desc, dataPerson[0], "0"))
                    cur.execute("""UPDATE person
                                SET name = %s, surname = %s, phoneNumber = %s
                                WHERE email LIKE %s""",
                                (k_name, k_surname, k_num, k_email))
                    flash('Klients veiksmīgi pievonts!', category='succes')
                except Exception as e:
                    flash('Kaut kas nogāja greizi', category='error')
                    writeToDoc(e)
            else:
                try:
                    cur.execute("""INSERT INTO person
                                (id, name, surname, email, phoneNumber, admin)
                                VALUES
                                (%s, %s, %s, %s, %s, %s)""",
                                (k_id, k_name, k_surname, k_email, k_num, "0"))
                    cur.execute("""INSERT INTO car 
                                (id, brand, model, carNum, carVin, date, description, person_id, status)
                                VALUES
                                (%s, %s, %s, %s, %s, %s, %s, %s, %s)""", 
                                (c_id, c_brand, c_make, c_num, c_vin, now, c_desc, k_id, "0"))
                    flash('Klients veiksmīgi pievonts!', category='succes')
                except Exception as e:
                    flash('Kaut kas nogāja greizi', category='error')
                    writeToDoc(e)
        except Exception as e:
            flash('Kaut kas nogāja greizi', category='error')
            writeToDoc(e)
        finally:
            endWorkDB(conn)

        return render_template("new_client.html")
    else:
        return render_template("new_client.html", date=now)
    
@views.route('/all_users')
@admin_login_required
def all_users():
    data = get_users()
    return render_template("all_users.html", data=data)

@views.route('/search_users')
@admin_login_required
def search_users():
    search_field = request.args.get('search_field', None)
    search_value = request.args.get('search_value', None)
    data = get_users(search_field, search_value)
    return render_template("all_users.html", data=data)

@views.route('/pending_page', methods=['GET'])
@admin_login_required
def pending_page():
    # Get search parameters from the request
    search_field = request.args.get('search_field', None)
    search_value = request.args.get('search_value', None)

    data = get_pending_users(search_field, search_value)
    return render_template("pending_page.html", data=data)

@views.route('/delete_car', methods=['POST'])
@admin_login_required
def delete_car():
    """
    Deletes a car record from the database.
    This operation is only possible if the car status is false.
    """
    car_id = request.form.get('car_id')

    try:
        conn, cur = startWorkDB()
        cur.execute("DELETE FROM car WHERE id = %s", (car_id,))
        conn.commit()
        flash('Ieraksts veiksmīgi dzēsts', category='success')

    except Exception as e:
        flash('Kaut kas nogāja greizi', category='error')
        writeToDoc(e)

    finally:
        endWorkDB(conn)

    return redirect(url_for('views.pending_page'))

@views.route('/update_car_status', methods=['POST'])
@admin_login_required
def update_car_status():
    """
    Updates car status from false (work unfinished) to true (work finished).
    This operation is triggered by a button click.
    """
    car_id = request.form.get('car_id')

    try:
        conn, cur = startWorkDB()
        cur.execute("UPDATE car SET status = true WHERE id = %s", (car_id,))
        conn.commit()

    except Exception as e:
        flash('Kaut kas nogāja greizi!', category='error')
        writeToDoc(e)

    finally:
        endWorkDB(conn)

    return redirect(url_for('views.pending_page'))

@views.route('/admin_home_161660')
@admin_login_required
def admin_home():
    return render_template("admin_home.html")

@views.route('/user_home')
@login_required
def user_home():
    """
    Fetches and displays the cars associated with the logged-in user.
    """
    user_id = session.get('user_id')
    cars = []

    if user_id:
        try:
            conn, cur = startWorkDB()

            # Fetch the cars associated with the user
            cur.execute("SELECT * FROM car WHERE person_id = %s ORDER BY date DESC", (user_id,))
            cars = cur.fetchall()

        except Exception as e:
            flash('Kaut kas nogāja greizi!', category='error')
            writeToDoc(e)

        finally:
            endWorkDB(conn)

    else:
        flash('Lietotājs nav atrasts', category='error')
        return redirect(url_for("auth.login"))

    return render_template("user_home.html", cars=cars)

@views.route('/notes', methods=['GET', 'POST'])
@login_required
def notes():
    return render_template("user_notes.html")

@views.route('/reservation', methods = ['GET', 'POST'])
@login_required
def reservation():    
    return render_template("user_reservation.html")

@views.after_request
def apply_caching(response):
    # me trying to stop XSS (i dont know what im doing)
    response.headers["X-Content-Type-Options"] = "nosniff" # Yeah! Dont sniff. Thats weird
    response.headers["X-XSS-Protection"] = "1; mode=block"
    return response