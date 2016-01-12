from functools import wraps
from flask import flash, redirect, session, url_for
from flask.ext.login import current_user
from datetime import datetime, timedelta

from . import db
from .models import BizType, Business, Center, CenterBusiness, CenterEmployee, \
    Document, Employee, EmpPosition

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

def get_stats():
    return Business.query.with_entities(Business.id).all()

def doc_expire(documents, ref, att=0):
    if documents == 'all':
        documents = Document.query.all()
    expire_list = []
    for doc in documents:
        if (doc.expiry - timedelta(days=ref)) <= datetime.today():
            expire_list.append([doc.id, doc.typId])
    if not expire_list: expire_list = [[-1,-1]]
    return zip(*expire_list)[att]

class EmployeeManager(object):
    def __init__(self):
        pass

def get_user_list():
    center = Center.query.get(session['center'])
    return center.employees.filter_by(roster=1).all()

def get_user_info(uid):
    user = Employee.query.get(uid)
    return user

def store_user_info(form):
    if not hasattr(form, 'id'):
        uid = current_user.id
    else:
        uid = form.id.data
    user = Employee.query.get(uid)
    user.fullName = form.fullName.data
    if hasattr(form, 'id'):
        user.posId = form.position.data
    user.email = form.email.data
    if form.password.data:
        user.password = form.password.data
    db.session.commit()
    return user.id

def add_new_user(form):
    user = Employee(fullName=form.fullName.data, posId=form.position.data,
                    email=form.email.data, password=form.password.data)
    db.session.add(user)
    db.session.commit()
    assoc = CenterEmployee(cenId=session['center'], empId=user.id, accId=1)
    db.session.add(assoc)
    db.session.commit()
    return user.id

class RecordManager(object):
    def __init__(self):
        self.__center = Center.query.get(session['center'])
        self.__business = None
        self.__record = None

    @property
    def id(self):
        return self.__record.id

    def all(self, archived=0):
        return self.__center.businesses.filter_by(archived=archived).all()

    def get(self, biz, doc=None, obj=None):
        self.__business = self.__center.businesses.filter_by(bizId=biz).first_or_404()
        if not doc == None:
            return self.__business.info.documents.filter_by(id=doc).first_or_404()
        if obj: return self.__business
        return self.__business.info

    def list(self):
        documents = self.__business.info.documents.with_entities(Document.typId).all()
        if not documents:
            documents = [[-1,-1]]
        return zip(*documents)[0]

    def store(self, form):
        if hasattr(form, 'bizId'):
            if form.id.data == 'new':
                self.__record = Document(typId=form.type.data, bizId=form.bizId.data,
                                         expiry=form.expiry.data)
                db.session.add(self.__record)
            else:
                self.__record = self.get(form.bizId.data, form.id.data)
                self.__record.expiry = form.expiry.data
        else:
            if form.id.data == 'new':
                assoc = CenterBusiness()
                assoc.info = Business(typId=form.type.data, name=form.name.data,
                                      contact=form.contact.data, phone=form.phone.data)
                self.__center.businesses.append(assoc)
                db.session.add(self.__center)
                self.__record = assoc.info
            else:
                self.__record = self.get(form.id.data)
                self.__record.name = form.name.data
                self.__record.typId = form.type.data
                self.__record.contact = form.contact.data
                self.__record.phone = form.phone.data
        db.session.commit()
        return self.__record.id

    def archive(self, biz):
        self.__record = self.get(biz, obj=True)
        self.__record.archived = 1
        db.session.commit()
        return self.__record.bizId

    def delete(self, biz, doc=None):
        if not doc == None:
            self.__record = self.get(biz, doc)
            db.session.delete(self.__record)
            db.session.commit()
            return doc
        self.__record = self.get(biz)
        return biz
