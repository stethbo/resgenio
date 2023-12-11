from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, PasswordField, BooleanField
from wtforms.validators import DataRequired, Email, Optional, EqualTo, Length


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=25)])
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=6),
        EqualTo('confirm', message='Hasła muszą być takie same.')
    ])
    confirm = PasswordField('Confirm Password')
    remember = BooleanField('Remember Me')
    submit = SubmitField('Zarejestruj')


class ResumeForm(FlaskForm):
    linkedin_url = StringField('LinkedIn Profile URL (required)', validators=[DataRequired()]) 
    full_name = StringField('Full Name (required)', validators=[DataRequired()])
    email = StringField('Email (required)', validators=[DataRequired(), Email()])
    phone_number = StringField('Phone Number (required)', validators=[DataRequired()])
    github = StringField('GitHub (optional)', validators=[Optional()])
    personal_website = StringField('Personal Website (optional)', validators=[Optional()])
    twitter = StringField('Twitter (optional)', validators=[Optional()])
    additionals = TextAreaField('Additional information (optional)', validators=[Optional()])
    job_description = TextAreaField('Job Description (required)', validators=[DataRequired()])
    submit = SubmitField('Generuj CV')
