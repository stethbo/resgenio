from . import db, bcrypt
from flask_login import UserMixin
from flask_bcrypt import Bcrypt

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)
    
    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')


class UserDetails(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    full_name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    phone_number = db.Column(db.String(20))
    github = db.Column(db.String(100), nullable=True)
    personal_website = db.Column(db.String(100), nullable=True)
    twitter = db.Column(db.String(100), nullable=True)
    job_description = db.Column(db.Text, nullable=True)

    user = db.relationship('User', backref=db.backref('details', lazy=True))


class Resumes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)  # For resume content
    summary = db.Column(db.String(255), nullable=False)  # For summary of the resume
    feedback = db.Column(db.Integer, nullable=True)

    user = db.relationship('User', backref=db.backref('resumes', lazy=True))
