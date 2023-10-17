from flask import Flask
from flask import render_template, redirect, url_for
from flask import session, request
import requests
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'supersecretkey'

# Simulated database for storing generation activity
activity_db = []


@app.route('/')
def login():
    # For demonstration purposes, just setting the session variable here
    session['logged_in'] = True
    # Simulated login page with "Log in with LinkedIn" button
    return render_template('login.html')



@app.route('/main', methods=['GET', 'POST'])
def main():
    if 'logged_in' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        # Simulate resume generation and add to activity_db
        activity_db.append("Resume generated on " + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

    return render_template('main.html')

@app.route('/archive')
def archive():
    if 'logged_in' not in session:
        return redirect(url_for('login'))

    # Display history of generation activity
    return render_template('archive.html', activities=activity_db)


if __name__ == '__main__':
    app.run(debug=True)

