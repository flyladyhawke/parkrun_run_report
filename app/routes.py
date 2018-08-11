from flask import render_template, url_for, redirect, flash
from app import app, db
from app.forms import EventForm, EventSectionForm, SectionForm, LoginForm
from src import run_report_utils
from app.models import Event, EventSection, Section, User
from flask_login import login_required, current_user, login_user, logout_user


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html', title='Index',)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        return redirect(url_for('index'))
    return render_template('auth/login.html', title='Sign In', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/create', methods=['GET', 'POST'])
def create():
    form = EventForm()
    result = ''
    event_id = False
    if form.validate_on_submit():
        model = Event()
        form.populate_obj(model)
        db.session.add(model)
        db.session.commit()

        run_report = run_report_utils.RunReportWeek(form.event_name.data, form.event_number.data)
        result = {'links': run_report.print_urls(form.week_number.data, 8)}
        event_id = model.id
    breadcrumbs = [
        {'link': url_for('index'), 'text': 'Home', 'visible': True},
        {'text': 'Create'}
    ]
    return render_template(
        'create.html',
        title='Create',
        form=form,
        result=result,
        event_id=event_id,
        breadcrumbs=breadcrumbs
    )


@app.route('/add_sections/<event_id>', methods=['GET', 'POST'])
def add_sections(event_id):
    form = EventSectionForm()
    form.event_id = event_id
    if form.validate_on_submit():
        model = EventSection()
        form.populate_obj(model)
        db.session.add(model)
        db.session.commit()

    current = EventSection.query.filter_by(event_id=event_id)

    return render_template('add_sections.html', title='Sections', form=form, current=current)


@app.route('/reference/section', methods=['GET', 'POST'])
def section():
    form = SectionForm()
    if form.validate_on_submit():
        model = Section()
        form.populate_obj(model)
        db.session.add(model)
        db.session.commit()
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


@app.route('/admin', methods=['GET', 'POST'])
def admin():
    breadcrumbs = [
        {'link': url_for('index'), 'text': 'Home', 'visible': True},
        {'text': 'Admin'}
    ]
    return render_template(
        'admin/admin.html',
        title='Admin',
        breadcrumbs=breadcrumbs
    )


@app.route('/event', methods=['GET', 'POST'])
def events():
    current = Event.query.all()
    breadcrumbs = [
        {'link': url_for('index'), 'text': 'Home', 'visible': True},
        {'link': url_for('admin'), 'text': 'Admin', 'visible': True},
        {'text': 'Events'}
    ]
    return render_template(
        'admin/events.html',
        title='Events',
        current=current,
        breadcrumbs=breadcrumbs
    )
