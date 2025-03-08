import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

import logging
from flask import Flask, render_template, request, jsonify, flash, redirect, url_for, make_response
from flask_login import LoginManager, login_required, current_user
from flask_jwt_extended import JWTManager
from flask_wtf.csrf import CSRFProtect
from flask_wtf import FlaskForm
from wtforms import HiddenField
from services.ats_analyzer import ATSAnalyzer
from services.ai_suggestions import AISuggestions
from services.file_parser import FileParser
from services.resume_customizer import ResumeCustomizer
from extensions import db
from models import JobDescription, CustomizedResume, User

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Initialize Flask app with explicit instance path
instance_path = os.path.join(os.getcwd(), 'instance')
app = Flask(__name__, instance_path=instance_path)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev_secret_key_change_in_production")

# Make sure instance folder exists and is writable
os.makedirs(app.instance_path, exist_ok=True)
logger.info(f"Using instance path: {app.instance_path}")

# Use a more direct approach for SQLite database
# Format the path correctly for SQLite: use three slashes for relative paths
# Avoid potential issues with Dropbox path handling
db_name = 'resumerocket.db'
db_path = os.path.join(app.instance_path, db_name) 
db_uri = f"sqlite:///{db_path}"
app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
logger.info(f"Database URI: {db_uri}")
logger.info(f"Database path: {db_path}")
app.config['JWT_SECRET_KEY'] = os.environ.get("JWT_SECRET_KEY", app.secret_key)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Configure SQLAlchemy specifically for SQLite in Dropbox
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    "connect_args": {
        "timeout": 30,       # 30 second timeout
        "check_same_thread": False  # Allow access from multiple threads
    },
    "pool_pre_ping": True,   # Verify connections before using them
    "pool_recycle": 60,      # Recycle connections after 60 seconds
    "max_overflow": 10       # Allow up to 10 connections over pool size
}

# Initialize extensions
db.init_app(app)
csrf = CSRFProtect(app)
jwt = JWTManager(app)
login_manager = LoginManager(app)
login_manager.login_view = 'auth.login'

# Register blueprints
from routes.auth import auth_bp
from routes.jobs import jobs_bp
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(jobs_bp, url_prefix='/api')

# Initialize services
ats_analyzer = ATSAnalyzer()
ai_suggestions = AISuggestions()
resume_customizer = ResumeCustomizer()

# In-memory storage for resumes
resumes = {}

@login_manager.user_loader
def load_user(user_id):
    try:
        return User.query.get(int(user_id))
    except Exception as e:
        logger.error(f"Error loading user: {str(e)}")
        return None

