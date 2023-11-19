import os
import tempfile
import re
import logging
from flask import Blueprint, render_template, redirect, url_for, flash, send_file, send_from_directory
from flask_login import login_user, logout_user, login_required, current_user
import markdown
from weasyprint import HTML

from . import db, bcrypt, login_manager
from .models import User, UserDetails
from .forms import LoginForm, RegistrationForm, ResumeForm
from src.generate_resume import get_resume_content


main_blueprint = Blueprint('main', __name__)
logger = logging.getLogger(__file__)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@main_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        # Check if user exists and the password is correct
        user = User.query.filter_by(username=form.username.data).first()
        if user and bcrypt.check_password_hash(user.password_hash, form.password.data):
            login_user(user, remember=form.remember.data)
            # Redirect to the dashboard or other page
            return redirect(url_for('main.dashboard'))
        else:
            flash('Invalid username or password')
    return render_template('login.html', form=form)


@main_blueprint.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        existing_user = User.query.filter_by(username=form.username.data).first()
        if existing_user:
            flash('Username already exists')
            return redirect(url_for('main.register'))
        
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, password_hash=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('main.login'))
    return render_template('register.html', form=form)


@main_blueprint.route('/dashboard')
@main_blueprint.route('/')
@login_required
def dashboard():
    return render_template('dashboard.html')


@main_blueprint.route('/generate', methods=['GET', 'POST'])
@login_required
def generate():
    user_details = UserDetails.query.filter_by(user_id=current_user.id).first()
    form = ResumeForm(obj=user_details)

    if form.validate_on_submit():
        if not user_details:
            user_details = UserDetails(user_id=current_user.id)
            db.session.add(user_details)

        form.populate_obj(user_details)
        db.session.commit()

        # Generate the resume content
        resume_content = get_resume_content(form.data)
        logger.info(f'Got resume content of type: {type(resume_content)}')

        user_id = re.sub(r'/$', '', form.data['linkedin_url'])  # deleting the / if exist at the end of a string
        user_id = user_id.split('/')[-1]
        temp_file_path = f"data/{user_id}_resume.pdf"
        html_content = markdown.markdown(resume_content)
        HTML(string=html_content).write_pdf(temp_file_path)

        flash('Resume generated successfully.')
        # Redirect to the download route with the path of the temporary file
        return redirect(url_for('main.preview_pdf', filename=temp_file_path.split('/')[-1]))

    return render_template('generate.html', form=form)


@main_blueprint.route('/preview/<filename>')
def preview_pdf(filename):
    # Render the preview template
    print(f"LOCATION: {os.getcwd()}")
    file_path = os.path.join('data', filename)
    return render_template('preview.html', filename=filename)


@main_blueprint.route('/pdf_preview/<filename>')
def pdf_preview(filename):
    # Construct the full file path
    dir = '/Users/stefan/coding/find_best_cv/data'
    return send_from_directory(dir, filename)



@main_blueprint.route('/download_pdf/<filename>')
def download_pdf(filename):
    dir = '/Users/stefan/coding/find_best_cv/data'
    return send_from_directory(dir, filename)


@main_blueprint.route('/download_resume/<temp_file_path>', methods=['GET'])
@login_required
def download_resume(temp_file_path):

    if temp_file_path and os.path.exists(temp_file_path):
        response = send_file(temp_file_path, as_attachment=True)
        os.remove(temp_file_path)
        return response

    flash('Error in downloading the file.')
    return redirect(url_for('main.dashboard'))


@main_blueprint.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.dashboard'))
