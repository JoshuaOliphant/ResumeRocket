import os
import logging
from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_required
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity
from services.ats_analyzer import ATSAnalyzer
from services.ai_suggestions import AISuggestions

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET")
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL", "sqlite:///app.db")
app.config['JWT_SECRET_KEY'] = os.environ.get("JWT_SECRET_KEY", app.secret_key)

# Initialize extensions
db = SQLAlchemy(app)
jwt = JWTManager(app)
login_manager = LoginManager(app)
login_manager.login_view = 'auth.login'

# Initialize services
ats_analyzer = ATSAnalyzer()
ai_suggestions = AISuggestions()

# In-memory storage for resumes
resumes = {}

@login_manager.user_loader
def load_user(user_id):
    from models import User
    return User.query.get(int(user_id))

# Register blueprints
from routes.auth import auth_bp
app.register_blueprint(auth_bp, url_prefix='/auth')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
@login_required
def upload_resume():
    try:
        # Debug logging
        logger.debug("Form data received: %s", request.form)

        resume_content = request.form.get('resume', '').strip()
        job_description = request.form.get('job_description', '').strip()

        logger.debug("Resume content length: %d", len(resume_content))
        logger.debug("Job description length: %d", len(job_description))

        if not resume_content or not job_description:
            return jsonify({
                'error': 'Resume and job description are required',
                'ats_score': {'score': 0, 'matching_keywords': [], 'missing_keywords': []},
                'suggestions': []
            }), 400

        # Store resume in memory with user ID
        resume_id = len(resumes)
        resumes[resume_id] = {
            'content': resume_content,
            'job_description': job_description,
            'user_id': get_jwt_identity()
        }

        # Perform ATS analysis
        ats_score = ats_analyzer.analyze(resume_content, job_description)

        # Get AI suggestions
        try:
            suggestions = ai_suggestions.get_suggestions(resume_content, job_description)
        except Exception as e:
            logger.error(f"Error getting AI suggestions: {str(e)}")
            suggestions = ["Error getting AI suggestions. Please try again later."]

        return jsonify({
            'resume_id': resume_id,
            'ats_score': ats_score,
            'suggestions': suggestions
        })
    except Exception as e:
        logger.error(f"Error processing resume: {str(e)}")
        return jsonify({
            'error': 'Failed to process resume. Please try again.',
            'ats_score': {'score': 0, 'matching_keywords': [], 'missing_keywords': []},
            'suggestions': []
        }), 500

@app.route('/analyze', methods=['POST'])
@login_required
def analyze_resume():
    try:
        resume_id = request.form.get('resume_id')
        if resume_id is None or int(resume_id) not in resumes:
            return jsonify({'error': 'Invalid resume ID'}), 400

        resume = resumes[int(resume_id)]
        # Check if resume belongs to current user
        if resume['user_id'] != get_jwt_identity():
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
        if resume['user_id'] != get_jwt_identity():
            return jsonify({'error': 'Unauthorized access'}), 403
        return jsonify({
            'content': resume['content']
        })
    except Exception as e:
        logger.error(f"Error exporting resume: {str(e)}")
        return jsonify({'error': 'Failed to export resume'}), 500

with app.app_context():
    db.create_all()