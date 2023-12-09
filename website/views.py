from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from uuid import uuid4
from datetime import datetime
from .database import startWorkDB, endWorkDB
from .verification import login_required, admin_login_required, sanitize_and_replace
from .viewsFunctions import writeToDoc

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
            #Select all data from db where client with the correct email is
            cur.execute("SELECT id FROM Person WHERE email LIKE %s", (k_email, ))
            dataPerson = cur.fetchone()

            if dataPerson:
                #if there is a client with the email
                person_id = dataPerson[0]
                #check if client owns the car
                cur.execute("SELECT id FROM Car WHERE person_id = %s AND car_vin = %s", (person_id, c_vin))
                dataCar = cur.fetchone()

                if dataCar:
                    #if client does own the car
                    try:
                        cur.execute("""
                                INSERT INTO Repair 
                                (id, date, description, status, car_id)
                                VALUES
                                (%s, %s, %s, %s, %s)""",
                                (str(uuid4()), now, c_desc, "0", dataCar[0]))
                        
                        flash('Klients veiksmīgi pievonts!', category='succes')

                    except Exception as e:
                        flash('Kaut kas nogāja greizi', category='error')
                        writeToDoc(e)
                
                else:
                    #if client doesnt own the car
                    try:
                        #select all values from db with a provided vin number
                        cur.execute("SELECT id FROM Car WHERE car_vin = %s", (c_vin, ))
                        dataCar = cur.fetchone()

                        if dataCar:
                            #if there is a car with the vin number update the person_id in Car table.
                            cur.execute("""UPDATE Car
                                        SET person_id = %s
                                        WHERE car_vin = %s""",
                                        (person_id, c_vin))
                            
                            cur.execute("""
                                    INSERT INTO Repair 
                                    (id, date, description, status, car_id)
                                    VALUES
                                    (%s, %s, %s, %s, %s)""",
                                    (str(uuid4()), now, c_desc, "0", dataCar[0]))
                        
                        else:
                            #if no vin number found (aka new car)
                            car_id = str(uuid4())
                            cur.execute("""
                                    INSERT INTO Car
                                    (id, brand, model, car_num, car_vin, description, person_id)
                                    VALUES
                                    (%s, %s, %s, %s, %s, %s, %s)""",
                                    (car_id, c_brand, c_make, c_num, c_vin, " ", person_id))
                        
                            cur.execute("""
                                    INSERT INTO Repair 
                                    (id, date, description, status, car_id)
                                    VALUES
                                    (%s, %s, %s, %s, %s)""",
                                    (str(uuid4()), now, c_desc, "0", car_id))
                        
                    except Exception as e:
                        flash('Kaut kas nogāja greizi.', category='error')
                        writeToDoc(e)
                    
                    finally:
                        return redirect(url_for("views.new_client"))
            else:
                #no client found
                try:
                    #check if there is a car in db with the vin number
                    cur.execute("SELECT id FROM Car WHERE car_vin = %s", (c_vin, ))
                    dataCar = cur.fetchone()

                    cur.execute("""
                                INSERT INTO Person
                                (id, name, surname, email, phone_number)
                                VALUES
                                (%s, %s, %s, %s, %s)""",
                                (k_id, k_name, k_surname, k_email, k_num))

                    if dataCar:
                        #if there is a car with the vin
                        cur.execute("""UPDATE Car
                                    SET person_id = %s
                                    WHERE car_vin = %s""",
                                    (k_id, c_vin))
                        
                        cur.execute("""
                                INSERT INTO Repair 
                                (id, date, description, status, car_id)
                                VALUES
                                (%s, %s, %s, %s, %s)""",
                                (str(uuid4()), now, c_desc, "0", dataCar[0]))
                        
                    else:
                        #if no such vin is found (aka a new car)
                        car_id = str(uuid4())
                        cur.execute("""
                                INSERT INTO Car
                                (id, brand, model, car_num, car_vin, description, person_id)
                                VALUES
                                (%s, %s, %s, %s, %s, %s, %s)""",
                                (car_id, c_brand, c_make, c_num, c_vin, " ", k_id))
                    
                        cur.execute("""
                                INSERT INTO Repair 
                                (id, date, description, status, car_id)
                                VALUES
                                (%s, %s, %s, %s, %s)""",
                                (str(uuid4()), now, c_desc, "0", car_id))
                        
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
        "name": "Person.name",
        "surname": "Person.surname",
        "phoneNumber": "Person.phone_number",
        "brand": "Car.brand",
        "model": "Car.model",
        "carNum": "Car.car_num",
        "carVin": "Car.car_vin",
        "date": "Repair.date"
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
            query = f"""SELECT Person.name, Person.surname, Person.email, Person.phone_number, 
                       Car.brand, Car.model, Car.car_num, Car.car_vin, Car.id, Repair.date, Repair.status, Repair.description
                       FROM Person 
                       INNER JOIN Car ON Person.id = Car.person_id
                       INNER JOIN Repair ON Car.id = Repair.car_id
                       WHERE {search_field} LIKE %s
                       ORDER BY Repair.date DESC"""
            cur.execute(query, (f"%{search_value}%",))

        else:
            query = """SELECT Person.name, Person.surname, Person.email, Person.phone_number, 
                       Car.brand, Car.model, Car.car_num, Car.car_vin, Car.id, Repair.date, Repair.status, Repair.description 
                       FROM Person 
                       INNER JOIN Car ON Person.id = Car.person_id
                       INNER JOIN Repair ON Car.id = Repair.car_id
                       ORDER BY Repair.date DESC"""
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
        "name": "Person.name",
        "surname": "Person.surname",
        "phoneNumber": "Person.phone_number",
        "brand": "Car.brand",
        "model": "Car.model",
        "carNum": "Car.car_num",
        "carVin": "Car.car_vin",
        "date": "Repair.date"
    }

    # Get search parameters from the request
    search_field = request.args.get('search_field', None)
    search_value = request.args.get('search_value', None)

    # Initialize query and params
    query = """SELECT Person.name, Person.surname, Person.email, Person.phone_number, 
               Car.brand, Car.model, Car.car_num, Car.car_vin, Repair.id, Repair.date, Repair.status, Car.description
               FROM Person 
               INNER JOIN Car ON Person.id = Car.person_id
               INNER JOIN Repair ON Car.id = Repair.car_id
               WHERE Repair.status = false"""
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
        query += " ORDER BY Repair.date DESC"
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
    """
    Deletes a repair record from the database.
    This operation is only possible if the repair status is false.
    """
    repair_id = request.form.get('car_id')
    try:
        conn, cur = startWorkDB()
        cur.execute("DELETE FROM Repair WHERE id = %s", (repair_id,))
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
    repair_id = request.form.get('car_id')

    try:
        conn, cur = startWorkDB()
        cur.execute("UPDATE Repair SET status = true WHERE id = %s", (repair_id,))
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
            cur.execute("""
                SELECT DISTINCT
                    Car.brand,
                    Car.model,
                    Car.id,
                    Car.car_num
                FROM Car
                WHERE Car.person_id = %s
            """, (user_id,))
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

