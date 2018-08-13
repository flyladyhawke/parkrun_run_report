from flask import render_template, url_for, redirect, flash, request
from app import app, db
from app.forms import RunReportForm, RunReportSectionForm, SectionForm, LoginForm, RegistrationForm, PasswordResetForm
from src import run_report_utils
from app.models import RunReport, RunReportSection, Section, User
from flask_login import login_required, current_user, login_user, logout_user
from werkzeug.urls import url_parse
from werkzeug.exceptions import Forbidden


@app.route('/')
@app.route('/index')
def index():
    breadcrumbs = [
        {'text': 'Home'}
    ]
    return render_template('index.html', title='Index', breadcrumbs=breadcrumbs)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password', 'danger')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    breadcrumbs = [
        {'link': url_for('index'), 'text': 'Home', 'visible': True},
        {'text': 'Login'}
    ]
    return render_template('auth/login.html', title='Sign In', form=form, breadcrumbs=breadcrumbs)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User()
        form.populate_obj(user)
        user.set_password(form.password.data)
        user.level = 3
        user.active = 1
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!', 'success')
        return redirect(url_for('login'))
    breadcrumbs = [
        {'link': url_for('index'), 'text': 'Home', 'visible': True},
        {'text': 'Register'}
    ]
    return render_template('auth/register.html', title='Register', form=form, breadcrumbs=breadcrumbs)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/password_reset', methods=['GET', 'POST'])
@login_required
def password_reset():
    form = PasswordResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(id=current_user.id).first()
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Password Reset!', 'success')
        return redirect(url_for('index'))
    breadcrumbs = [
        {'link': url_for('index'), 'text': 'Home', 'visible': True},
        {'text': 'Password Reset'}
    ]
    return render_template('auth/password_reset.html', title='Password Reset', form=form, breadcrumbs=breadcrumbs)


@app.route('/run_reports', methods=['GET', 'POST'])
@login_required
def run_reports():
    current = RunReport.query.filter_by(created_by_id=current_user.id)
    breadcrumbs = [
        {'link': url_for('index'), 'text': 'Home', 'visible': True},
        {'text': 'Run Reports'}
    ]
    return render_template(
        'run_reports.html',
        title='Run Reports',
        current=current,
        breadcrumbs=breadcrumbs,
        tables=[{'name': 'run-report-list'}],
    )


@app.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    form = RunReportForm()
    result = ''
    run_report_id = False
    if form.validate_on_submit():
        model = RunReport()
        form.populate_obj(model)
        model.created_by_id = current_user.id
        db.session.add(model)
        db.session.commit()

        run_report = run_report_utils.RunReportWeek(form.event_name.data, form.event_number.data)
        result = {'links': run_report.print_urls(form.week_number.data, 8)}
        run_report_id = model.id
        # return redirect(url_for('run_report_update', run_report_id=run_report_id))
    breadcrumbs = [
        {'link': url_for('index'), 'text': 'Home', 'visible': True},
        {'link': url_for('run_reports'), 'text': 'Run Reports', 'visible': True},
        {'text': 'Create'}
    ]
    return render_template(
        'create.html',
        title='Create',
        form=form,
        result=result,
        run_report_id=run_report_id,
        breadcrumbs=breadcrumbs
    )


@app.route('/run_report/update/<run_report_id>', methods=['GET', 'POST'])
def run_report_update(run_report_id):
    form = RunReportSectionForm()
    form.run_report_id = run_report_id
    if form.validate_on_submit():
        # Check whether there is already this section
        found = RunReportSection.query.filter_by(run_report_id=run_report_id, section_id=form.section_id.data.id).first()
        if found:
            flash('This section was already added.', 'danger')
        else:
            model = RunReportSection()
            form.populate_obj(model)
            model.section_id = model.section_id.id
            model.run_report_id = model.run_report_id.id
            db.session.add(model)
            db.session.commit()
            flash('This section has been added', 'success')

    current = RunReportSection.query.filter_by(run_report_id=run_report_id)
    breadcrumbs = [
        {'link': url_for('index'), 'text': 'Home', 'visible': True},
        {'link': url_for('run_reports'), 'text': 'Run Reports', 'visible': True},
        {'text': 'Update'}
    ]
    return render_template(
        'add_sections.html',
        title='Sections',
        form=form,
        current=current,
        breadcrumbs=breadcrumbs,
    )


