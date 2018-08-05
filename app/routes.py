from flask import render_template, url_for
from app import app, db
from app.forms import CreateForm
from src import run_report_utils
from app.models import Event


@app.route('/')
@app.route('/index')
def index():
    form = CreateForm()
    return render_template('index.html', title='Index',)


@app.route('/create', methods=['GET', 'POST'])
def create():
    form = CreateForm()
    result = ''
    if form.validate_on_submit():
        model = Event()
        form.populate_obj(model)
        db.session.add(model)
        db.session.commit()

        run_report = run_report_utils.RunReportWeek(form.event_name.data, form.event_number.data)
        result = {'links': run_report.print_urls(form.week_number.data, 8)}

    return render_template('create.html', title='Create', form=form, result=result)


@app.route('/admin', methods=['GET', 'POST'])
def admin():
    form = CreateForm()
    if form.validate_on_submit():
        run_report = run_report_utils.RunReportWeek(form.event_name.data, form.event_number.data)
        result = {'links': run_report.print_urls(form.week_number.data, 8)}
        return render_template('admin/admin.html', title='Admin', form=form, result=result)
    return render_template('admin/admin.html', title='Admin', form=form)


@app.route('/event', methods=['GET', 'POST'])
def events():
    current = Event.query.all()
    return render_template('events.html', title='Events', current=current)
