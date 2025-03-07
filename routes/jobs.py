from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from extensions import db
from models import JobDescription
from services.job_description_processor import JobDescriptionProcessor
from services.ats_analyzer import ATSAnalyzer
from services.ai_suggestions import AISuggestions
import logging

logger = logging.getLogger(__name__)
jobs_bp = Blueprint('jobs', __name__)
job_processor = JobDescriptionProcessor()
ats_analyzer = ATSAnalyzer()
ai_suggestions = AISuggestions()

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

        # Get resume analysis
        resume_content = request.form.get('resume')
        if resume_content:
            ats_score = ats_analyzer.analyze(resume_content, processed['content'])
            suggestions = ai_suggestions.get_suggestions(resume_content, processed['content'])
        else:
            ats_score = {'score': 0, 'matching_keywords': [], 'missing_keywords': []}
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

        # Get URL from form data
        url = request.form.get('url')
        if not url:
            return jsonify({'error': 'Job posting URL is required'}), 400

        # Get resume content from form data
        resume_content = request.form.get('resume', '').strip()

        logger.debug(f"Received URL: {url}")
        logger.debug(f"Resume content received: {bool(resume_content)} (length: {len(resume_content)})")

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