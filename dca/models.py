from sqlalchemy.dialects.mysql import MEDIUMINT, TINYINT, VARCHAR
from sqlalchemy.sql.expression import and_, or_
from sqlalchemy.ext.hybrid import hybrid_property
from flask.ext.login import UserMixin

from . import bcrypt, db

class Center(db.Model):
    id = db.Column(MEDIUMINT(8, unsigned=True), primary_key=True,
                   autoincrement=False)
    phone = db.Column(VARCHAR(10), nullable=False)
    location = db.Column(VARCHAR(255), nullable=False)
    businesses = db.relationship('CenterBusiness', lazy='dynamic')
    employees = db.relationship('CenterEmployee', lazy='dynamic')

    def all_biz(self, archived):
        return self.businesses.filter_by(archived=archived).all()

    def all_excluded(self):
        return db.engine.execute("SELECT * FROM (SELECT * FROM center_business WHERE cenId = %s) cb RIGHT OUTER JOIN business b ON bizId = id WHERE cb.archived = 1 or cb.archived is NULL" % self.id)

    def biz_by_id(self, biz):
        return self.businesses.filter(and_(
            CenterBusiness.bizId==biz,
            CenterBusiness.archived==0)).first_or_404()

    def arc_by_id(self, biz):
        return self.businesses.filter_by(bizId=biz).first()

class Employee(db.Model,UserMixin):
    id = db.Column(MEDIUMINT(8, unsigned=True), primary_key=True,
                   autoincrement=True)
    posId = db.Column(TINYINT(2, unsigned=True),
                      db.ForeignKey('emp_position.id',
                                    onupdate='RESTRICT',
                                    ondelete='RESTRICT'),
                      nullable=False)
    position = db.relationship('EmpPosition', backref='employees',
                               lazy='subquery')
    email = db.Column(VARCHAR(255), nullable=False)
    _password = db.Column(VARCHAR(60), nullable=False)
    fullName = db.Column(VARCHAR(255), nullable=False)
    admin = db.Column(TINYINT(1, unsigned=True), nullable=False,
                      server_default='0')
    permissions = db.relationship('CenterEmployee', lazy='dynamic')

    @hybrid_property
    def password(self):
        return self._password

    @password.setter
    def _set_password(self, plaintext):
        self._password = bcrypt.generate_password_hash(plaintext)

    def is_valid_pass(self, plaintext):
        return bcrypt.check_password_hash(self._password, plaintext)

    def centers_list(self):
        return self.permissions.with_entities(CenterEmployee.cenId).all()

    def user_perms_for(self, center):
        if center == 'all':
            return self.permissions.all()
        return self.permissions.filter_by(cenId=center).first()

class EmpPosition(db.Model):
    id = db.Column(TINYINT(2, unsigned=True), primary_key=True,
                   autoincrement=False)
    title = db.Column(VARCHAR(255), nullable=False)
    description = db.Column(VARCHAR(255), nullable=False)

class CenterEmployee(db.Model):
    cenId = db.Column(MEDIUMINT(8, unsigned=True),
                      db.ForeignKey('center.id',
                                    onupdate='RESTRICT',
                                    ondelete='RESTRICT'),
                      primary_key=True)
    empId = db.Column(MEDIUMINT(8, unsigned=True),
                      db.ForeignKey('employee.id',
                                    onupdate='RESTRICT',
                                    ondelete='RESTRICT'),
                      primary_key=True)
    data = db.relationship('Employee', backref='centers',
                           lazy='subquery')
    accId = db.Column(MEDIUMINT(8, unsigned=True),
                      db.ForeignKey('ce_access.id',
                                    onupdate='RESTRICT',
                                    ondelete='RESTRICT'),
                      nullable=False)
    access = db.relationship('CeAccess', backref='center_employees',
                             lazy='subquery')
    moderator = db.Column(TINYINT(1, unsigned=True), nullable=False,
                       server_default='0')
    roster = db.Column(TINYINT(1, unsigned=True), nullable=False,
                       server_default='1')

