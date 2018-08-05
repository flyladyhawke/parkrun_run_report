from flask import render_template, url_for
from app import app, db
from app.forms import EventForm, EventSectionForm, SectionForm
from src import run_report_utils
from app.models import Event, EventSection, Section


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html', title='Index',)


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

    return render_template('create.html', title='Create', form=form, result=result, event_id=event_id)


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
    return render_template('reference/section.html', title='Section', form=form, current=current)


@app.route('/admin', methods=['GET', 'POST'])
def admin():
    return render_template('admin/admin.html', title='Admin')


@app.route('/event', methods=['GET', 'POST'])
def events():
    current = Event.query.all()
    return render_template('admin/events.html', title='Events', current=current)
