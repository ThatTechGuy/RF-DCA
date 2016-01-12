from flask import abort, flash, jsonify, render_template, redirect, request, \
    url_for, session
from flask.ext.login import current_user, login_required, login_user, logout_user

from . import app
from .forms import BusinessForm, DocumentForm, LoginForm, UserInfoForm
from .models import BizType, DocType, EmpPosition
from .util import add_new_user, admin_perm_req, center_required, check_pass, \
    doc_expire, get_stats, get_user_data, get_user_info, \
    get_user_list, mod_perm_req, store_user_info, RecordManager

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
    data['stats'], = zip(*get_stats())
    data['expire'] = {'exp_30': doc_expire('all', 30)}
    data['expire']['exp_60'] = doc_expire('all', 60)
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
    records = RecordManager()
    data = get_user_data()
    form = BusinessForm()
    form.type.choices = [(c.id, c.name) for c in BizType.query.order_by('id')]
    if form.validate_on_submit() and records.store(form):
        if form.id.data == 'new':
            return redirect(url_for('doc_manage', record=records.id))
        flash('Record has been successfully updated.', 'info')
        return redirect(url_for('biz_manage'))
    data['biz_list'] = records.all()
    return render_template('manager.html', data=data, form=form)

@app.route('/manager/record/<record>', methods=["GET", "POST"])
@login_required
@center_required
def doc_manage(record):
    records = RecordManager()
    data = get_user_data()
    form = DocumentForm()
    form.type.choices = [(c.id, c.name) for c in DocType.query.order_by('id')]
    if form.validate_on_submit() and records.store(form):
        flash('Document has been successfully updated.', 'info')
        return redirect(url_for('doc_manage', record=record))
    data['record'] = records.get(record)
    data['doc_list'] = records.list()
    data['expire'] = doc_expire(data['record'].documents, 30, 1)
    return render_template('record.html', data=data, form=form)

@app.route('/users', methods=["GET", "POST"])
@login_required
@mod_perm_req
def user_admin():
    data = get_user_data()
    form = UserInfoForm()
    form.position.choices = [(c.id, c.title) for c in EmpPosition.query.order_by('id')]
    if form.validate_on_submit() and data['perms'].access.moderator:
        if store_user_info(form):
            flash('User has been successfully updated.', 'info')
            return redirect(url_for('user_admin'))
        else:
            flash('User Update has Failed, Try Again!', 'error')
    data['user_list'] = get_user_list()
    return render_template('users.html', data=data, form=form)

@app.route('/settings', methods=["GET", "POST"])
@login_required
@admin_perm_req
def global_settings():
    pass

@app.route('/_get_data/<type>', methods=["POST"])
@login_required
@center_required
def get_data(type):
    records = RecordManager()
    if type == 'biz':
        if 'action' in request.form and request.form['action'] == 'archive':
            result = records.archive(request.form['bizId'])
            flash('Record has been archived successfully.', 'info')
            return jsonify({'id': result})
        bizId = request.form['bizId']
        biz = records.get(bizId)
        business = {
            'id': biz.id,
            'type': biz.type.id,
            'name': biz.name,
            'contact': biz.contact,
            'phone': biz.phone
        }
        return jsonify(business)
    elif type == 'doc':
        if 'action' in request.form and request.form['action'] == 'delete':
            result = records.delete(request.form['bizId'], request.form['docId'])
            flash('Document has been deleted successfully.', 'info')
            return jsonify({'id': result})
        docId = request.form['docId']
        bizId = request.form['bizId']
        doc = records.get(bizId, docId)
        document = {
            'id': doc.id,
            'type': doc.type.id,
            'expiry': doc.expiry.strftime('%m/%d/%Y'),
        }
        return jsonify(document)
    elif type == 'usr':
        if 'action' in request.form and request.form['action'] == 'remove':
            result = delete_record(request.form['usrId'], 'user')
            return jsonify({'id': result})
        usrId = request.form['usrId']
        usr = get_user_info(usrId)
        user = {
            'id': usr.id,
            'fullName': usr.fullName,
            'position': usr.posId,
            'email': usr.email
        }
        return jsonify(user)
    else:
        abort(400)