@app.route('/api/customize-resume', methods=['POST'])
@login_required
def customize_resume_endpoint():
    try:
        # Check if the request is JSON
        if request.is_json:
            data = request.get_json()
            if not data:
                logger.error("No JSON data provided")
                return jsonify({'error': 'No data provided'}), 400
                
            resume_id = data.get('resume_id')
            job_id = data.get('job_id')
        else:
            # Handle form data for HTMX requests
            logger.debug(f"Form data received: {request.form}")
            
            # Get values directly from form data
            resume_id = request.form.get('resume_id')
            job_id = request.form.get('job_id')

        logger.debug(f"Raw values - resume_id: {resume_id}, job_id: {job_id}")

        if not resume_id or not job_id:
            error_msg = 'Both resume and job information are required'
            logger.error(f"Missing required IDs - {error_msg}")
            if request.headers.get('HX-Request'):
                flash(error_msg, 'error')
                return render_template('partials/error.html', error=error_msg)
            return jsonify({'error': error_msg}), 400

        try:
            resume_id = int(resume_id)
            job_id = int(job_id)
        except (TypeError, ValueError) as e:
            error_msg = 'Invalid resume or job ID format'
            logger.error(f"Invalid ID format: {str(e)}")
            if request.headers.get('HX-Request'):
                flash(error_msg, 'error')
                return render_template('partials/error.html', error=error_msg)
            return jsonify({'error': error_msg}), 400

        # Get the job description
        job = JobDescription.query.get_or_404(job_id)
        if job.user_id != current_user.id:
            error_msg = 'Unauthorized access'
            logger.error(f"Unauthorized access - job.user_id: {job.user_id}, current_user.id: {current_user.id}")
            if request.headers.get('HX-Request'):
                flash(error_msg, 'error')
                return redirect(url_for('index'))
            return jsonify({'error': error_msg}), 403

        # Get the original resume content
        if resume_id not in resumes or resumes[resume_id]['user_id'] != current_user.id:
            error_msg = 'Invalid resume or unauthorized access'
            logger.error(f"Invalid resume access - resume_id: {resume_id}")
            if request.headers.get('HX-Request'):
                flash(error_msg, 'error')
                return redirect(url_for('index'))
            return jsonify({'error': error_msg}), 403

        original_content = resumes[resume_id]['content']
        logger.debug("Found original resume content")

        # Generate customized resume
        customization_result = resume_customizer.customize_resume(
            original_content,
            job.content
        )
        logger.debug("Generated customized resume content")

        # Create new customized resume record
        customized_resume = CustomizedResume(
            original_content=original_content,
            customized_content=customization_result['customized_content'],
            job_description_id=job.id,
            user_id=current_user.id,
            ats_score=customization_result['ats_score'],
            matching_keywords=customization_result['matching_keywords'],
            missing_keywords=customization_result['missing_keywords']
        )

        db.session.add(customized_resume)
        db.session.commit()
        logger.debug(f"Created customized resume with ID: {customized_resume.id}")

        # For HTMX requests, redirect to the stacked view first
        # JavaScript will then redirect to comparison view if JS is enabled
        if request.headers.get('HX-Request'):
            response = make_response('')
            response.headers['HX-Redirect'] = url_for('view_customized_resume', resume_id=customized_resume.id)
            return response

        # For API requests, return JSON response
        return jsonify({
            'success': True,
            'customized_resume': customized_resume.to_dict(),
            'redirect': url_for('view_customized_resume', resume_id=customized_resume.id)
        }), 201

    except Exception as e:
        logger.error(f"Error customizing resume: {str(e)}")
        error_msg = f'Error customizing resume: {str(e)}'
        if request.headers.get('HX-Request'):
            return render_template('partials/error.html', error=error_msg)
        return jsonify({'error': error_msg}), 500

@app.route('/upload', methods=['POST'])
@login_required
def upload_resume():
    try:
        # Debug logging
        logger.debug("Form data received: %s", request.form)

        # Check if file is present
        if 'resume_file' not in request.files and 'resume' not in request.form:
            return render_template('partials/analysis_results.html',
                               error='No resume file or content provided',
                               ats_score={'score': 0, 'matching_keywords': [], 'missing_keywords': []},
                               suggestions=[])

        # Get job description from form
        job_description = None
        job_url = request.form.get('job_url', '').strip()
        if job_url:
            # Basic cleanup of URL format - add https:// if missing
            if not job_url.startswith(('http://', 'https://')):
                job_url = 'https://' + job_url
                
            # If URL is provided, fetch job description
            try:
                from services.job_description_processor import JobDescriptionProcessor
                processor = JobDescriptionProcessor()
                job_data = processor.extract_from_url(job_url)
                # Extract content from the returned dictionary
                job_description = job_data['content'] if isinstance(job_data, dict) else job_data
                logger.info(f"Successfully extracted job description from URL: {job_url}")
            except Exception as e:
                logger.error(f"Error extracting job description from URL: {str(e)}")
                return render_template('partials/analysis_results.html',
                                   error=f'Error extracting job description from URL. Please try entering the job description directly.',
                                   ats_score={'score': 0, 'matching_keywords': [], 'missing_keywords': []},
                                   suggestions=[])
        else:
            job_description = request.form.get('job_description', '').strip()

        if not job_description:
            return render_template('partials/analysis_results.html',
                               error='Job description is required',
                               ats_score={'score': 0, 'matching_keywords': [], 'missing_keywords': []},
                               suggestions=[])

        # Get resume content either from file or form
        resume_content = None
        if 'resume_file' in request.files:
            file = request.files['resume_file']
            if file.filename:
                # Validate file
                is_valid, error_message = FileParser.allowed_file(file)
                if not is_valid:
                    logger.error(f"File validation failed: {error_message}")
                    return render_template('partials/analysis_results.html',
                                       error=error_message,
                                       ats_score={'score': 0, 'matching_keywords': [], 'missing_keywords': []},
                                       suggestions=[])

                try:
                    resume_content = FileParser.parse_to_markdown(file)
                except Exception as e:
                    logger.error(f"Error parsing file: {str(e)}")
                    return render_template('partials/analysis_results.html',
                                       error=f'Error parsing resume file: {str(e)}',
                                       ats_score={'score': 0, 'matching_keywords': [], 'missing_keywords': []},
                                       suggestions=[])
        else:
            resume_content = request.form.get('resume', '').strip()

        if not resume_content:
            return render_template('partials/analysis_results.html',
                               error='No resume content provided',
                               ats_score={'score': 0, 'matching_keywords': [], 'missing_keywords': []},
                               suggestions=[])

        # Store resume in memory with user ID
        resume_id = len(resumes)
        resumes[resume_id] = {
            'content': resume_content,
            'job_description': job_description,
            'user_id': current_user.id
        }

        # Create job description
        job = JobDescription(
            title="Job Description",
            content=job_description,
            user_id=current_user.id
        )
        db.session.add(job)
        db.session.commit()

        # Perform ATS analysis
        ats_score = ats_analyzer.analyze(resume_content, job_description)

        # Get AI suggestions
        try:
            suggestions = ai_suggestions.get_suggestions(resume_content, job_description)
            logger.debug(f"Generated {len(suggestions)} AI suggestions")
        except Exception as e:
            logger.error(f"Error getting AI suggestions: {str(e)}")
            suggestions = ["Error getting AI suggestions. Please try again later."]

        logger.debug(f"Rendering template with resume_id={resume_id}, job_id={job.id}")
        return render_template('partials/analysis_results.html',
                           resume_id=resume_id,
                           job_id=job.id,
                           ats_score=ats_score,
                           suggestions=suggestions)

    except Exception as e:
        logger.error(f"Error processing resume: {str(e)}")
        return render_template('partials/analysis_results.html',
                           error=f'Error processing resume: {str(e)}',
                           ats_score={'score': 0, 'matching_keywords': [], 'missing_keywords': []},
                           suggestions=[])

