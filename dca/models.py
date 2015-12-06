from sqlalchemy.dialects.mysql import MEDIUMINT, TINYINT, VARCHAR
from sqlalchemy.ext.hybrid import hybrid_property
from flask.ext.login import UserMixin

from . import bcrypt, db

class Employee(db.Model,UserMixin):
    id = db.Column(MEDIUMINT(8, unsigned=True), primary_key=True,
                   autoincrement=True)
    posId = db.Column(TINYINT(2, unsigned=True),
                      db.ForeignKey('emp_position.id',
                                    onupdate='RESTRICT',
                                    ondelete='RESTRICT'),
                      nullable=False)
    email = db.Column(VARCHAR(255), nullable=False)
    _password = db.Column(VARCHAR(60), nullable=False)
    fullName = db.Column(VARCHAR(255), nullable=False)
    admin = db.Column(TINYINT(1, unsigned=True), nullable=False,
                      server_default='0')

    @hybrid_property
    def password(self):
        return self._password

    @password.setter
    def _set_password(self, plaintext):
        self._password = bcrypt.generate_password_hash(plaintext)

    def is_valid_pass(self, plaintext):
        return bcrypt.check_password_hash(self._password, plaintext)

class EmpPosition(db.Model):
    id = db.Column(TINYINT(2, unsigned=True), primary_key=True,
                   autoincrement=False)
    position = db.Column(VARCHAR(255), nullable=False)
    employees = db.relationship('Employee', backref='emp_position',
                                lazy='dynamic')
