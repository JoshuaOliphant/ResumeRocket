import os
import logging
from flask import Flask, render_template, request, jsonify, flash, redirect, url_for
from flask_login import LoginManager, login_required, current_user
from flask_jwt_extended import JWTManager
from flask_wtf.csrf import CSRFProtect
from services.ats_analyzer import ATSAnalyzer
from services.ai_suggestions import AISuggestions
from services.file_parser import FileParser
from services.resume_customizer import ResumeCustomizer
from extensions import db
from models import JobDescription, CustomizedResume

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET")
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL", "sqlite:///app.db")
app.config['JWT_SECRET_KEY'] = os.environ.get("JWT_SECRET_KEY", app.secret_key)

# Initialize CSRF protection
csrf = CSRFProtect(app)

# Configure SQLAlchemy for better connection handling
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    "pool_pre_ping": True,
    "pool_recycle": 300,
    "pool_timeout": 30,
    "max_overflow": 15
}

# Initialize extensions
db.init_app(app)
jwt = JWTManager(app)
login_manager = LoginManager(app)
login_manager.login_view = 'auth.login'

# Initialize services
ats_analyzer = ATSAnalyzer()
ai_suggestions = AISuggestions()
resume_customizer = ResumeCustomizer()

# In-memory storage for resumes
resumes = {}

@login_manager.user_loader
def load_user(user_id):
    from models import User
    return User.query.get(int(user_id))

# Register blueprints
from routes.auth import auth_bp
from routes.jobs import jobs_bp
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(jobs_bp, url_prefix='/api')

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
            # If URL is provided, fetch job description
            from services.job_description_processor import JobDescriptionProcessor
            processor = JobDescriptionProcessor()
            job_data = processor.extract_from_url(job_url)
            # Extract content from the returned dictionary
            job_description = job_data['content'] if isinstance(job_data, dict) else job_data
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

@app.route('/export', methods=['POST'])
@login_required
def export_resume():
    try:
        resume_id = request.form.get('resume_id')
        if resume_id is None or int(resume_id) not in resumes:
            return jsonify({'error': 'Invalid resume ID'}), 400

        resume = resumes[int(resume_id)]
        if resume['user_id'] != current_user.id:
            return jsonify({'error': 'Unauthorized access'}), 403
        return jsonify({
            'content': resume['content']
        })
    except Exception as e:
        logger.error(f"Error exporting resume: {str(e)}")
        return jsonify({'error': 'Failed to export resume'}), 500

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

        return render_template('customized_resume.html',
                                resume=customized_resume,
                                job=job,
                                title='Customized Resume')
    except Exception as e:
        logger.error(f"Error viewing customized resume: {str(e)}")
        return render_template('error.html', message='Failed to load customized resume'), 500


@app.route('/api/customize-resume', methods=['POST'])
@login_required
def customize_resume_endpoint():
    try:
        logger.debug(f"Form data received: {request.form}")

        # Handle both form data and JSON requests
        data = request.get_json(silent=True) if request.is_json else request.form
        resume_id = data.get('resume_id')
        job_id = data.get('job_id')

        logger.debug(f"Raw values - resume_id: {resume_id}, job_id: {job_id}")

        if not resume_id or not job_id:
            error_msg = 'Both resume and job information are required'
            logger.error(f"Missing required IDs - {error_msg}")
            if request.headers.get('HX-Request'):
                flash(error_msg, 'error')
                return redirect(url_for('index'))
            return jsonify({'error': error_msg}), 400

        try:
            resume_id = int(resume_id)
            job_id = int(job_id)
        except (TypeError, ValueError) as e:
            error_msg = 'Invalid resume or job ID format'
            logger.error(f"Invalid ID format: {str(e)}")
            if request.headers.get('HX-Request'):
                flash(error_msg, 'error')
                return redirect(url_for('index'))
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

        # Return appropriate response based on request type
        if request.headers.get('HX-Request'):
            return redirect(url_for('view_customized_resume', resume_id=customized_resume.id))
        return jsonify({
            'success': True,
            'redirect': url_for('view_customized_resume', resume_id=customized_resume.id)
        })

    except Exception as e:
        logger.error(f"Error customizing resume: {str(e)}")
        error_msg = f'Error customizing resume: {str(e)}'
        if request.headers.get('HX-Request'):
            flash(error_msg, 'error')
            return redirect(url_for('index'))
        return jsonify({'error': error_msg}), 500

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/')
def index():
    return render_template('index.html')

with app.app_context():
    db.create_all()