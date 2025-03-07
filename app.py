import os
import logging
from flask import Flask, render_template, request, jsonify
from services.ats_analyzer import ATSAnalyzer
from services.ai_suggestions import AISuggestions

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET")

# In-memory storage for resumes
resumes = {}

# Initialize services
ats_analyzer = ATSAnalyzer()
ai_suggestions = AISuggestions()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
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

        # Store resume in memory
        resume_id = len(resumes)
        resumes[resume_id] = {
            'content': resume_content,
            'job_description': job_description
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
def analyze_resume():
    try:
        resume_id = request.form.get('resume_id')
        if resume_id is None or int(resume_id) not in resumes:
            return jsonify({'error': 'Invalid resume ID'}), 400

        resume = resumes[int(resume_id)]
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
def export_resume():
    try:
        resume_id = request.form.get('resume_id')
        if resume_id is None or int(resume_id) not in resumes:
            return jsonify({'error': 'Invalid resume ID'}), 400

        resume = resumes[int(resume_id)]
        return jsonify({
            'content': resume['content']
        })
    except Exception as e:
        logger.error(f"Error exporting resume: {str(e)}")
        return jsonify({'error': 'Failed to export resume'}), 500