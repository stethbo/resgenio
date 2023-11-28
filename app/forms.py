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
    linkedin_url = StringField('LinkedIn Profile URL', validators=[DataRequired()]) 
    full_name = StringField('Full Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone_number = StringField('Phone Number', validators=[DataRequired()])
    github = StringField('GitHub', validators=[Optional()])
    personal_website = StringField('Personal Website', validators=[Optional()])
    twitter = StringField('Twitter', validators=[Optional()])
    job_description = TextAreaField('Job Description', validators=[DataRequired()])
    submit = SubmitField('Generuj CV')