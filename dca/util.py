from functools import wraps
from flask import flash, redirect, session, url_for
from flask.ext.login import current_user

from . import db
from .models import Business, Center, Employee

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

def get_user_data():
    data = {'center': session['center']}
    data['centers'], = zip(*current_user.centers_list())
    data['perms'] = current_user.user_perms_for(session['center'])
    return data

def get_biz_info(business, archived=0):
    center = Center.query.get(session['center'])
    if business == 'all':
        return center.businesses.filter_by(archived=archived).all()
    return center.businesses.filter_by(bizId=business).first()

def store_biz_info(form):
    business = Business.query.get(form.id.data)
    business.name = form.name.data
    business.typId = form.type.data
    business.contact = form.contact.data
    business.phone = form.phone.data
    db.session.commit()
    return business.id
