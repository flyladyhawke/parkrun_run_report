from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField
from wtforms.validators import DataRequired


class CreateForm(FlaskForm):
    event_name = StringField('Event Name', validators=[DataRequired()])
    event_number = StringField('Event Number', validators=[DataRequired()])
    week_number = SelectField('Week Number',  choices=[('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5')])
    parameters = StringField('Parameters')
    submit = SubmitField('Create Urls')

