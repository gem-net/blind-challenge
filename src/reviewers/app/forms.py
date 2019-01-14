from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


class RequestForm(FlaskForm):
    password = StringField('Password', validators=[DataRequired()])
    submit = SubmitField('Submit')
