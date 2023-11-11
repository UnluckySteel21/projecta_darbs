from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from uuid import uuid4
from datetime import datetime
from .database import startWorkDB, endWorkDB
from .verification import login_required, admin_login_required, sanitize_and_replace, writeToDoc

views = Blueprint('views', __name__)

@views.route('/')
@views.route('/home')
def home():
    return render_template("home.html")

@views.route('/new_client', methods = ['GET', 'POST'])
@admin_login_required
def new_client():
    #New client insertion into database
    #fetching time and date
    now = datetime.now()
    now = now.strftime("%Y-%m-%d %H:%M:%S")
    if request.method == 'POST':
        #sanitizing user input and making it mostly uppercase for easier search funtion
        k_id = sanitize_and_replace(str(uuid4()))
        c_id = sanitize_and_replace(str(uuid4()))
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
            #all this in a try so website keeps running if there is a database failure.
            conn, cur = startWorkDB()
            cur.execute("SELECT * FROM person WHERE email LIKE %s", (k_email, ))
            dataPerson = cur.fetchone()
            if dataPerson != None:
                try:
                    cur.execute("""INSERT
                                INTO car (id, brand, model, carNum, carVin, date, description, person_id, status)
                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                                """, (c_id, c_brand, c_make, c_num, c_vin, now, c_desc, dataPerson[0], "0"))
                    
                    flash('Klients veiksmīgi pievonts!', category='succes')
            
                except Exception as e:
                    flash('Kaut kas nogāja greizi', category='error')
                    writeToDoc(e)

            else:
                try:
                    cur.execute("""INSERT 
                                INTO person (id, name, surname, email, phoneNumber) 
                                VALUES (%s, %s, %s, %s, %s)
                                """, (k_id, k_name, k_surname, k_email, k_num))
            
                    cur.execute("""INSERT
                                INTO car (id, brand, model, carNum, carVin, date, description, person_id, status)
                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                                """, (c_id, c_brand, c_make, c_num, c_vin, now, c_desc, k_id, "0"))

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
    # shows all users in the database
    # Mapping form values to database column names (trying to prevent sql injections)
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
    if search_field is not None:
        if search_field in column_mapping:
            search_field = column_mapping[search_field]
        else:
            flash('Nepareizs ievades lauks', category='error')
            return redirect(url_for('views.all_users'))

    if search_value != None:
        search_value = sanitize_and_replace(search_value.upper())
    
    data = []
    try:
        #allat in a try so the webiste keeps running 
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
        flash('Kaut kas nogāja greizi', category='error')
        writeToDoc(e)

    finally:
        endWorkDB(conn)

    return render_template("all_users.html", data=data)

@views.route('/pending_page', methods=['GET'])
@admin_login_required
def pending_page():
    # Mapping form values to database column names (trying to prevent sql injections)
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

    # Get search parameters from the request
    search_field = request.args.get('search_field', None)
    search_value = request.args.get('search_value', None)

    # Initialize query and params
    query = """SELECT person.name, person.surname, person.email, person.phoneNumber, 
               car.brand, car.model, car.carNum, car.carVin, car.id, car.date, car.status, car.description 
               FROM person 
               INNER JOIN car ON person.id = car.person_id
               WHERE car.status = false"""
    params = []

    # Check if the search field exists in the column mapping
    if search_field is not None:
        if search_field in column_mapping:
            search_field = column_mapping[search_field]
            if search_value is not None:
                search_value = sanitize_and_replace(search_value.upper())
                query += f" AND {search_field} LIKE %s"
                params.append(f"%{search_value}%")
        else:
            flash('Nepareizs ievades lauks', category='error')
            return redirect(url_for('views.all_users'))

    try:
        # Try so the website keeps running 
        conn, cur = startWorkDB()

        # Add ORDER BY clause to the query
        query += " ORDER BY car.date DESC"
        cur.execute(query, params)

        # Fetch data
        data = cur.fetchall()

    except Exception as e:
        flash('An error occurred', category='error')
        writeToDoc(e)
        data = []

    finally:
        endWorkDB(conn)

    return render_template("pending_page.html", data=data)

@views.route('/delete_car', methods=['POST'])
@admin_login_required
def delete_car():
    # deletes a row from the database (possible only if status is false)
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
    # reddirect from button. Updates car status from false (work unfinished) to true (work finished)
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
    user_id = session.get('user_id')
    cars = []
    
    if user_id:
        try:
            conn, cur = startWorkDB()

            # Query to retrieve the user's ID based on their email from the logindata table
            cur.execute("SELECT person.id FROM person JOIN logindata ON person.email = logindata.email WHERE logindata.id = %s", (user_id,))
            
            user_data = cur.fetchone()
            if user_data:
                user_id = user_data[0]  # Update user_id with the retrieved user's ID

                # Now, you can use the updated user_id to fetch the cars associated with the user
                cur.execute("SELECT * FROM car WHERE person_id = %s ORDER BY date DESC", (user_id,))
                cars = cur.fetchall()
            else:
                flash('Lietotājs nav atrasts!', category='error')
                return redirect(url_for("auth.login"))

        except Exception as e:
            flash('Kaut kas nogāja greizi!', category='error')
            writeToDoc(e)

        finally:
            endWorkDB(conn)

    else:
        flash('Lietotāja ID nav atrasts sesijā!', category='error')
        return redirect(url_for("auth.login"))

    return render_template("user_home.html", cars=cars)

@views.after_request
def apply_caching(response):
    # me trying to stop XSS (i dont know what im doing)
    response.headers["X-Content-Type-Options"] = "nosniff" # Yeah! Dont sniff. Thats weird
    response.headers["X-XSS-Protection"] = "1; mode=block"
    return response