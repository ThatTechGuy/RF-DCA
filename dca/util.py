from functools import wraps
from flask import flash, redirect, session, url_for
from flask.ext.login import current_user

from .models import Center, Employee

def admin_perm_req(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        admin = current_user.admin
        if not admin:
            flash('You Do Not Have Permission to Access This Page!', 'error')
            return redirect(url_for('dashboard'))
        return func(*args, **kwargs)

    return decorated_function

def mod_perm_req(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        perms = current_user.user_perms_for(session['center'])
        if not perms or not perms.access.moderator:
            flash('You Do Not Have Permission to Access This Page!', 'error')
            return redirect(url_for('dashboard'))
        return func(*args, **kwargs)

    return decorated_function

def center_required(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        center = session['center']
        if not center:
            flash('You Must Select a Center to Access This Page!', 'error')
            return redirect(url_for('dashboard'))
        return func(*args, **kwargs)

    return decorated_function

def check_pass(email, password):
    user = Employee.query.filter_by(email=email).first()
    if not user or not user.is_valid_pass(password):
        flash('Incorrect Username or Password!', 'error')
        return False
    return user

def get_biz_info(business, archived=0):
    center = Center.query.filter_by(id=session['center']).first()
    if business == 'all':
        return center.businesses.filter_by(archived=archived).all()
    return center.businesses.filter_by(bizId=business).first()
