from flask import render_template, redirect, url_for
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
        user = Employee.query.filter_by(email=form.email.data).first_or_404()
        if user.is_valid_pass(form.password.data):
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            return redirect(url_for('login'))
    return render_template('login.html', form=form)
