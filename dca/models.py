from sqlalchemy.dialects.mysql import MEDIUMINT, TINYINT, VARCHAR
from sqlalchemy.ext.hybrid import hybrid_property
from flask.ext.login import UserMixin

from . import bcrypt, db

class Center(db.Model):
    id = db.Column(MEDIUMINT(8, unsigned=True), primary_key=True,
                             autoincrement=False)
    phone = db.Column(VARCHAR(10), nullable=False)
    location = db.Column(VARCHAR(255), nullable=False)
    businesses = db.relationship('CenterBusiness', lazy='dynamic')

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

    def user_perms_for(self, center):
        return self.permissions.filter_by(cenId=center).first()

    def centers_list(self):
        return self.permissions.with_entities(CenterEmployee.cenId).all()

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
    accId = db.Column(MEDIUMINT(8, unsigned=True),
                      db.ForeignKey('ce_access.id',
                                    onupdate='RESTRICT',
                                    ondelete='RESTRICT'),
                      nullable=False)
    access = db.relationship('CeAccess', backref='center_employees',
                               lazy='subquery')
    roster = db.Column(TINYINT(1, unsigned=True), nullable=False,
                       server_default='1')

class CeAccess(db.Model):
    id = db.Column(MEDIUMINT(8, unsigned=True), primary_key=True,
                   autoincrement=True)
    access = db.Column(VARCHAR(255), nullable=False)
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
    moderator = db.Column(TINYINT(1, unsigned=True), nullable=False,
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

class BizType(db.Model):
    id = db.Column(TINYINT(2, unsigned=True), primary_key=True,
                   autoincrement=False)
    name = db.Column(VARCHAR(255), nullable=False)
    description = db.Column(VARCHAR(255), nullable=False)

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
    info = db.relationship('Business', backref='centers',
                               lazy='joined')
    archived = db.Column(TINYINT(1, unsigned=True), nullable=False,
                         server_default='0')
