from flask import abort, flash, jsonify, render_template, redirect, request, \
    url_for, session
from flask.ext.login import current_user, login_required, login_user, logout_user

from . import app
from .forms import BusinessForm, DocumentForm, EmployeeForm, LoginForm, \
    NewBusinessForm, NewDocumentForm, NewEmployeeForm, UserInfoForm
from .models import BizType, DocType, EmpPosition
from .util import add_new_record, admin_perm_req, center_required, check_pass, \
    delete_record, doc_expire, get_rec_info, get_stats, get_user_data, get_user_info, \
    get_user_list, mod_perm_req, store_biz_info, store_doc_info, store_user_info

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
    data['expire'] = doc_expire('all')
    data['stats'], = zip(*get_stats())
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
    form_new = NewBusinessForm()
    form.type.choices = [(c.id, c.name) for c in BizType.query.order_by('id')]
    form_new.type.choices = [(c.id, c.name) for c in BizType.query.order_by('id')]
    if form_new.validate_on_submit() and data['perms'].access.addBiz:
        if form_new.form.data == 'add' and add_new_record(form_new):
            flash('Record has been successfully created.', 'info')
            return redirect(url_for('biz_manage'))
        else:
            flash('Record Creation has Failed, Try Again!', 'error')
    if form.validate_on_submit() and data['perms'].access.modBiz:
        if store_biz_info(form):
            flash('Record has been successfully updated.', 'info')
            return redirect(url_for('biz_manage'))
        else:
            flash('Record Update has Failed, Try Again!', 'error')
    data['biz_list'] = get_rec_info('all')
    return render_template('manager.html', data=data, form=form, form_new=form_new)

@app.route('/manager/record/<record>', methods=["GET", "POST"])
@login_required
@center_required
def doc_manage(record):
    data = get_user_data()
    form = DocumentForm()
    form_new = NewDocumentForm()
    form.type.choices = [(c.id, c.name) for c in DocType.query.order_by('id')]
    form_new.type.choices = [(c.id, c.name) for c in DocType.query.order_by('id')]
    if form_new.validate_on_submit() and data['perms'].access.addDoc:
        if add_new_record(form_new, 'doc'):
            flash('Document has been successfully created.', 'info')
            return redirect(url_for('doc_manage', record=record))
        else:
            flash('Document Creation has Failed, Try Again!', 'error')
    if form.validate_on_submit() and data['perms'].access.modDoc:
        if store_doc_info(form):
            flash('Document has been successfully updated.', 'info')
            return redirect(url_for('doc_manage', record=record))
        else:
            flash('Document Update has Failed, Try Again!', 'error')
    data['record'] = get_rec_info(record)
    data['record']['docs'], = zip(*data['record']['docs'])
    expire_list = doc_expire(data['record']['info'].documents)
    data['expire'] = {'exp_30': zip(*expire_list['exp_30'])[1]}
    data['expire']['exp_60'] = zip(*expire_list['exp_60'])[1]
    return render_template('record.html', data=data, form=form, form_new=form_new)

@app.route('/_get_record/<type>', methods=["POST"])
@login_required
@center_required
def get_record(type):
    if type == 'biz':
        if 'action' in request.form and request.form['action'] == 'delete':
            result = delete_record(request.form['id'])
            return jsonify({'id': result})
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
        if 'action' in request.form and request.form['action'] == 'delete':
            result = delete_record(request.form['id'], 'doc')
            return jsonify({'id': result})
        docId = request.form['id']
        doc = get_rec_info(None, document=docId)
        document = {
            'id': doc.id,
            'type': doc.type.id,
            'expiry': doc.expiry.strftime('%m/%d/%Y'),
        }
        return jsonify(document)
    elif type == 'user':
        if 'action' in request.form and request.form['action'] == 'delete':
            result = delete_record(request.form['id'], 'user')
            return jsonify({'id': result})
        empId = request.form['id']
        emp = get_user_info(empId)
        employee = {
            'id': emp.id,
            'fullName': emp.fullName,
            'position': emp.posId,
            'email': emp.email
        }
        return jsonify(employee)
    else:
        abort(400)

@app.route('/users', methods=["GET", "POST"])
@login_required
@mod_perm_req
def user_admin():
    data = get_user_data()
    form = EmployeeForm()
    form_new = NewEmployeeForm()
    form.position.choices = [(c.id, c.title) for c in EmpPosition.query.order_by('id')]
    form_new.position.choices = [(c.id, c.title) for c in EmpPosition.query.order_by('id')]
    data['user_list'] = get_user_list()
    return render_template('users.html', data=data, form=form, form_new=form_new)

@app.route('/settings', methods=["GET", "POST"])
@login_required
@admin_perm_req
def global_settings():
    pass
