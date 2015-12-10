from flask import flash, render_template, redirect, request, url_for
from flask.ext.login import current_user, login_user, login_required, logout_user

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
            next = request.args.get('next')
            return redirect(next or url_for('dashboard'))
        else:
            flash(u'Incorrect Username or Password!', 'error')
            return redirect(url_for('login'))
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash(u'You have been logged out, login again.', 'info')
    return redirect(url_for('login'))

@app.route('/users/<action>')
@login_required
def user_admin(action):
    user = str(current_user.id)
    flash(u'The User Box Contains ' + user, 'error')
    return redirect(url_for('login'))
