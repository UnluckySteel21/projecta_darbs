from flask import flash, redirect, url_for, session
from .verification import sanitize_and_replace
from .database import startWorkDB, endWorkDB
from datetime import datetime

def get_users(search_field=None, search_value=None):
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

    return data

def get_pending_users(search_field=None, search_value=None):
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

    # Initialize query and params
    query = """SELECT person.name, person.surname, person.email, person.phoneNumber, 
               car.brand, car.model, car.carNum, car.carVin, car.id, car.date, car.status, car.description, person.description
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
            return redirect(url_for('views.pending_page'))

    data = []
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

    finally:
        endWorkDB(conn)

    return data

def writeToDoc(error):
    with open('documentation\errorMessages.txt', 'r') as file:
        content = file.read()

    with open('documentation\errorMessages.txt', 'w') as file:
        file.write('-'*30 + '\n')
        # Check if 'name' and 'surname' exist in the session
        name = session.get('name', 'Name not found')
        surname = session.get('surname', 'Surname not found')
        file.write(name + ' ' + surname + '\n')
        file.write(str(datetime.now()) + '\n')
        file.write(f'{error}')
        file.write('\n' + '-'*30)
        file.write(content)
