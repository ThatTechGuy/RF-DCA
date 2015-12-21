from flask.ext.wtf import Form
from wtforms.fields import BooleanField, DateField, HiddenField, \
    PasswordField, SelectField, TextField
from wtforms.validators import InputRequired, Length, Required, Email, \
    EqualTo, Optional

class LoginForm(Form):
    email = TextField('Email Address', validators=[Required(), Email()])
    password = PasswordField('Password', validators=[Required()])
    remember = BooleanField('Remember Me')

class UserInfoForm(Form):
    id = HiddenField('Employee ID')
    fullName = TextField('Full Name', validators=[Required()])
    position = SelectField('Employee Position', coerce=int,
                           validators=[Optional()])
    email = TextField('Email Address', validators=[Required(), Email()])
    password = PasswordField(
        'New Password',
        validators=[EqualTo('confirm', message='Passwords must match.')])
    confirm = PasswordField('Repeat Password')

class UserPermForm(Form):
    accId = SelectField('Access ID', coerce=int)

class BusinessForm(Form):
    id = HiddenField('Business ID', validators=[Required()])
    type = SelectField('Record Type', coerce=int)
    name = TextField('Registered Name', validators=[Required()])
    contact = TextField('Agent Name', validators=[Required()])
    phone = TextField('Phone Number', validators=[Required()])

class DocumentForm(Form):
    id = HiddenField('Document ID', validators=[Required()])
    type = SelectField('Record Type', coerce=int, validators=[Optional()])
    expiry = DateField('Expiry Date', format='%m/%d/%Y',
                       validators=[Required()])
