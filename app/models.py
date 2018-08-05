from app import db


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
    sections = db.relationship('EventSection', backref='section', lazy='dynamic')

    def __repr__(self):
        return '<Section {}>'.format(self.description)


class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event_name = db.Column(db.String(50), index=True)
    event_number = db.Column(db.Integer, index=True)
    sections = db.relationship('EventSection', backref='event', lazy='dynamic')
    options = db.relationship('EventOption', backref='event', lazy='dynamic')

    def __repr__(self):
        return '{} {}'.format(self.event_name, self.event_number)


class EventOption(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'))
    key = db.Column(db.String(50), index=True)
    value = db.Column(db.String(50))


class EventSection(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'))
    section_id = db.Column(db.Integer, db.ForeignKey('section.id'))
    order = db.Column(db.Integer)
    display = db.Column(db.Integer)


class EventSectionText(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event_section_id = db.Column(db.Integer, db.ForeignKey('event_section.id'))
    part = db.Column(db.String(50))
    text = db.Column(db.String(250))
