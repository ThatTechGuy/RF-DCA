from functools import wraps
from flask import flash, redirect, session, url_for
from flask.ext.login import current_user
from datetime import datetime, timedelta

from . import db
from .models import BizType, Business, Center, CenterBusiness, Document, \
    Employee, EmpPosition

def admin_perm_req(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if not current_user.admin:
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

def get_user_data(center=False):
    data = {'center': session['center']}
    data['centers'], = zip(*current_user.centers_list())
    if center == 'all':
        data['perms_list'] = current_user.user_perms_for(center)
    data['perms'] = current_user.user_perms_for(data['center'])
    return data

def get_user_list():
    center = Center.query.get(session['center'])
    return center.employees.filter_by(roster=1).all()

def get_user_info(uid):
    user = Employee.query.get(uid)
    return user

def store_user_info(form):
    user = Employee.query.get(current_user.id)
    user.fullName = form.fullName.data
    user.email = form.email.data
    if form.password.data:
        user.password = form.password.data
    db.session.commit()
    return user.id

def get_rec_info(business, archived=0, document=False):
    center = Center.query.get(session['center'])
    if business == 'all':
        return center.businesses.filter_by(archived=archived).all()
    if document:
        return Document.query.get_or_404(document)
    record = center.businesses.filter_by(bizId=business).first_or_404()
    documents = record.info.documents.with_entities(Document.typId).all()
    if not documents: documents = [(-1,)]
    return {'info': record.info, 'docs': documents}

def get_stats():
    return Business.query.with_entities(Business.id).all()

def doc_expire(documents):
    if documents == 'all':
        documents = Document.query.all()
    expire_list = {'exp_30': [], 'exp_60': []}
    for doc in documents:
        if (doc.expiry - timedelta(days=30)) <= datetime.today():
            expire_list['exp_30'].append([doc.id, doc.typId])
        if (doc.expiry - timedelta(days=60)) <= datetime.today():
            expire_list['exp_60'].append([doc.id, doc.typId])
    if not expire_list['exp_30']: expire_list['exp_30'] = [[-1,-1]]
    if not expire_list['exp_60']: expire_list['exp_60'] = [[-1,-1]]
    return expire_list

def store_biz_info(form):
    business = Business.query.get(form.id.data)
    business.name = form.name.data
    business.typId = form.type.data
    business.contact = form.contact.data
    business.phone = form.phone.data
    db.session.commit()
    return business.id

def store_doc_info(form):
    document = Document.query.get(form.id.data)
    document.expiry = form.expiry.data
    db.session.commit()
    return document.id

def add_new_record(form,type='biz'):
    if type == 'biz':
        new = Business(typId=form.type.data, name=form.name.data,
                       contact=form.contact.data, phone=form.phone.data)
        db.session.add(new)
        db.session.commit()
        assoc = CenterBusiness(cenId=session['center'], bizId=new.id)
        db.session.add(assoc)
        db.session.commit()
        return new.id
    elif type == 'doc':
        new = Document(typId=form.type.data, bizId=form.bizId.data,
                       expiry=form.expiry.data)
        db.session.add(new)
        db.session.commit()
        return new.id
    else:
        abort(400)

def delete_record(record,type='biz'):
    if type == 'biz':
        center = Center.query.get(session['center'])
        business = center.businesses.filter_by(bizId=record).first()
        business.archived = 1
        db.session.commit()
        flash('Record has been placed in the archive.', 'info')
        return record
    elif type == 'doc':
        Document.query.filter_by(id=record).delete()
        db.session.commit()
        flash('Document has been removed from the record.', 'info')
        return record
    else:
        abort(400)
