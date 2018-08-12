from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.validators import DataRequired, EqualTo, Email, ValidationError
from app.models import Event, Section, User


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')


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
