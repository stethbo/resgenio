import os
from dotenv import load_dotenv
from flask import Flask
from flask import render_template, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask import session, request
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required
from datetime import datetime


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///resgen_db.db'
app.config['SECRET_KEY'] = os.environ.get('DB_SECRET_KEY')

activity_db = []
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

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



@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password')
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if password != confirm_password:
            flash('Passwords must match.')
            return redirect(url_for('register'))

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username already exists.')
            return redirect(url_for('register'))

        new_user = User(username=username)
        new_user.set_password(password)

        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful. Please log in.')
        return redirect(url_for('login'))

    return render_template('register.html')



@app.route('/dashboard')
@app.route('/')
@login_required
def dashboard():
    return render_template('dashboard.html')


@app.route('/main', methods=['GET', 'POST'])
def main():
    if 'logged_in' not in session:
        return redirect(url_for('login.html'))

    if request.method == 'POST':
        # Simulate resume generation and add to activity_db
        activity_db.append("Resume generated on " + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

    return render_template('main.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/archive')
@login_required
def archive():
    if 'logged_in' not in session:
        return redirect(url_for('login'))

    # Display history of generation activity
    return render_template('archive.html', activities=activity_db)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port="8080")
    