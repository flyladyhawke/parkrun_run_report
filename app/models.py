from app import db, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50))
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    email = db.Column(db.String(50))
    active = db.Column(db.Integer)
    level = db.Column(db.Integer)
    password_hash = db.Column(db.String(128))
    run_reports = db.relationship('RunReport', backref='created_by', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '{} {}'.format(self.first_name, self.last_name)


class Option(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(50), index=True)
    value = db.Column(db.String(50))
    description = db.Column(db.String(150))

    def __repr__(self):
        return '<Option {} {}>'.format(self.key, self.description)


class Section(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    description = db.Column(db.String(150))
    default_order = db.Column(db.Integer)
    sections = db.relationship('RunReportSection', backref='section', lazy='dynamic')

    def __repr__(self):
        return self.name


class RunReport(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event_name = db.Column(db.String(50), index=True)
    event_number = db.Column(db.Integer, index=True)
    journalist_report = db.Column(db.Text)
    created_by_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    sections = db.relationship('RunReportSection', backref='event', lazy='dynamic')
    options = db.relationship('RunReportOption', backref='event', lazy='dynamic')
    results = db.relationship('RunReportResult', backref='event', lazy='dynamic')

    def __repr__(self):
        return '{} {}'.format(self.event_name, self.event_number)


class RunReportOption(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    run_report_id = db.Column(db.Integer, db.ForeignKey('run_report.id'))
    key = db.Column(db.String(50), index=True)
    value = db.Column(db.String(50))


class RunReportSection(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    run_report_id = db.Column(db.Integer, db.ForeignKey('run_report.id'))
    section_id = db.Column(db.Integer, db.ForeignKey('section.id'))
    order = db.Column(db.Integer)
    display = db.Column(db.Integer)
    photos = db.relationship('RunReportPhoto', backref='section', lazy='dynamic')

    def __repr__(self):
        return '{}'.format(self.section.name)


class RunReportSectionText(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    run_report_section_id = db.Column(db.Integer, db.ForeignKey('run_report_section.id'))
    part = db.Column(db.String(50))
    text = db.Column(db.String(250))


class RunReportPhoto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    run_report_section_id = db.Column(db.Integer, db.ForeignKey('run_report_section.id'))
    link = db.Column(db.String(250))
    width = db.Column(db.Integer)
    height = db.Column(db.Integer)
    title = db.Column(db.String(250))


class RunReportResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    run_report_id = db.Column(db.Integer, db.ForeignKey('run_report.id'))
    event_result = db.Column(db.Text)
    is_current = db.Column(db.Integer)
