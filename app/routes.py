import tempfile
import logging
from flask import (Blueprint, render_template, redirect, url_for, flash, send_file,
                   make_response, request, jsonify)
from flask_login import login_user, logout_user, login_required, current_user
import markdown
from weasyprint import HTML

from . import db, bcrypt, login_manager
from .models import User, UserDetails, Resumes
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
        resume_content, resume_title = get_resume_content(form.data, test=False)


        logger.info(f'User id🆔: {current_user.id}')
        resume = Resumes(user_id=current_user.id, content=resume_content, summary=resume_title)
        db.session.add(resume)
        db.session.commit()
        generated_id = resume.id

        flash('Resume generated successfully.')
        # Redirect to the download route with the path of the temporary file
        return redirect(url_for('main.preview', resume_id=generated_id))

    return render_template('generate.html', form=form)


@main_blueprint.route('/preview/<int:resume_id>')
@login_required
def preview(resume_id):
    # Retrieve the resume content by ID
    resume = Resumes.query.get_or_404(resume_id)

    # Convert the Markdown content to HTML
    html_content = markdown.markdown(resume.content)
    logger.info(f'type of content from DB: {type(html_content)}')

    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temp:
        # Create a path for the temp file to send it
        HTML(string=html_content).write_pdf(temp.name)

    # Render the template with the filename
    return render_template('preview.html', resume_id=resume_id)


@main_blueprint.route('/pdf_preview/<int:resume_id>')
@login_required
def pdf_preview(resume_id):
    resume = Resumes.query.get_or_404(resume_id)

    # Convert the Markdown content to HTML
    html_content = markdown.markdown(resume.content)
    logger.info(f'type of content from DB: {type(html_content)}')

    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temp:
        # Create a path for the temp file to send it
        temp_file_path = temp.name
        HTML(string=html_content).write_pdf(temp.name)

    return send_file(temp_file_path)


@main_blueprint.route('/download_resume/<int:resume_id>', methods=['GET'])
@login_required
def download_resume(resume_id):

    user_name = UserDetails.query.filter_by(user_id=current_user.id).first().full_name

    resume = Resumes.query.get_or_404(resume_id)

    # Convert the Markdown content to HTML
    html_content = markdown.markdown(resume.content)
    logger.info(f'type of content from DB: {type(html_content)}')

    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temp:
        # Create a path for the temp file to send it
        temp_file_path = temp.name
        HTML(string=html_content).write_pdf(temp.name)

    # Render the template with the filename
    return make_response(
        send_file(
            temp_file_path,
            as_attachment=True,
            download_name=f"{user_name.replace(' ', '_').lower()}_resume_{resume_id}.pdf"
            ))


@main_blueprint.route('/feedback', methods=['POST'])
@login_required
def handle_feedback():
    logger.info("HANDLING FEEDBACK🔙")
    data = request.get_json()
    resume_id = data['resume_id']
    user_feedback = 1 if data['feedback'] == 'like' else 0

    # Find the resume and update feedback
    resume = Resumes.query.get_or_404(resume_id)
    resume.feedback = user_feedback
    
    # Commit the changes to the database
    db.session.commit()

    return jsonify({"message": "Feedback received"})


@main_blueprint.route('/archive')
@login_required
def archive():
    resume_list = Resumes.query.filter_by(user_id=current_user.id).order_by(Resumes.id.desc()).all()
    return render_template('archive.html', resume_list=resume_list)


@main_blueprint.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.dashboard'))
