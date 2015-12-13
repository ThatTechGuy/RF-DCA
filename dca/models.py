from sqlalchemy.dialects.mysql import MEDIUMINT, TINYINT, VARCHAR
from sqlalchemy.ext.hybrid import hybrid_property
from flask.ext.login import UserMixin

from . import bcrypt, db

class Center(db.Model):
    id = db.Column(MEDIUMINT(8, unsigned=True), primary_key=True,
                             autoincrement=False)
    phone = db.Column(VARCHAR(10), nullable=False)
    location = db.Column(VARCHAR(255), nullable=False)

class Employee(db.Model,UserMixin):
    id = db.Column(MEDIUMINT(8, unsigned=True), primary_key=True,
                   autoincrement=True)
    posId = db.Column(TINYINT(2, unsigned=True),
                      db.ForeignKey('emp_position.id',
                                    onupdate='RESTRICT',
                                    ondelete='RESTRICT'),
                      nullable=False)
    position = db.relationship('EmpPosition', backref='employees',
                               lazy='select')
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
    accId = db.Column(MEDIUMINT(8, unsigned=True), nullable=False)
    roster = db.Column(TINYINT(1, unsigned=True), nullable=False,
                       server_default='1')
