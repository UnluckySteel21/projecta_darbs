from flask import Blueprint, render_template, request, flash, redirect, url_for, session #Importing the standart flask components
from .database import startWorkDB, endWorkDB #the self made database functions
from uuid import uuid4 #uuid for id generation
from werkzeug.security import generate_password_hash, check_password_hash #password hashing and salting for more security
from .verification import custom_logout_user, custom_user_session, login_required, sanitize_and_replace, writeToDoc #self made module to check user privileges, session data and input sanitization

#def the blueprint
auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = sanitize_and_replace(request.form.get('email'))
        password = sanitize_and_replace(request.form.get('password'))
        
        try:
            conn, cur = startWorkDB()
            cur.execute("SELECT * FROM logindata WHERE email = %s", (email,))
            user_data = cur.fetchone()
            cur.execute("SELECT * FROM admins WHERE email = %s", (email,))
            admin_data = cur.fetchone()
            cur.execute("SELECT name, surname FROM person WHERE email = %s", (email, ))
            users_name = cur.fetchall()

            if admin_data:
                hashed_password = admin_data[2]
                if check_password_hash(hashed_password, password):
                    flash('Veiksmīga ielogošanās!', category='success')
                    custom_user_session(admin_data[0], True, "Admin", "", remember=True)
                    return redirect(url_for("views.admin_home"))
                else:
                    flash('Nepareiza parole!', category='error')
                    return redirect(url_for("auth.login"))
            
            if user_data:
                hashed_password = user_data[2]
                if check_password_hash(hashed_password, password):
                    flash('Veiksmīga ielogošanās!', category='success')
                    custom_user_session(user_data[0], False, users_name[0][0], users_name[0][1], remember=True)
                    return redirect(url_for("views.user_home"))
                else:
                    flash('Nepareiza parole!', category='error')
                    return redirect(url_for("auth.login"))
            
            flash('Lietotājs nav atrasts! Pārbaudiet vai pareizi ievadīts epasts!', category='error')
            return redirect(url_for("auth.login"))
        
        except Exception as e:
            flash('Kaut kas nogāja greizi!', category='error')
            writeToDoc(e)
        
        finally:
            endWorkDB(conn)

    return render_template("login.html")

@auth.route('/logout')
@login_required
def logout():
    #logout function
    custom_logout_user()
    return redirect(url_for('auth.login'))

@auth.route('/sign_up', methods=['GET', 'POST'])
def sign_up():
    #function for signup
    if request.method == 'POST':
        #sanitizes user input
        email = sanitize_and_replace(request.form.get('email'))
        firstName = sanitize_and_replace(request.form.get('firstName').upper())
        lastName = sanitize_and_replace(request.form.get('lastName').upper())
        password1 = sanitize_and_replace(request.form.get('password1'))
        password2 = sanitize_and_replace(request.form.get('password2'))

        #basic requirments (might do this in javascript on the user end instead. Idk yet)
        if len(email) < 4:
            flash('Epasta adresei jābūt garākai par 4 simboliem!', category='error')
        elif len(firstName) < 2:
            flash('Vārdam jābūt garākam par 2 simboliem!', category='error')
        elif len(lastName) < 2:
            flash('Uzvārdam jābūt garākam par 2 simboliem!', category='error')
        elif len(password1) < 7:
            flash('Parolei jābūt garākai par 7 simboliem!', category='error')
        elif password1 != password2:
            flash('Paroles nav vienādas!', category='error')
        else:
            try:
                #using try so the website keeps running in case of database failure.
                conn, cur = startWorkDB()
                cur.execute("SELECT * FROM person WHERE email LIKE %s", (email,))
                notUsedData = cur.fetchone()
                cur.execute("SELECT * FROM logindata WHERE email LIKE %s", (email,))
                UsedData = cur.fetchone()
                if notUsedData is None or notUsedData[1] != firstName or notUsedData[2] != lastName:
                    flash('Nepareizi lietotāja dati!', category='error')
                elif UsedData is None:
                    loginID = str(uuid4())
                    password = generate_password_hash(password1, method='pbkdf2:sha256')
                    cur.execute("""INSERT
                                INTO logindata (id, email, password, admin)
                                VALUES (%s, %s, %s, %s)
                                """, (loginID, email, password, False))
                    flash('Konts izveidots!', category='succes')
                    return redirect(url_for("auth.login"))
            
            except Exception as e:
                flash('Kaut kas nogāja greizi', category='error')
                writeToDoc(e)
            
            finally:
                endWorkDB(conn)
        
        return render_template("sign_up.html")
    else:
        return render_template("sign_up.html")
    
@auth.after_request
def apply_caching(response):
    #these are my poor atempts to stop XSS (I dont have any cybersecirty degree so i am surprised this somewhat works)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    return response