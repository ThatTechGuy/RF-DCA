from flask.ext.wtf import Form
from wtforms.fields import HiddenField, TextField, PasswordField, BooleanField
from wtforms.validators import Required, Email

class LoginForm(Form):
    email = TextField('Email Address', validators=[Required(), Email()])
    password = PasswordField('Password', validators=[Required()])
    remember = BooleanField('Remember Me')

class BusinessForm(Form):
    biz_id = HiddenField('Record ID', validators=[Required()])
    name = TextField('Business Name', validators=[Required()])
    contact = TextField('Contact Name', validators=[Required()])
    phone = TextField('Phone Number', validators=[Required()])
