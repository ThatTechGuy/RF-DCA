from flask import abort, flash, jsonify, render_template, redirect, request, \
    url_for, session
from flask.ext.login import current_user, login_required, login_user, logout_user

from . import app
from .forms import BusinessForm, LoginForm
from .models import BizType
from .util import admin_perm_req, center_required, check_pass, get_biz_info, \
    get_user_data, mod_perm_req, store_biz_info

@app.route('/', defaults={'center': None})
@app.route('/center/<center>', endpoint='center')
@login_required
def dashboard(center):
    session['center'] = center
    if not center: center = ''
    data = {'center': center}
    data['centers'], = zip(*current_user.centers_list())
    if center and int(center) not in data['centers']:
        flash('You Do Not Have Permission to Access This Center!', 'error')
        return redirect(url_for('dashboard'))
    return render_template('dashboard.html', data=data)

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

@app.route('/profile', methods=["GET", "POST"])
@login_required
def my_profile():
    data = get_user_data()
    # form = ProfileForm()
    # if form.validate_on_submit():
    #     pass
    return render_template('profile.html')

@app.route('/manager', methods=["GET", "POST"])
@login_required
@center_required
def biz_manage():
    data = get_user_data()
    form = BusinessForm()
    form.type.choices = [(g.id, g.name) for g in BizType.query.order_by('id')]
    if form.validate_on_submit():
        if store_biz_info(form):
            flash('Record has been successfully updated.', 'info')
            return redirect(url_for('biz_manage'))
        else:
            flash('Record Update has Failed, Try Again!', 'error')
    data['biz_list'] = get_biz_info('all')
    return render_template('manager.html', data=data, form=form)

@app.route('/_edit_biz', methods=["POST"])
@login_required
@center_required
def edit_biz():
    bizId = request.form['id']
    biz = get_biz_info(bizId)
    business = {
        'id': biz.info.id,
        'type': biz.info.type.id,
        'name': biz.info.name,
        'contact': biz.info.contact,
        'phone': biz.info.phone
    }
    return jsonify(business)

@app.route('/record/<record>', methods=["GET", "POST"])
@login_required
@center_required
def doc_manage(record):
    pass

@app.route('/users', methods=["GET", "POST"])
@login_required
@mod_perm_req
def user_admin():
    pass

@app.route('/settings', methods=["GET", "POST"])
@login_required
@admin_perm_req
def global_settings():
    pass
