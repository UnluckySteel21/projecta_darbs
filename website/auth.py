#Importing the standart flask components

from flask import (Blueprint,
                render_template,
                request, flash,
                redirect,
                url_for) 
#the self made database functions
from .database import startWorkDB, endWorkDB
#password hashing and salting for more security
from werkzeug.security import generate_password_hash, check_password_hash
#self made module to check user privileges, session data
from .verification import (custom_logout_user,
                           custom_user_session,
                           login_required,
                           sanitize_and_replace)
from .viewsFunctions import writeToDoc
#def the blueprint
auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    """
    Handles user login. 
    If the user is an admin, they are redirected to the admin home page.
    If the user is not admin, they are redirected to the user home page.
    """
    if request.method == 'POST':
        email = sanitize_and_replace(request.form.get('email'))
        password = sanitize_and_replace(request.form.get('password'))

        try:
            conn, cur = startWorkDB()
            cur.execute("SELECT * FROM Person WHERE email LIKE %s", (email,))
            user_data = cur.fetchone()
            cur.execute("SELECT * FROM Admins WHERE email LIKE  %s", (email,))
            admin_data = cur.fetchone()
            print(user_data)

            if admin_data and check_password_hash(admin_data[2],
                                                  password):
                flash('Veiksmīga ielogošanās!',
                      category='success')
                custom_user_session(admin_data[0],
                                    True,
                                    "Admin",
                                    "",
                                    remember=True)
                return redirect(url_for("views.admin_home"))

            if user_data and check_password_hash(user_data[3], password):
                flash('Veiksmīga ielogošanās!', category='success')
                custom_user_session(user_data[0],
                                    False,
                                    user_data[1],
                                    user_data[2],
                                    remember=True)
                return redirect(url_for("views.user_home"))

            flash('Lietotājs nav atrasts!',
                  category='error')
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
    """
    Sign-up form, lets users make an account
    """
    if request.method == 'POST':
        email = sanitize_and_replace(request.form.get('email'))
        firstName = sanitize_and_replace(request.form.get('firstName'))
        lastName = sanitize_and_replace(request.form.get('lastName'))
        password1 = sanitize_and_replace(request.form.get('password1'))
        password2 = sanitize_and_replace(request.form.get('password2'))
        lastName = lastName.upper()
        firstName = firstName.upper()

        if len(email) < 4:
            if len(firstName) < 2:
                if len(lastName) < 2:
                    if len(password1) < 7: 
                        if password1 != password2:
                            flash('Lūdzu pārbaudi ievaddatus!',
                            category='error')           
        else:
            try:
                conn, cur = startWorkDB()
                cur.execute("SELECT * FROM Person WHERE email LIKE %s",
                            (email,))
                UsedData = cur.fetchone()
                if UsedData is not None:
                    if UsedData[3] is not None:
                        flash('Epasta adrese jau ir piereģistrēta!',
                              category='error')
                    elif UsedData[3] == None:
                        if UsedData[1] == firstName and UsedData[2] == lastName:
                            password = generate_password_hash(password1,
                                                method='pbkdf2:sha256')
                            cur.execute("""UPDATE Person
                                    SET password = %s
                                    WHERE email LIKE %s""",
                                    (password, email))
                            flash('Konts veiksmigi izveidots!',
                                  category='success')
                            return redirect(url_for("auth.login"))
                else:
                    flash("Lai reģistrētos apmeklējiet autoservisu.",
                          category='error')
                    return redirect(url_for("auth.login"))

            except Exception as e:
                flash('Kaut kas nogāja greizi!', category='error')
                writeToDoc(e)

            finally:
                endWorkDB(conn)

    return render_template("sign_up.html")
    
@auth.after_request
def apply_caching(response):
    #these are my poor atempts to stop XSS 
    #(I am surprised this somewhat works)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    return response