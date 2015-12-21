from flask import abort, flash, jsonify, render_template, redirect, request, \
    url_for, session
from flask.ext.login import current_user, login_required, login_user, logout_user

from . import app
from .forms import BusinessForm, DocumentForm, LoginForm, UserInfoForm, \
    UserPermForm
from .models import BizType, DocType, EmpPosition
from .util import admin_perm_req, center_required, check_pass, doc_expire, \
    get_rec_info, get_user_data, mod_perm_req, store_biz_info, store_doc_info, \
    store_user_info

@app.route('/', defaults={'center': None})
@app.route('/center/<center>', endpoint='center')
@login_required
def dashboard(center):
    session['center'] = center
    if not center: center = ''
    data = get_user_data()
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
    data = get_user_data(center='all')
    form = UserInfoForm()
    form.position.choices = [(c.id, c.title) for c in EmpPosition.query.order_by('id')]
    if form.validate_on_submit():
        if store_user_info(form):
            flash('Your profile has been successfully updated', 'info')
            return redirect(url_for('my_profile'))
        else:
            flash('Profile Update has Failed, Try Again!', 'error')
    form.fullName.data = current_user.fullName
    form.position.data = current_user.position.id
    form.email.data = current_user.email
    return render_template('profile.html', data=data, form=form)

@app.route('/manager', methods=["GET", "POST"])
@login_required
@center_required
def biz_manage():
    data = get_user_data()
    form = BusinessForm()
    form.type.choices = [(c.id, c.name) for c in BizType.query.order_by('id')]
    if form.validate_on_submit() and data['perms'].access.modBiz:
        if store_biz_info(form):
            flash('Record has been successfully updated.', 'info')
            return redirect(url_for('biz_manage'))
        else:
            flash('Record Update has Failed, Try Again!', 'error')
    data['biz_list'] = get_rec_info('all')
    return render_template('manager.html', data=data, form=form)

@app.route('/manager/record/<record>', methods=["GET", "POST"])
@login_required
@center_required
def doc_manage(record):
    data = get_user_data()
    form = DocumentForm()
    form.type.choices = [(c.id, c.name) for c in DocType.query.order_by('id')]
    if form.validate_on_submit() and data['perms'].access.modDoc:
        if store_doc_info(form):
            flash('Document has been successfully updated.', 'info')
            return redirect(url_for('doc_manage', record=record))
        else:
            flash('Document Update has Failed, Try Again!', 'error')
    data['record'] = get_rec_info(record)
    data['record']['docs'], = zip(*data['record']['docs'])
    data['expire'] = doc_expire(data['record']['info'].documents)
    return render_template('record.html', data=data, form=form)

@app.route('/_get_record/<type>', methods=["POST"])
@login_required
@center_required
def get_record(type):
    if type == 'biz':
        bizId = request.form['id']
        biz = get_rec_info(bizId)
        business = {
            'id': biz['info'].id,
            'type': biz['info'].type.id,
            'name': biz['info'].name,
            'contact': biz['info'].contact,
            'phone': biz['info'].phone
        }
        return jsonify(business)
    elif type == 'doc':
        docId = request.form['id']
        doc = get_rec_info(None, document=docId)
        document = {
            'id': doc.id,
            'type': doc.type.id,
            'expiry': doc.expiry.strftime('%m/%d/%Y'),
        }
        return jsonify(document)
    else:
        abort(400)

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
