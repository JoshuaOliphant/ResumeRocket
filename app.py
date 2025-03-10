import os
import secrets
import logging
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session, send_file
from flask import make_response
from flask_login import LoginManager, login_required, login_user, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import JWTManager
from flask_wtf.csrf import CSRFProtect
from flask_wtf import FlaskForm
from wtforms import HiddenField
from services.ats_analyzer import EnhancedATSAnalyzer
from services.ai_suggestions import AISuggestions
from services.file_parser import FileParser
from services.resume_customizer import ResumeCustomizer
from extensions import db
from models import JobDescription, CustomizedResume, User, ABTest, OptimizationSuggestion
from io import BytesIO
from sqlalchemy import func
from functools import wraps

# Import blueprints
from routes.auth import auth_bp
from routes.jobs import jobs_bp

# Import the feedback loop service
from services.feedback_loop import FeedbackLoop

logging.basicConfig(level=logging.DEBUG, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("app")

# Create Flask app
app = Flask(__name__)
# Set the absolute path for the database
db_path = os.path.join(os.getcwd(), 'resumerocket.db')
print(f"Using database at: {db_path}")

app.config.from_mapping(
    SECRET_KEY=os.environ.get('SECRET_KEY', 'dev_key'),
    SQLALCHEMY_DATABASE_URI=f"sqlite:///{db_path}",
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
    JWT_SECRET_KEY=os.environ.get('JWT_SECRET_KEY', 'jwt_dev_key'),
    UPLOAD_FOLDER=os.path.join(os.getcwd(), 'uploads'),
    MAX_CONTENT_LENGTH=16 * 1024 * 1024  # 16MB max file size
)

# Initialize Flask extensions
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'
jwt = JWTManager(app)
csrf = CSRFProtect(app)

# Define default format for empty ATS result
DEFAULT_ATS_RESULT = {
    'score': 0, 
    'confidence': 'low',
    'matching_keywords': [], 
    'missing_keywords': [],
    'section_scores': {},
    'job_type': 'unknown',
    'suggestions': []
}

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Register blueprints
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(jobs_bp, url_prefix='/api')

# Initialize services
ats_analyzer = EnhancedATSAnalyzer()
ai_suggestions = AISuggestions()
resume_customizer = ResumeCustomizer()
file_parser = FileParser()  # Create an instance of FileParser

# In-memory storage for resumes
resumes = {}

# Initialize the feedback loop service
feedback_loop = FeedbackLoop()

# Define form classes
class ResumeAnalysisForm(FlaskForm):
    resume_id = HiddenField('Resume ID')
    job_id = HiddenField('Job ID')

# Admin required decorator
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('You do not have permission to access this page.', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    return render_template('index.html', title='ResumeRocket - ATS-Optimized Resumes')

@app.route('/customize-resume', methods=['POST'])
@login_required
def customize_resume_endpoint():
    try:
        logger.debug("Handling customize-resume request")
        # Check if we received JSON or form data
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
        file_format = resumes[resume_id].get('file_format', 'md')
        original_bytes = resumes[resume_id].get('original_bytes')
        logger.debug(f"Found original resume content with format: {file_format}")

        # Generate customized resume
        customization_result = resume_customizer.customize_resume(
            original_content,
            job.content
        )
        logger.debug("Generated customized resume content")

        # Get results from the enhanced ResumeCustomizer
        ats_score = customization_result['new_score']
        matching_keywords = customization_result['matching_keywords']
        missing_keywords = customization_result['missing_keywords']
        comparison_data = customization_result.get('comparison_data', {})
        
        # Count of added keywords and total changes
        added_keywords_count = len(comparison_data.get('added_keywords', []))
        changes_count = comparison_data.get('total_changes', 0)
        
        logger.debug(f"Customization added {added_keywords_count} keywords with {changes_count} total changes")
        
        # Create new customized resume record
        customized_resume = CustomizedResume(
            original_content=original_content,
            customized_content=customization_result['customized_content'],
            job_description_id=job.id,
            user_id=current_user.id,
            original_ats_score=customization_result['original_score'],
            ats_score=ats_score,
            matching_keywords=matching_keywords,
            missing_keywords=missing_keywords,
            file_format=file_format,
            original_bytes=original_bytes,
            comparison_data=comparison_data,
            added_keywords_count=added_keywords_count,
            changes_count=changes_count
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
            flash(error_msg, 'error')
            return render_template('partials/error.html', error=error_msg)
        return jsonify({'error': error_msg}), 500

@app.route('/api/process_resume', methods=['POST'])
@login_required
def process_resume():
    try:
        # Extract resume and job description
        if not request.form:
            return jsonify({'error': 'No form data provided'}), 400

        resume_text = request.form.get('resume')
        job_description = request.form.get('job_description')
        
        # Validate input
        if not resume_text:
            return jsonify({'error': 'Resume text is required'}), 400
        if not job_description:
            return jsonify({'error': 'Job description is required'}), 400
            
        logger.debug(f"Processing resume, text length: {len(resume_text)}")
        logger.debug(f"Processing job description, text length: {len(job_description)}")
        
        # Generate a resume ID
        resume_id = len(resumes)
        resumes[resume_id] = {
            'content': resume_text,
            'job_description': job_description,
            'user_id': current_user.id,
            'file_format': 'md'  # Default to markdown for text input
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
        ats_score = ats_analyzer.analyze(resume_text, job_description)

        # Get AI suggestions
        try:
            suggestions = ai_suggestions.get_suggestions(resume_text, job_description)
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
                           ats_score=DEFAULT_ATS_RESULT,
                           suggestions=[])

@app.route('/api/analyze_resume', methods=['POST'])
@login_required
def analyze_resume_endpoint():
    try:
        # Debug log the incoming form data
        logger.debug(f"Form data received: {request.form}")
        logger.debug(f"Files received: {request.files}")
        
        # Check if resume is uploaded as a file or provided as text
        if 'resume_file' in request.files and request.files['resume_file'].filename:
            file = request.files['resume_file']
            logger.debug(f"Resume file received: {file.filename}")
            
            # Validate file
            is_valid, error_message = file_parser.allowed_file(file)
            if not is_valid:
                return jsonify({'error': error_message}), 400
                
            # Parse file content to markdown
            resume_content, original_file_bytes, file_format = file_parser.parse_file_with_format(file)
            
        elif 'resume' in request.form and request.form['resume'].strip():
            resume_content = request.form['resume']
            file_format = 'md'  # Default to markdown for text input
            original_file_bytes = resume_content.encode('utf-8')
        else:
            return jsonify({'error': 'No resume provided. Please upload a file or enter text.'}), 400

        # Store resume in memory with user ID
        resume_id = len(resumes)
        resumes[resume_id] = {
            'content': resume_content,
            'job_description': None,
            'user_id': current_user.id,
            'file_format': file_format,
            'original_bytes': original_file_bytes
        }

        # Process job description from URL or text
        job_description = None
        job_url = request.form.get('job_url', '').strip()
        
        if job_url:
            try:
                # Basic cleanup of URL format - add https:// if missing
                if not job_url.startswith(('http://', 'https://')):
                    job_url = 'https://' + job_url
                
                # Fetch job description from URL
                from services.job_description_processor import JobDescriptionProcessor
                processor = JobDescriptionProcessor()
                job_data = processor.extract_from_url(job_url)
                # Extract content from the returned dictionary
                job_description = job_data.get('content', '') if isinstance(job_data, dict) else job_data
                
                logger.debug(f"Job description extracted from URL. Length: {len(job_description or '')}")
            except Exception as e:
                logger.error(f"Error fetching job description from URL: {str(e)}")
                job_description = "Failed to fetch job description from URL."
        else:
            # Get job description from form text input
            job_description = request.form.get('job_description', '').strip()
        
        # Create job description (use a placeholder if no content available)
        job = JobDescription(
            title="Job Description",
            content=job_description or "No job description provided",
            url=job_url if job_url else None,
            user_id=current_user.id
        )
        db.session.add(job)
        db.session.commit()

        # Update the resume's job description reference
        resumes[resume_id]['job_description'] = job_description
        
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
                           ats_score=DEFAULT_ATS_RESULT,
                           suggestions=[])

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

        # Get the file format
        file_format = customized_resume.file_format or 'md'
        
        # Determine which content to export based on version and format
        if version == 'original':
            # If format is markdown or the original bytes are not available, return markdown
            if file_format == 'md' or not customized_resume.original_bytes:
                content = customized_resume.original_content
                filename = f"original_resume_{resume_id}.md"
                mimetype = 'text/markdown'
            else:
                # For DOCX or PDF, return the original binary file
                content = customized_resume.original_bytes
                extension = file_format
                filename = f"original_resume_{resume_id}.{extension}"
                if file_format == 'docx':
                    mimetype = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
                elif file_format == 'pdf':
                    mimetype = 'application/pdf'
                else:
                    mimetype = 'application/octet-stream'
        else:
            # For customized version
            if file_format == 'md':
                # If original was markdown, export as markdown
                content = customized_resume.customized_content
                filename = f"customized_resume_{resume_id}.md"
                mimetype = 'text/markdown'
            elif file_format == 'docx':
                # If original was DOCX, convert the customized markdown back to DOCX
                try:
                    content = file_parser.markdown_to_docx(customized_resume.customized_content)
                    filename = f"customized_resume_{resume_id}.docx"
                    mimetype = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
                except Exception as e:
                    logger.error(f"Error converting to DOCX: {str(e)}")
                    # Fallback to markdown if conversion fails
                    content = customized_resume.customized_content
                    filename = f"customized_resume_{resume_id}.md"
                    mimetype = 'text/markdown'
            elif file_format == 'pdf':
                # Convert the customized markdown to PDF
                try:
                    content = file_parser.markdown_to_pdf(customized_resume.customized_content)
                    filename = f"customized_resume_{resume_id}.pdf"
                    mimetype = 'application/pdf'
                except Exception as e:
                    logger.error(f"Error converting to PDF: {str(e)}")
                    # Fallback to markdown if conversion fails
                    content = customized_resume.customized_content
                    filename = f"customized_resume_{resume_id}.md"
                    mimetype = 'text/markdown'
                    flash('Error creating PDF. Exporting as Markdown instead.', 'warning')
            else:
                content = customized_resume.customized_content
                filename = f"customized_resume_{resume_id}.md"
                mimetype = 'text/markdown'

        # Create response with proper headers for download
        response = app.response_class(
            response=content,
            mimetype=mimetype,
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

@app.route('/compare/<int:resume_id>')
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

        return render_template('customized_resume_comparison.html',
                              resume=customized_resume,
                              job=job,
                              title='Resume Comparison')
    except Exception as e:
        logger.error(f"Error viewing resume comparison: {str(e)}")
        return render_template('error.html', message='Failed to load resume comparison'), 500
        
@app.route('/download/<int:resume_id>/<format>')
@login_required
def download_resume(resume_id, format):
    try:
        # Get the customized resume from database
        customized_resume = CustomizedResume.query.get_or_404(resume_id)

        # Check if the resume belongs to the current user
        if customized_resume.user_id != current_user.id:
            return render_template('error.html', message='Unauthorized access'), 403

        # Determine which content to export based on format
        if format == 'md':
            content = customized_resume.customized_content
            filename = f"customized_resume_{resume_id}.md"
            mimetype = 'text/markdown'
        elif format == 'docx':
            try:
                content = file_parser.markdown_to_docx(customized_resume.customized_content)
                filename = f"customized_resume_{resume_id}.docx"
                mimetype = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
            except Exception as e:
                logger.error(f"Error converting to DOCX: {str(e)}")
                content = customized_resume.customized_content
                filename = f"customized_resume_{resume_id}.md"
                mimetype = 'text/markdown'
                flash('Error creating DOCX. Downloading as Markdown instead.', 'warning')
        elif format == 'pdf':
            try:
                content = file_parser.markdown_to_pdf(customized_resume.customized_content)
                filename = f"customized_resume_{resume_id}.pdf"
                mimetype = 'application/pdf'
            except Exception as e:
                logger.error(f"Error converting to PDF: {str(e)}")
                content = customized_resume.customized_content
                filename = f"customized_resume_{resume_id}.md"
                mimetype = 'text/markdown'
                flash('Error creating PDF. Downloading as Markdown instead.', 'warning')
        else:
            return render_template('error.html', message='Invalid format specified'), 400

        # Create response with proper headers for download
        response = make_response(content)
        response.headers.set('Content-Type', mimetype)
        response.headers.set('Content-Disposition', f'attachment; filename={filename}')
        return response

    except Exception as e:
        logger.error(f"Error downloading resume: {str(e)}")
        return render_template('error.html', message='Failed to download resume'), 500

# Route for user to provide feedback on a customized resume
@app.route('/api/feedback/<int:resume_id>', methods=['POST'])
@login_required
@csrf.exempt  # Exempt this route from CSRF protection since we're handling it manually in the AJAX request
def submit_resume_feedback(resume_id):
    try:
        # Get the customized resume
        customized_resume = CustomizedResume.query.get_or_404(resume_id)
        
        # Check if the resume belongs to the current user
        if customized_resume.user_id != current_user.id:
            return jsonify({'error': 'Unauthorized access'}), 403
        
        # Get data from request
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Update resume with feedback
        customized_resume.user_rating = data.get('rating')
        customized_resume.user_feedback = data.get('feedback')
        customized_resume.was_effective = data.get('was_effective')
        customized_resume.interview_secured = data.get('interview_secured')
        customized_resume.job_secured = data.get('job_secured')
        customized_resume.feedback_date = datetime.utcnow()
        
        db.session.commit()
        
        # Trigger evaluation if enough feedback is provided
        if customized_resume.user_rating and customized_resume.user_feedback:
            result = feedback_loop.evaluate_customization(resume_id)
            logger.info(f"Evaluation triggered for resume ID {resume_id}")
        
        return jsonify({
            'success': True,
            'message': 'Feedback submitted successfully'
        }), 200
        
    except Exception as e:
        logger.error(f"Error submitting feedback: {str(e)}")
        return jsonify({'error': f'Failed to submit feedback: {str(e)}'}), 500

@app.route('/admin/feedback-loop/evaluations', methods=['GET'])
@login_required
@admin_required
def list_evaluations():
    # Check if user is admin (implement proper admin check in production)
    if not current_user.is_admin:
        return jsonify({'error': 'Unauthorized access'}), 403
    
    # Get evaluations
    evaluations = CustomizationEvaluation.query.order_by(CustomizationEvaluation.created_at.desc()).limit(50).all()
    evaluations_data = [evaluation.to_dict() for evaluation in evaluations]
    
    return jsonify({
        'success': True,
        'evaluations': evaluations_data,
        'count': len(evaluations_data)
    }), 200

@app.route('/admin/feedback-loop/optimize', methods=['POST'])
@login_required
@admin_required
def trigger_optimization():
    # Check if user is admin (implement proper admin check in production)
    if not current_user.is_admin:
        return jsonify({'error': 'Unauthorized access'}), 403
    
    # Get min evaluations from request, default to 50
    data = request.get_json() or {}
    min_evaluations = data.get('min_evaluations', 50)
    
    # Trigger optimization
    result = feedback_loop.optimize_customization_strategy(min_evaluations)
    
    return jsonify(result), 200 if result.get('success', False) else 400

@app.route('/admin/feedback-loop/ab-test/<int:optimization_id>', methods=['POST'])
@login_required
@admin_required
def create_ab_test(optimization_id):
    # Check if user is admin (implement proper admin check in production)
    if not current_user.is_admin:
        return jsonify({'error': 'Unauthorized access'}), 403
    
    # Create A/B test
    result = feedback_loop.implement_ab_testing(optimization_id)
    
    return jsonify(result), 200 if 'error' not in result else 400

@app.route('/admin/feedback-loop/ab-test/<int:test_id>/analyze', methods=['POST'])
@login_required
@admin_required
def analyze_ab_test(test_id):
    # Check if user is admin (implement proper admin check in production)
    if not current_user.is_admin:
        return jsonify({'error': 'Unauthorized access'}), 403
    
    # Analyze A/B test
    result = feedback_loop.analyze_ab_test_results(test_id)
    
    return jsonify(result), 200 if 'error' not in result else 400

@app.route('/admin/feedback-loop/ab-test/<int:test_id>/apply/<int:optimization_id>', methods=['POST'])
@login_required
@admin_required
def apply_ab_test_winner(test_id, optimization_id):
    # Check if user is admin (implement proper admin check in production)
    if not current_user.is_admin:
        return jsonify({'error': 'Unauthorized access'}), 403
    
    # Apply winning variant
    result = feedback_loop.apply_winning_variant(test_id, optimization_id)
    
    return jsonify(result), 200 if 'error' not in result else 400

@app.route('/admin/feedback-loop/dashboard', methods=['GET'])
@login_required
@admin_required
def feedback_loop_dashboard():
    # Get statistics
    total_customizations = CustomizedResume.query.count()
    avg_improvement = db.session.query(func.avg(CustomizedResume.ats_score - CustomizedResume.original_ats_score)).scalar() or 0
    
    # Get feedback statistics
    feedback_count = CustomizedResume.query.filter(CustomizedResume.user_rating.isnot(None)).count()
    avg_rating = db.session.query(func.avg(CustomizedResume.user_rating)).scalar() or 0
    
    # Get active A/B tests
    active_tests = ABTest.query.filter_by(is_active=True).all()
    completed_tests = ABTest.query.filter_by(is_active=False).all()
    
    # Get optimization suggestions
    optimizations = OptimizationSuggestion.query.order_by(OptimizationSuggestion.created_at.desc()).limit(10).all()
    
    return render_template(
        'admin/feedback_dashboard.html',
        stats={
            'total_customizations': total_customizations,
            'avg_improvement': round(avg_improvement, 2),
            'feedback_count': feedback_count,
            'feedback_rate': round((feedback_count / total_customizations * 100), 2) if total_customizations > 0 else 0,
            'avg_rating': round(avg_rating, 1)
        },
        active_tests=active_tests,
        completed_tests=completed_tests,
        optimizations=optimizations
    )

@app.route('/admin/users', methods=['GET'])
@login_required
@admin_required
def admin_users():
    """Admin page to manage users and admin privileges."""
    users = User.query.all()
    return render_template('admin/users.html', users=users)

@app.route('/admin/users/<int:user_id>/toggle-admin', methods=['POST'])
@login_required
@admin_required
def toggle_admin(user_id):
    """Toggle admin status for a user."""
    user = User.query.get_or_404(user_id)
    
    # Prevent removing admin status from yourself
    if user.id == current_user.id:
        flash('You cannot remove your own admin privileges.', 'danger')
        return redirect(url_for('admin_users'))
    
    user.is_admin = not user.is_admin
    db.session.commit()
    
    action = "granted" if user.is_admin else "revoked"
    flash(f'Admin privileges {action} for {user.username}.', 'success')
    return redirect(url_for('admin_users'))

@app.route('/dashboard', methods=['GET'])
@login_required
def user_dashboard():
    """
    Display all customized resumes for the logged-in user, 
    along with job details and improvement metrics.
    """
    # Get all customized resumes for the current user, ordered by creation date (newest first)
    resumes = CustomizedResume.query.filter_by(user_id=current_user.id).order_by(CustomizedResume.created_at.desc()).all()
    
    # For each resume, retrieve the associated job description
    dashboard_data = []
    for resume in resumes:
        job = JobDescription.query.get(resume.job_description_id)
        if job:
            # Calculate improvement percentage
            improvement = 0
            if resume.original_ats_score and resume.ats_score:
                improvement = resume.ats_score - resume.original_ats_score
            
            dashboard_data.append({
                'resume': resume,
                'job': job,
                'improvement': round(improvement, 1),
                'date': resume.created_at.strftime('%Y-%m-%d %H:%M')
            })
    
    # Calculate overall statistics
    total_resumes = len(dashboard_data)
    avg_improvement = sum(item['improvement'] for item in dashboard_data) / total_resumes if total_resumes > 0 else 0
    
    return render_template('user_dashboard.html', 
                          dashboard_data=dashboard_data, 
                          total_resumes=total_resumes,
                          avg_improvement=round(avg_improvement, 1))

@app.route('/resume/<int:resume_id>/delete', methods=['GET'])
@login_required
def delete_resume(resume_id):
    """
    Delete a customized resume if it belongs to the current user.
    """
    resume = CustomizedResume.query.get_or_404(resume_id)
    
    # Check if the resume belongs to the current user
    if resume.user_id != current_user.id:
        flash('You do not have permission to delete this resume.', 'danger')
        return redirect(url_for('user_dashboard'))
    
    try:
        db.session.delete(resume)
        db.session.commit()
        flash('Resume deleted successfully.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting resume: {str(e)}', 'danger')
        app.logger.error(f"Error deleting resume ID {resume_id}: {str(e)}")
    
    return redirect(url_for('user_dashboard'))

# Simple database initialization
with app.app_context():
    try:
        # Check if we can connect to the database
        import sqlite3
        from sqlalchemy import inspect
        
        # Check if tables exist instead of creating them automatically
        inspector = inspect(db.engine)
        tables_exist = inspector.get_table_names()
        
        if not tables_exist:
            logger.warning("Database tables not found. Creating tables...")
            db.create_all()
            logger.info("Database tables created successfully")
            
        logger.info(f"Database tables found: {tables_exist}")
    except Exception as e:
        logger.error(f"Error checking database tables: {str(e)}")
        logger.error(f"Current directory: {os.getcwd()}")
        # Try to provide helpful information about potential issues
        try:
            # Check database status
            if 'sqlite' in app.config['SQLALCHEMY_DATABASE_URI'].lower():
                logger.info("Using SQLite database")
                db_path = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
                logger.info(f"Database path: {db_path}")
                
                if not os.path.isabs(db_path):
                    abs_path = os.path.abspath(db_path)
                    logger.info(f"Absolute database path: {abs_path}")
                    
                if os.path.exists(db_path):
                    logger.info(f"Database file exists. Size: {os.path.getsize(db_path)}")
                else:
                    logger.warning("Database file does not exist")
            else:
                logger.info(f"Using database: {app.config['SQLALCHEMY_DATABASE_URI']}")
        except Exception as ex:
            logger.error(f"Error checking database status: {str(ex)}")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)