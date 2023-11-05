from functools import wraps
from flask import session, flash, redirect, url_for, request
import re

def custom_user_session(user_id, is_admin, remember=False):
    session['user_id'] = user_id
    session['admin'] = is_admin

    if remember:
        session['remember'] = True

    session.modified = True

def custom_logout_user():
    session.pop('user_id', None)
    session.pop('admin', None)

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