@views.route('/notes/<car_id>', methods=['GET', 'POST'])
@login_required
def notes(car_id):
    description = []

    if request.method == 'POST':
        try:
            descr = sanitize_and_replace(request.form.get("description"))
            conn, cur = startWorkDB()
            cur.execute("UPDATE Car SET description = %s WHERE id LIKE %s", (descr, car_id, ))
            flash("Ziņa veiksmīgi pievienota!", category='success')
        
        except Exception as e:
            writeToDoc(e)
            flash('Kaut kas nogāja greizi!', category='error')
            return redirect(url_for("views.user_home"))
        
        finally:
            endWorkDB(conn)
            return redirect(url_for("views.notes", car_id=car_id))
        
    else:
        try:
            conn, cur = startWorkDB()
            cur.execute("SELECT person_id FROM Car WHERE id = %s", (car_id,))
            carUser = cur.fetchone()

            if carUser[0] == session.get('user_id'):
                
                cur.execute("SELECT description FROM Car WHERE id = %s", (car_id,))
                description = cur.fetchone()
                return render_template("user_notes.html", description=description[0])

            else:
                flash('Šī mašīna nepieder jums!', category='error')

        except Exception as e:
            flash('Kaut kas nogāja greizi.', category='error')
            writeToDoc(e)

        finally:
            endWorkDB(conn)

        return redirect(url_for("views.user_home"))

@views.route('/car/<car_id>', methods = ['GET', 'POST'])
@login_required
def car_view(car_id):
    if request.method == 'POST':
        ...
    
    else:
        try:
            conn, cur = startWorkDB()
            cur.execute("SELECT person_id FROM Car WHERE id = %s", (car_id, ))
            carUser = cur.fetchone()
            cur.execute("SELECT * FROM Reservation WHERE car_id = %s", (car_id, ))
            checkReservation = cur.fetchall()
            cars = []

            if carUser[0] == session.get('user_id'):
                cur.execute("""
                    SELECT
                        Car.brand,
                        Car.model,
                        Repair.date,
                        Car.car_num,
                        Repair.status,
                        Repair.description,
                        Car.id
                    FROM Car
                    INNER JOIN Repair ON Car.id = Repair.car_id
                    WHERE Car.id = %s
                    ORDER BY Repair.date DESC
                """, (car_id, ))
                cars = cur.fetchall()

                return render_template("car_view.html", cars = cars, car_id=car_id, checkReservation=checkReservation)

            else:
                flash('Šī mašīna nepieder jums!', category='error')
                return redirect(url_for("views.user_home"))
            
        except Exception as e:
            flash('Kaut kas nogāja greizi!', category='error')
            writeToDoc(e)
            return redirect(url_for("views.user_home"))

        finally:
            endWorkDB(conn)

