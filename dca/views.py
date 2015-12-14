from flask import flash, render_template, redirect, request, url_for, session
from flask.ext.login import current_user, login_user, login_required, logout_user

from . import app
from .forms import LoginForm
from .util import admin_perm_req, mod_perm_req, check_pass, get_perms

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
def biz_manage(action):
	perms = get_perms()
	if action == 'new' and get_perm('addBiz'):
		return render_template('add-biz.html')
	elif action == 'edit' and get_perm('modBiz'):
		return render_template('mod-biz.html')
	return render_template('manager.html', perms=perms)

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