@app.route('/analyze', methods=['POST'])
@login_required
def analyze_resume():
    try:
        resume_id = request.form.get('resume_id')
        if resume_id is None or int(resume_id) not in resumes:
            return jsonify({'error': 'Invalid resume ID'}), 400

        resume = resumes[int(resume_id)]
        # Check if resume belongs to current user
        if resume['user_id'] != current_user.id:
            return jsonify({'error': 'Unauthorized access'}), 403

        ats_score = ats_analyzer.analyze(resume['content'], resume['job_description'])
        suggestions = ai_suggestions.get_suggestions(resume['content'], resume['job_description'])

        return jsonify({
            'ats_score': ats_score,
            'suggestions': suggestions
        })
    except Exception as e:
        logger.error(f"Error analyzing resume: {str(e)}")
        return jsonify({'error': 'Failed to analyze resume'}), 500

@app.route('/export/<int:resume_id>')
@app.route('/export/<int:resume_id>/<version>')
@login_required
def export_resume(resume_id, version='customized'):
    try:
        # Get the customized resume from database
        customized_resume = CustomizedResume.query.get_or_404(resume_id)

        # Check if the resume belongs to the current user
        if customized_resume.user_id != current_user.id:
            return render_template('error.html', message='Unauthorized access'), 403

        # Determine which content to export based on version parameter
        if version == 'original':
            content = customized_resume.original_content
            filename = f"original_resume_{resume_id}.md"
        else:
            content = customized_resume.customized_content
            filename = f"customized_resume_{resume_id}.md"

        # Create response with proper headers for download
        response = app.response_class(
            response=content,
            mimetype='text/markdown',
            status=200
        )
        response.headers.set('Content-Disposition', f'attachment; filename={filename}')
        return response

    except Exception as e:
        logger.error(f"Error exporting resume: {str(e)}")
        return render_template('error.html', message='Failed to export resume'), 500