@app.route('/run_report/export/<run_report_id>', methods=['GET', 'POST'])
def run_report_export(run_report_id):
    current = RunReport.query.filter_by(id=run_report_id).first()
    breadcrumbs = [
        {'link': url_for('index'), 'text': 'Home', 'visible': True},
        {'link': url_for('run_reports'), 'text': 'Run Reports', 'visible': True},
        {'text': 'Export'}
    ]
    return render_template(
        'add_sections.html',
        title='Sections',
        current=current,
        breadcrumbs=breadcrumbs
    )


@app.route('/run_report/delete/<run_report_id>', methods=['GET', 'POST'])
def run_report_delete(run_report_id):
    current_model = RunReport.query.filter_by(id=run_report_id).first_or_404()
    db.session.delete(current_model)
    db.session.commit()
    flash('The run report has been deleted.', 'success')
    return redirect(url_for('run_reports'))


@app.route('/run_report_section/delete/<run_report_section_id>', methods=['GET', 'POST'])
def run_report_section_delete(run_report_section_id):
    current_model = RunReportSection.query.filter_by(id=run_report_section_id).first_or_404()
    run_report_id = current_model.run_report_id
    db.session.delete(current_model)
    db.session.commit()
    flash('The run report section has been deleted.', 'success')
    return redirect(url_for('run_report_update', run_report_id=run_report_id))


@app.route('/reference/section', methods=['GET', 'POST'])
@login_required
def section():
    if not is_admin():
        raise Forbidden
    form = SectionForm()
    if form.validate_on_submit():
        model = Section()
        form.populate_obj(model)
        db.session.add(model)
        db.session.commit()
        flash('Your changes have been saved.', 'success')
    current = Section.query.all()
    breadcrumbs = [
        {'link': url_for('index'), 'text': 'Home', 'visible': True},
        {'link': url_for('admin'), 'text': 'Admin', 'visible': True},
        {'text': 'Sections'}
    ]
    return render_template(
        'reference/section.html',
        title='Section',
        form=form,
        current=current,
        breadcrumbs=breadcrumbs
    )


@app.route('/reference/section/delete<section_id>', methods=['GET', 'POST'])
@login_required
def section_delete(section_id):
    current_model = Section.query.filter_by(id=section_id).first_or_404()
    db.session.delete(current_model)
    db.session.commit()
    flash('The section has been deleted.', 'success')
    return redirect(url_for('section'))


@app.route('/admin', methods=['GET', 'POST'])
@login_required
def admin():
    if not is_admin():
        raise Forbidden
    breadcrumbs = [
        {'link': url_for('index'), 'text': 'Home', 'visible': True},
        {'text': 'Admin'}
    ]
    return render_template(
        'admin/admin.html',
        title='Admin',
        breadcrumbs=breadcrumbs
    )


@app.route('/admin/users', methods=['GET', 'POST'])
@login_required
def users():
    if not is_admin():
        raise Forbidden
    current = User.query.all()
    breadcrumbs = [
        {'link': url_for('index'), 'text': 'Home', 'visible': True},
        {'link': url_for('admin'), 'text': 'Admin', 'visible': True},
        {'text': 'Users'}
    ]
    return render_template(
        'admin/users.html',
        title='Sections',
        current=current,
        breadcrumbs=breadcrumbs,
        tables=[{'name': 'user-list'}],
    )


# @app.route('/run_report', methods=['GET', 'POST'])
# @login_required
# def run_reports():
#     if not is_admin():
#         raise Forbidden
#     current = RunReport.query.all()
#     breadcrumbs = [
#         {'link': url_for('index'), 'text': 'Home', 'visible': True},
#         {'link': url_for('admin'), 'text': 'Admin', 'visible': True},
#         {'text': 'Run Reports'}
#     ]
#     return render_template(
#         'run_reports.html',
#         title='Run Reports',
#         current=current,
#         breadcrumbs=breadcrumbs
#     )


def is_admin():
    return current_user.is_authenticated and current_user.level >= 2


def is_sys_admin():
    return current_user.is_authenticated and current_user.level >= 3