@views.route('/reservation/<car_id>', methods = ['GET', 'POST'])
@login_required
def reservation(car_id):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if request.method == 'POST':
        descr = request.form.get("description")

        try:
            conn, cur = startWorkDB()
            cur.execute("""INSERT INTO 
                        Reservation
                        (reservation_id, date, car_id, description)
                        VALUES (%s, %s, %s, %s)""", (str(uuid4()), now, car_id, descr))
            
            flash('Jūsu pieprasījums ir saņemts! Uzgaidiet līdz mēs kontaktēsimies ar jums par ērtu laiku.', category='success')
            return redirect(url_for("views.user_home"))
        
        except Exception as e:
            writeToDoc(e)
            flash('Kaut kas nogāja greizi!', category='error')
        
        finally: 
            endWorkDB(conn)
        
        return redirect(url_for("views.user_home"))

    else:
        try:
            conn, cur = startWorkDB()
            cur.execute("SELECT person_id FROM Car WHERE id = %s", (car_id, ))
            carUser = cur.fetchone()

            if carUser[0] == session.get('user_id'):
                cur.execute("SELECT * FROM Reservation WHERE car_id = %s", (car_id, ))
                carResev = cur.fetchall()

                if carResev:
                    flash('Mašīnai ir aktīva rezervācija! Lūdzu pacietīgi uzgaidiet, kamēr mēs ar jums sazināsimies!', category='error')
                    return redirect(url_for("views.user_home"))
                
                else:
                    return render_template("user_reservation.html", car_id = car_id)

        except Exception as e:
            writeToDoc(e)
            flash('Kaut kas nogāja greizi.', category='error')

        finally:
            endWorkDB(conn)
        
        return render_template("user_reservation.html")

@views.route('/reservation_cancel/<car_id>')
@login_required
def reservation_cancel(car_id):
    try:
        conn, cur = startWorkDB()
        cur.execute("SELECT person_id FROM Car WHERE id = %s", (car_id, ))
        carUser = cur.fetchone()

        if carUser[0] == session.get('user_id'):
            cur.execute("DELETE FROM Reservation WHERE car_id = %s", (car_id, ))

    except Exception as e:
        writeToDoc(e)
        flash('Kaut kas nogāja greizi!', category='error')
    
    finally:
        endWorkDB(conn)
        return redirect(url_for("views.user_home"))

@views.route('/view_reservations')
@admin_login_required
def view_reservations():
    try:
        conn, cur = startWorkDB()
        cur.execute("""
                    SELECT
                        Reservation.reservation_id, 
                        Reservation.date,
                        Reservation.description,
                        Car.brand,
                        Car.model,
                        Person.name,
                        Person.surname,
                        Person.email,
                        Person.phone_number
                    FROM
                        Reservation
                    INNER JOIN Car ON Car.id = Reservation.car_id
                    INNER JOIN Person ON Person.id = Car.person_id
                    ORDER BY
                        Reservation.date DESC;""")
        reservationData = cur.fetchall()
        return render_template("view_reservations.html", reservationData=reservationData)
    
    except Exception as e:
        writeToDoc(e)
        flash('Kaut kas nogāja greizi!', category='error')
    
    finally:
        endWorkDB(conn)
    
    return redirect(url_for("views.admin_home"))

@views.route('/delete_reservation', methods = ['POST'])
@admin_login_required
def delete_reservation():
    reservation_id = request.form.get('reservation_id')
    try:
        conn, cur = startWorkDB()
        cur.execute("DELETE FROM Reservation WHERE reservation_id = %s", (reservation_id, ))
        flash('Ieraksts veiksmīgi dzēsts!', category='success')
    
    except Exception as e:
        writeToDoc(e)
        flash('Kaut kas nogāja greizi!', category='error')
    
    finally:
        endWorkDB(conn)
        return redirect(url_for("views.view_reservations"))

@views.after_request
def apply_caching(response):
    # me trying to stop XSS (i dont know what im doing)
    response.headers["X-Content-Type-Options"] = "nosniff" # Yeah! Dont sniff. Thats weird
    response.headers["X-XSS-Protection"] = "1; mode=block"
    return response