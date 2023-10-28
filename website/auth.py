from flask import Blueprint, render_template, request, flash
from .database import startWorkDB, endWrokDB
from uuid import uuid4
from werkzeug.security import generate_password_hash, check_password_hash

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        flash('Veiksmīga ielogošanās!', category='succes')
        return render_template("user_home.html")
    else:
        return render_template("login.html")
    #if login successful and is admin return render template admin_home
    #if not admin render template user_home

@auth.route('/logout')
def logout():
    return "<p>logout</p>"

@auth.route('/sign_up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        email = request.form.get('email')
        firstName = request.form.get('firstName')
        lastName = request.form.get('lastName')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

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
                conn, cur = startWorkDB()
                cur.execute("SELECT * FROM person WHERE email LIKE %s", (email,))
                notUsedData = cur.fetchone()
                cur.execute("SELECT * FROM logindata WHERE email LIKE %s", (email,))
                UsedData = cur.fetchone()
                if notUsedData != None:
                    if notUsedData[1] == firstName and notUsedData[2] == lastName:
                        if UsedData == None:
                            loginID = str(uuid4())
                            password = generate_password_hash(password1, method='pbkdf2:sha256')
                            cur.execute("""INSERT
                                        INTO logindata (id, email, password)
                                        VALUES (%s, %s, %s)
                                        """, (loginID, email, password))
                            #insert into database sthsth
                            flash('Konts izveidots!', category='succes')
                            return render_template("login.html")
            
            except Exception as e:
                flash(f'Kaut kas nogāja greizi: {e}', category='error')
            
            finally:
                endWrokDB(conn)
        
        return render_template("sign_up.html")
    else:
        return render_template("sign_up.html")
