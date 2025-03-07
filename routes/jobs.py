from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from extensions import db
from models import JobDescription
from services.job_description_processor import JobDescriptionProcessor
import logging

logger = logging.getLogger(__name__)
jobs_bp = Blueprint('jobs', __name__)
job_processor = JobDescriptionProcessor()

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

        return jsonify({
            'message': 'Job description saved successfully',
            'job': job.to_dict()
        }), 201

    except Exception as e:
        logger.error(f"Error submitting job description text: {str(e)}")
        return jsonify({'error': 'Failed to process job description'}), 500

@jobs_bp.route('/job/url', methods=['POST'])
@login_required
def submit_job_url():
    try:
        data = request.get_json()
        if not data or not data.get('url'):
            return jsonify({'error': 'Job posting URL is required'}), 400

        url = data.get('url')

        # Extract job description from URL
        processed = job_processor.extract_from_url(url)

        # Create new job description
        job = JobDescription(
            title=processed['title'],
            content=processed['content'],
            url=url,
            user_id=current_user.id
        )

        db.session.add(job)
        db.session.commit()

        return jsonify({
            'message': 'Job description saved successfully',
            'job': job.to_dict()
        }), 201

    except Exception as e:
        logger.error(f"Error submitting job URL: {str(e)}")
        return jsonify({'error': 'Failed to process job URL'}), 500

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