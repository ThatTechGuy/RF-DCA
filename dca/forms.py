from flask.ext.wtf import Form
from wtforms.fields import BooleanField, HiddenField, PasswordField, \
    SelectField, TextField
from wtforms.validators import Required, Email

class LoginForm(Form):
    email = TextField('Email Address', validators=[Required(), Email()])
    password = PasswordField('Password', validators=[Required()])
    remember = BooleanField('Remember Me')

class BusinessForm(Form):
    id = HiddenField('Record ID', validators=[Required()])
    type = SelectField('Business Type', coerce=int)
    name = TextField('Business Name', validators=[Required()])
    contact = TextField('Contact Name', validators=[Required()])
    phone = TextField('Phone Number', validators=[Required()])
