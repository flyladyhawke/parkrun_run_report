from flask import render_template, url_for
from app import app
from app.forms import CreateForm
from src import run_report_utils


@app.route('/')
@app.route('/index')
def index():
    form = CreateForm()
    return render_template('index.html', title='Index',)


@app.route('/create', methods=['GET', 'POST'])
def create():
    form = CreateForm()
    if form.validate_on_submit():
        run_report = run_report_utils.RunReportWeek(form.event_name.data, form.event_number.data)
        result = {'links': run_report.print_urls(form.week_number.data, 8)}
        return render_template('create.html', title='Sign In', form=form, result=result)
    return render_template('create.html', title='Sign In', form=form)