@app.route('/customized-resume/<int:resume_id>')
@login_required
def view_customized_resume(resume_id):
    try:
        # Get the customized resume from database
        customized_resume = CustomizedResume.query.get_or_404(resume_id)

        # Check if the resume belongs to the current user
        if customized_resume.user_id != current_user.id:
            return render_template('error.html', message='Unauthorized access'), 403

        # Get the associated job description
        job = JobDescription.query.get(customized_resume.job_description_id)

        # This view now serves as a fallback for browsers with JavaScript disabled
        # For browsers with JavaScript enabled, we'll redirect to the comparison view
        return render_template('customized_resume.html',
                              resume=customized_resume,
                              job=job,
                              comparison_url=url_for('compare_resume', resume_id=resume_id),
                              title='Customized Resume')
    except Exception as e:
        logger.error(f"Error viewing customized resume: {str(e)}")
        return render_template('error.html', message='Failed to load customized resume'), 500

@app.route('/resume-comparison/<int:resume_id>')
@login_required
def compare_resume(resume_id):
    try:
        # Get the customized resume from database
        customized_resume = CustomizedResume.query.get_or_404(resume_id)

        # Check if the resume belongs to the current user
        if customized_resume.user_id != current_user.id:
            return render_template('error.html', message='Unauthorized access'), 403

        # Get the associated job description
        job = JobDescription.query.get(customized_resume.job_description_id)

        # Render the comparison template
        return render_template('customized_resume_comparison.html',
                               resume=customized_resume,
                               job=job,
                               title='Resume Comparison')
    except Exception as e:
        logger.error(f"Error comparing resume: {str(e)}")
        return render_template('error.html', message='Failed to load resume comparison'), 500

@app.route('/login')
def login():
    # Redirect to the auth blueprint's login route
    return redirect(url_for('auth.login'))

@app.route('/register')
def register():
    # Redirect to the auth blueprint's register route
    return redirect(url_for('auth.register'))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/partials/toggle-input')
def toggle_input():
    input_type = request.args.get('type', 'file')
    return render_template('partials/toggle_input.html', type=input_type)

@app.route('/partials/toggle-job-input')
def toggle_job_input():
    input_type = request.args.get('type', 'url')
    return render_template('partials/toggle_job_input.html', type=input_type)

# Simple database initialization
with app.app_context():
    try:
        # Ensure the database directory exists
        db_dir = os.path.dirname(db_path)
        os.makedirs(db_dir, exist_ok=True)
        
        # Before creating tables, explicitly set the database file permissions
        # First, touch the file to create it if it doesn't exist
        if not os.path.exists(db_path):
            with open(db_path, 'w') as f:
                pass
            logger.info(f"Created empty database file at {db_path}")
            
            # Set permissions on the file
            try:
                os.chmod(db_path, 0o666)  # rw-rw-rw-
                logger.info(f"Set permissions on database file to 0o666")
            except Exception as perm_ex:
                logger.error(f"Failed to set permissions on database file: {str(perm_ex)}")
        
        # Special handling for SQLite on network/shared drives like Dropbox
        # Set a longer timeout and enable WAL mode for better concurrency
        from sqlalchemy import event
        from sqlalchemy.engine import Engine
        import sqlite3
        
        @event.listens_for(Engine, "connect")
        def set_sqlite_pragma(dbapi_connection, connection_record):
            if isinstance(dbapi_connection, sqlite3.Connection):
                cursor = dbapi_connection.cursor()
                # Set a longer timeout for busy connections
                cursor.execute("PRAGMA busy_timeout = 30000")  # 30 seconds
                # Use WAL mode for better concurrency
                cursor.execute("PRAGMA journal_mode = WAL")
                cursor.close()
        
        # Create database tables
        db.create_all()
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {str(e)}")
        logger.error(f"Current directory: {os.getcwd()}")
        # Try to provide helpful information about potential issues
        try:
            # Check database status
            if os.path.exists(db_path):
                logger.info(f"Database file exists at {db_path}")
                logger.info(f"File permissions: {oct(os.stat(db_path).st_mode)}")
                # Try to open the file directly to diagnose issues
                try:
                    with open(db_path, 'rb+') as f:
                        logger.info("Successfully opened database file for read/write")
                except Exception as open_ex:
                    logger.error(f"Failed to open database file: {str(open_ex)}")
            else:
                logger.info(f"Database file does not exist yet at {db_path} (will be created)")
                logger.info(f"Instance folder permissions: {oct(os.stat(app.instance_path).st_mode)}")
                logger.info(f"Instance folder is writable: {os.access(app.instance_path, os.W_OK)}")
        except Exception as ex:
            logger.error(f"Error checking database info: {str(ex)}")