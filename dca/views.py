from flask import flash, render_template, redirect, request, url_for, session
from flask.ext.login import current_user, login_user, login_required, logout_user

from . import app
from .forms import LoginForm
from .models import Employee
from .util import mod_perm_req

@app.route('/', defaults={'center': None})
@app.route('/center/<center>', endpoint='center')
@login_required
def dashboard(center):
    session['center'] = center
    centers, = zip(*current_user.centers_list())
    if center and int(center) not in centers:
        flash('You Do Not Have Permission to Access This Center!', 'error')
    return render_template('dashboard.html', centers=centers)

@app.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()
    next = request.args.get('next')
    if form.validate_on_submit():
        user = Employee.query.filter_by(email=form.email.data).first()
        if user and user.is_valid_pass(form.password.data):
            remember = form.remember.data == 'y'
            login_user(user, remember=remember)
            return redirect(next or url_for('dashboard'))
        else:
            flash(u'Incorrect Username or Password!', 'error')
            return redirect(url_for('login'))
    return render_template('login.html', form=form, next=next)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash(u'You have been logged out, login again.', 'info')
    return redirect(url_for('login'))

@app.route('/record/<record>')
@login_required
def doc_manage
    pass
    
@app.route('/manager/<action>')
@login_required
def biz_manage(action):
    pass

@app.route('/users/<action>')
@login_required
@mod_perm_req
def user_admin(action):
    pass

@app.route('/settings')
@login_required
@admin_perm_req
def global_settings():
    pass
