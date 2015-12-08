from flask import flash, render_template, redirect, url_for
from flask.ext.login import login_user, login_required

from . import app
from .forms import LoginForm
from .models import Employee

@app.route('/')
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = Employee.query.filter_by(email=form.email.data).first()
        if user and user.is_valid_pass(form.password.data):
            remember = form.remember.data == 'y'
            login_user(user, remember=remember)
            return redirect(url_for('dashboard'))
        else:
            flash('Incorrect Username or Password!', category='error')
            return redirect(url_for('login'))
    return render_template('login.html', form=form)
