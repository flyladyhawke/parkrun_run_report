from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.validators import DataRequired
from app.models import Event, Section


class EventForm(FlaskForm):
    event_name = StringField('Event Name', validators=[DataRequired()])
    event_number = StringField('Event Number', validators=[DataRequired()])
    week_number = SelectField('Week Number',  choices=[('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5')])
    parameters = StringField('Parameters')
    submit = SubmitField('Create and show URLS')


class SectionForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    description = StringField('Description', validators=[DataRequired()])
    submit = SubmitField('Add')


class EventSectionForm(FlaskForm):
    event_id = QuerySelectField(
        'Event',
        validators=[DataRequired()],
        query_factory=lambda: Event.query.order_by(Event.event_name.asc()).all()
    )
    section_id = QuerySelectField(
        'Section',
        validators=[DataRequired()],
        query_factory=lambda: Section.query.order_by(Section.name.asc()).all()
    )
    order = StringField('Order')
    display = StringField('Display')
    submit = SubmitField('Add')
