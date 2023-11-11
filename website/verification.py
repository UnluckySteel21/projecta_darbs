from functools import wraps
from flask import session, flash, redirect, url_for, request
import re
from datetime import datetime

def custom_user_session(user_id, is_admin, user_name, user_surname, remember=False):
    session['user_id'] = user_id
    session['admin'] = is_admin
    session['name'] = user_name
    session['surname'] = user_surname

    if remember:
        session['remember'] = True

    session.modified = True

def custom_logout_user():
    session.pop('user_id', None)
    session.pop('admin', None)
    session.pop('name', None)
    session.pop('surname', None)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Lai apmeklētu šo lapu jums jābūt adminam! ', category='error')
            return redirect(url_for('auth.login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

def admin_login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or 'admin' not in session or not session['admin']:
            flash('Lai apmeklētu šo lapu jums jāielogojas', category='error')
            return redirect(url_for('auth.login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

def sanitize_and_replace(input_string):
    #   Sanitize user input to prevent XSS and replace special characters.
    # Replace special characters
    trans = str.maketrans("ĒĀĪŪ", "EAIU")
    input_string = input_string.translate(trans)
    
    # Remove any character that isn't a word character, a space, or @ . -
    sanitized = re.sub(r'[^\w\s@.-]', '', input_string)
    
    return sanitized

def writeToDoc(error):
    with open('documentation\errorMessages.txt', 'r') as file:
        content = file.read()

    with open('documentation\errorMessages.txt', 'w') as file:
        file.write('-'*30 + '\n')
        file.write(session['name'] + ' ' + session['surname'] + '\n')
        file.write(str(datetime.now()) + '\n')
        file.write(f'{error}')
        file.write('\n' + '-'*30)
        file.write(content) 
