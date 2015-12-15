from flask import abort, flash, render_template, redirect, request, url_for, session
from flask.ext.login import current_user, login_user, login_required, logout_user

from . import app
from .forms import LoginForm
from .util import *

@app.route('/', defaults={'center': None})
@app.route('/center/<center>', endpoint='center')
@login_required
def dashboard(center):
    session['center'] = center
    if not center: center = ''
    centers, = zip(*current_user.centers_list())
    if center and int(center) not in centers:
        flash('You Do Not Have Permission to Access This Center!', 'error')
        return redirect(url_for('dashboard'))
    return render_template('dashboard.html', center=center, centers=centers)

@app.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()
    next = request.args.get('next')
    if form.validate_on_submit():
        valid_user = check_pass(form.email.data, form.password.data)
        if valid_user:
            remember = form.remember.data == 'y'
            login_user(valid_user, remember=remember)
            return redirect(next or url_for('dashboard'))
    return render_template('login.html', form=form, next=next)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out, login again.', 'info')
    return redirect(url_for('login'))

@app.route('/record/<record>')
@login_required
def doc_manage(record):
    pass

@app.route('/manager/<action>')
@login_required
@center_required
def biz_manage(action):
    center = session['center']
    centers, = zip(*current_user.centers_list())
    perms = current_user.user_perms_for(session['center'])
    if action == 'index':
        bizs = get_biz_info('all')
        return render_template('manager.html', bizs=bizs,
                               center=center, centers=centers)
    elif action == 'new' and perms.access.addBiz:
        return render_template('new_biz.html')
    elif action == 'edit' and perms.access.modBiz:
        return render_template('edit_biz.html')
    else:
        abort(404)

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