class CeAccess(db.Model):
    id = db.Column(MEDIUMINT(8, unsigned=True), primary_key=True,
                   autoincrement=True)
    level = db.Column(VARCHAR(255), nullable=False)
    addDoc = db.Column(TINYINT(1, unsigned=True), nullable=False,
                       server_default='0')
    modDoc = db.Column(TINYINT(1, unsigned=True), nullable=False,
                       server_default='0')
    delDoc = db.Column(TINYINT(1, unsigned=True), nullable=False,
                       server_default='0')
    addBiz = db.Column(TINYINT(1, unsigned=True), nullable=False,
                       server_default='0')
    modBiz = db.Column(TINYINT(1, unsigned=True), nullable=False,
                       server_default='0')
    delBiz = db.Column(TINYINT(1, unsigned=True), nullable=False,
                       server_default='0')
    impBiz = db.Column(TINYINT(1, unsigned=True), nullable=False,
                       server_default='0')
    arcBiz = db.Column(TINYINT(1, unsigned=True), nullable=False,
                       server_default='0')

class Business(db.Model):
    id = db.Column(MEDIUMINT(8, unsigned=True), primary_key=True,
                   autoincrement=True)
    typId = db.Column(TINYINT(2, unsigned=True),
                      db.ForeignKey('biz_type.id',
                                    onupdate='RESTRICT',
                                    ondelete='RESTRICT'),
                      nullable=False)
    type = db.relationship('BizType', backref='businesses',
                           lazy='subquery')
    name = db.Column(VARCHAR(255), nullable=False)
    contact = db.Column(VARCHAR(255), nullable=False)
    phone = db.Column(VARCHAR(10), nullable=False)
    documents = db.relationship('Document', backref='business',
                                lazy='dynamic')

class BizType(db.Model):
    id = db.Column(TINYINT(2, unsigned=True), primary_key=True,
                   autoincrement=False)
    name = db.Column(VARCHAR(255), nullable=False)
    description = db.Column(VARCHAR(255), nullable=False)
    requirements = db.relationship('TypeRequire', lazy='dynamic')

class CenterBusiness(db.Model):
    cenId = db.Column(MEDIUMINT(8, unsigned=True),
                      db.ForeignKey('center.id',
                                    onupdate='RESTRICT',
                                    ondelete='RESTRICT'),
                      primary_key=True)
    bizId = db.Column(MEDIUMINT(8, unsigned=True),
                      db.ForeignKey('business.id',
                                    onupdate='RESTRICT',
                                    ondelete='RESTRICT'),
                      primary_key=True)
    details = db.relationship('Business', backref='centers',
                              lazy='joined')
    archived = db.Column(TINYINT(1, unsigned=True), nullable=False,
                         server_default='0')

    def doc_by_id(self, doc):
        return self.details.documents.filter_by(id=doc).first_or_404()

    def doc_type_list(self):
        return self.details.documents.with_entities(Document.typId).all()

class Document(db.Model):
    id = db.Column(MEDIUMINT(8, unsigned=True), primary_key=True,
                   autoincrement=True)
    typId = db.Column(TINYINT(2, unsigned=True),
                      db.ForeignKey('doc_type.id',
                                    onupdate='RESTRICT',
                                    ondelete='RESTRICT'),
                      nullable=False)
    type = db.relationship('DocType', backref='documents',
                           lazy='subquery')
    bizId = db.Column(MEDIUMINT(8, unsigned=True),
                      db.ForeignKey('business.id',
                                    onupdate='RESTRICT',
                                    ondelete='RESTRICT'),
                      nullable=False)
    store = db.Column(VARCHAR(255), nullable=True)
    expiry = db.Column(db.DateTime, nullable=False)

class DocType(db.Model):
    id = db.Column(TINYINT(2, unsigned=True), primary_key=True,
                   autoincrement=False)
    name = db.Column(VARCHAR(255), nullable=False)
    description = db.Column(VARCHAR(255), nullable=False)

class TypeRequire(db.Model):
    bizType = db.Column(TINYINT(2, unsigned=True),
                        db.ForeignKey('biz_type.id',
                                      onupdate='RESTRICT',
                                      ondelete='RESTRICT'),
                      primary_key=True)
    docType = db.Column(TINYINT(2, unsigned=True),
                        db.ForeignKey('doc_type.id',
                                      onupdate='RESTRICT',
                                      ondelete='RESTRICT'),
                        primary_key=True)
    type = db.relationship('DocType', lazy='joined')
    available = db.Column(TINYINT(1, unsigned=True), nullable=False,
                          server_default='0')
