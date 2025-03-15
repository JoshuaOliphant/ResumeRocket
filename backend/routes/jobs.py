from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from backend.extensions import db
from backend.models import JobDescription, CustomizedResume
from backend.services.job_description_processor import JobDescriptionProcessor
from backend.services.ats_analyzer import EnhancedATSAnalyzer
from backend.services.ai_suggestions import AISuggestions
from backend.services.resume_customizer import ResumeCustomizer
from backend.services.file_parser import FileParser
import logging

logger = logging.getLogger(__name__)
jobs_bp = Blueprint('jobs', __name__)
job_processor = JobDescriptionProcessor()
ats_analyzer = EnhancedATSAnalyzer()
ai_suggestions = AISuggestions()
resume_customizer = ResumeCustomizer()
file_parser = FileParser()

def handle_job_url_submission(job_url, resume_content=None):
    """
    Process a job URL submission and create a job description record.
    Can be called from other blueprints.
    
    Args:
        job_url: URL of the job posting to process
        resume_content: Optional resume content for context
        
    Returns:
        Dict with job_id on success or error message on failure
    """
    try:
        if not job_url:
            return {'error': 'Job URL is required'}
            
        # Process the job URL
        job_data = job_processor.extract_from_url(job_url)
        
        if not job_data or not job_data.get('content'):
            return {'error': 'Failed to extract job description from URL'}
            
        # Create new job description
        job = JobDescription(
            title=job_data.get('title', 'Job from URL'),
            content=job_data.get('content'),
            url=job_url,
            user_id=current_user.id
        )
        
        db.session.add(job)
        db.session.commit()
        
        return {'job_id': job.id}
    except Exception as e:
        logger.error(f"Error processing job URL: {str(e)}")
        return {'error': f'Error processing job URL: {str(e)}'}

@jobs_bp.route('/job/text', methods=['POST'])
@login_required
def submit_job_text():
    try:
        data = request.get_json()
        if not data or not data.get('content'):
            return jsonify({'error': 'Job description content is required'}), 400

        title = data.get('title')
        content = data.get('content')

        # Process the job description
        processed = job_processor.process_text(content, title)

        # Create new job description
        job = JobDescription(
            title=processed['title'],
            content=processed['content'],
            user_id=current_user.id
        )

        db.session.add(job)
        db.session.commit()

        # Get resume analysis if resume_id is provided
        resume_id = data.get('resume_id')
        if resume_id is not None:
            from app import resumes
            if resume_id in resumes:
                resume_content = resumes[resume_id]['content']
                ats_score = ats_analyzer.analyze(resume_content, processed['content'])
                suggestions = ai_suggestions.get_suggestions(resume_content, processed['content'])
            else:
                ats_score = {
                    'score': 0, 
                    'confidence': 'low',
                    'matching_keywords': [], 
                    'missing_keywords': [],
                    'section_scores': {},
                    'job_type': 'unknown',
                    'suggestions': []
                }
                suggestions = []
        else:
            ats_score = {
                'score': 0, 
                'confidence': 'low',
                'matching_keywords': [], 
                'missing_keywords': [],
                'section_scores': {},
                'job_type': 'unknown',
                'suggestions': []
            }
            suggestions = []

        return jsonify({
            'message': 'Job description saved successfully',
            'job': job.to_dict(),
            'ats_score': ats_score,
            'suggestions': suggestions
        }), 201

    except Exception as e:
        logger.error(f"Error submitting job description text: {str(e)}")
        return jsonify({'error': str(e)}), 500

@jobs_bp.route('/job/url', methods=['POST'])
@login_required
def submit_job_url():
    try:
        logger.debug("Processing job URL submission")
        logger.debug(f"Form data received: {request.form}")

        # Get URL from form data
        url = request.form.get('job_url', '')
        if not url:
            logger.error("No URL provided")
            return jsonify({'error': 'No URL provided'}), 400

        # Get resume content from form data
        resume_content = request.form.get('resume', '')
        resume_file = request.files.get('resume_file')

        if resume_file:
            is_valid, error_message = file_parser.allowed_file(resume_file)
            if not is_valid:
                return jsonify({'error': error_message}), 400
            resume_content = file_parser.parse_to_markdown(resume_file)

        logger.debug(f"Received URL: {url}")
        logger.debug(f"Resume content received: {bool(resume_content)} (length: {len(resume_content) if resume_content else 0})")

        # Extract job description from URL
        logger.debug("Extracting job description from URL...")
        processed = job_processor.extract_from_url(url)
        logger.debug(f"Job description extracted, title: {processed['title']}, content length: {len(processed['content'])}")

        # Create new job description
        job = JobDescription(
            title=processed['title'],
            content=processed['content'],
            url=url,
            user_id=current_user.id
        )

        db.session.add(job)
        db.session.commit()
        logger.debug(f"Job description saved to database with ID: {job.id}")

        # Get resume analysis if resume content is provided
        if resume_content:
            logger.debug("Analyzing resume against job description...")
            ats_score = ats_analyzer.analyze(resume_content, processed['content'])
            logger.debug(f"ATS analysis complete, score: {ats_score['score']}")

            logger.debug("Getting AI suggestions...")
            suggestions = ai_suggestions.get_suggestions(resume_content, processed['content'])
            logger.debug(f"AI suggestions generated, count: {len(suggestions)}")
        else:
            logger.debug("No resume content provided, skipping analysis")
            ats_score = {'score': 0, 'matching_keywords': [], 'missing_keywords': []}
            suggestions = []

        return jsonify({
            'message': 'Job description saved successfully',
            'job': job.to_dict(),
            'ats_score': ats_score,
            'suggestions': suggestions
        }), 201

    except Exception as e:
        logger.error(f"Error submitting job URL: {str(e)}")
        return jsonify({'error': str(e)}), 500

@jobs_bp.route('/jobs', methods=['GET'])
@login_required
def get_jobs():
    try:
        jobs = JobDescription.query.filter_by(user_id=current_user.id).order_by(JobDescription.created_at.desc()).all()
        return jsonify({
            'jobs': [job.to_dict() for job in jobs]
        })
    except Exception as e:
        logger.error(f"Error fetching jobs: {str(e)}")
        return jsonify({'error': 'Failed to fetch jobs'}), 500

@jobs_bp.route('/customize-resume-v2', methods=['POST'])
@login_required
def customize_resume():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        resume_id = data.get('resume_id')
        job_id = data.get('job_id')

        if not resume_id or not job_id:
            return jsonify({'error': 'Both resume_id and job_id are required'}), 400

        # Get the job description
        job = JobDescription.query.get(job_id)
        if not job or job.user_id != current_user.id:
            return jsonify({'error': 'Invalid job description or unauthorized access'}), 404

        # Get the original resume content from memory storage
        from app import resumes
        if resume_id not in resumes or resumes[resume_id]['user_id'] != current_user.id:
            return jsonify({'error': 'Invalid resume or unauthorized access'}), 404

        original_content = resumes[resume_id]['content']

        # Generate customized resume
        customization_result = resume_customizer.customize_resume(
            original_content,
            job.content
        )

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

        return jsonify({
            'message': 'Resume customized successfully',
            'customized_resume': customized_resume.to_dict()
        }), 201

    except Exception as e:
        logger.error(f"Error customizing resume: {str(e)}")
        return jsonify({'error': str(e)}), 500