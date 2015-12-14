from functools import wraps
from flask import flash, redirect, session, url_for
from flask.ext.login import current_user

def mod_perm_req(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        perms = current_user.user_perms_for(session['center'])
        if not perms or not perms.access.moderator:
            flash('You Do Not Have Permission to Access This Page!', 'error')
            return redirect(url_for('dashboard'))
        return func(*args, **kwargs)

    return decorated_function
