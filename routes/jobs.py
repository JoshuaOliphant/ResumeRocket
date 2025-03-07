from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from extensions import db
from models import JobDescription, CustomizedResume
from services.job_description_processor import JobDescriptionProcessor
from services.resume_customizer import ResumeCustomizer
from services.ats_analyzer import ATSAnalyzer
from services.ai_suggestions import AISuggestions
import logging

logger = logging.getLogger(__name__)
jobs_bp = Blueprint('jobs', __name__)
job_processor = JobDescriptionProcessor()
resume_customizer = ResumeCustomizer()
ats_analyzer = ATSAnalyzer()
ai_suggestions = AISuggestions()

@jobs_bp.route('/api/job/text', methods=['POST'])
@login_required
def submit_job_text():
    try:
        logger.debug("Processing job text submission")
        logger.debug(f"Form data received: {request.form}")
        logger.debug(f"Files received: {request.files}")

        # Get job description from form data
        content = request.form.get('content')
        if not content:
            return jsonify({'error': 'Job description content is required'}), 400

        # Process the job description
        processed = job_processor.process_text(content)
        logger.debug(f"Processed job description, length: {len(processed['content'])}")

        # Create new job description
        job = JobDescription(
            title=processed['title'] if 'title' in processed else 'Untitled Position',
            content=processed['content'],
            user_id=current_user.id
        )

        db.session.add(job)
        db.session.commit()
        logger.debug(f"Job description saved with ID: {job.id}")

        # Get resume content
        resume_content = request.form.get('resume', '').strip()
        resume_file = request.files.get('resume_file')

        if resume_file:
            logger.debug("Processing uploaded resume file")
            from services.file_parser import FileParser
            try:
                resume_content = FileParser.parse_to_markdown(resume_file)
                logger.debug(f"Successfully parsed resume file to markdown, length: {len(resume_content)}")
            except Exception as e:
                logger.error(f"Error parsing resume file: {str(e)}")
                return jsonify({'error': 'Failed to parse resume file. Please ensure it is a valid document.'}), 400

        # Analyze resume if provided
        if resume_content:
            logger.debug("Analyzing resume...")
            try:
                ats_score = ats_analyzer.analyze(resume_content, processed['content'])
                logger.debug(f"ATS analysis complete, score: {ats_score['score']}")

                suggestions = ai_suggestions.get_suggestions(resume_content, processed['content'])
                logger.debug(f"AI suggestions generated, count: {len(suggestions)}")
            except Exception as e:
                logger.error(f"Error during analysis: {str(e)}")
                return jsonify({'error': 'Failed to analyze resume. Please try again.'}), 500
        else:
            ats_score = {'score': 0, 'matching_keywords': [], 'missing_keywords': []}
            suggestions = []

        return jsonify({
            'message': 'Job description saved successfully',
            'job': job.to_dict(),
            'ats_score': ats_score,
            'suggestions': suggestions,
            'resume_content': resume_content
        }), 201

    except Exception as e:
        logger.error(f"Error processing job text: {str(e)}")
        return jsonify({'error': str(e)}), 500

@jobs_bp.route('/job/url', methods=['POST'])
@login_required
def submit_job_url():
    try:
        logger.debug("Processing job URL submission")
        logger.debug(f"Form data received: {request.form}")

        # Get URL from form data
        url = request.form.get('url')
        if not url:
            return jsonify({'error': 'Job posting URL is required'}), 400

        # Get resume content from form data
        resume_content = request.form.get('resume', '')
        resume_file = request.files.get('resume_file')

        if resume_file:
            from services.file_parser import FileParser
            is_valid, error_message = FileParser.allowed_file(resume_file)
            if not is_valid:
                return jsonify({'error': error_message}), 400
            try:
                resume_content = FileParser.parse_to_markdown(resume_file)
                logger.debug(f"Successfully parsed resume file to markdown, length: {len(resume_content)}")
            except Exception as e:
                logger.error(f"Error parsing resume file: {str(e)}")
                return jsonify({'error': 'Failed to parse resume file. Please ensure it is a valid document.'}), 400

        logger.debug(f"Received URL: {url}")
        logger.debug(f"Resume content received: {bool(resume_content)} (length: {len(resume_content) if resume_content else 0})")

        # Extract job description from URL
        logger.debug("Extracting job description from URL...")
        try:
            processed = job_processor.extract_from_url(url)
            logger.debug(f"Job description extracted, title: {processed['title']}, content length: {len(processed['content'])}")
        except Exception as e:
            logger.error(f"Error extracting job description from URL: {str(e)}")
            return jsonify({'error': 'Failed to extract job description from URL. Please ensure the URL is valid and accessible.'}), 400

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
            try:
                ats_score = ats_analyzer.analyze(resume_content, processed['content'])
                logger.debug(f"ATS analysis complete, score: {ats_score['score']}")

                logger.debug("Getting AI suggestions...")
                suggestions = ai_suggestions.get_suggestions(resume_content, processed['content'])
                logger.debug(f"AI suggestions generated, count: {len(suggestions)}")
            except Exception as e:
                logger.error(f"Error during resume analysis: {str(e)}")
                return jsonify({'error': 'Failed to analyze resume. Please try again.'}), 500
        else:
            logger.debug("No resume content provided, skipping analysis")
            ats_score = {'score': 0, 'matching_keywords': [], 'missing_keywords': []}
            suggestions = []

        return jsonify({
            'message': 'Job description saved successfully',
            'job': job.to_dict(),
            'ats_score': ats_score,
            'suggestions': suggestions,
            'resume_content': resume_content
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

@jobs_bp.route('/api/customize-resume', methods=['POST'])
@login_required
def customize_resume():
    try:
        logger.debug("Customizing resume, received data:")
        data = request.get_json()
        logger.debug(f"Request data: {data}")

        if not data:
            return jsonify({'error': 'No data provided'}), 400

        resume_content = data.get('resume_content')
        job_description_id = data.get('job_description_id')

        if not resume_content or not job_description_id:
            logger.error(f"Missing required data - resume_content: {bool(resume_content)}, job_description_id: {job_description_id}")
            return jsonify({'error': 'Resume content and job description ID are required'}), 400

        # Get the job description
        job_description = JobDescription.query.get(job_description_id)
        if not job_description:
            return jsonify({'error': 'Job description not found'}), 404

        # Verify ownership
        if job_description.user_id != current_user.id:
            return jsonify({'error': 'Unauthorized access'}), 403

        logger.debug(f"Customizing resume for job description ID: {job_description_id}")
        logger.debug(f"Resume content length: {len(resume_content)}")
        logger.debug(f"Job description content length: {len(job_description.content)}")

        # Generate customized resume
        result = resume_customizer.customize_resume(resume_content, job_description.content)
        logger.debug(f"Resume customization completed, result length: {len(result['customized_content'])}")

        # Store the customized resume
        customized_resume = CustomizedResume(
            original_content=resume_content,
            customized_content=result['customized_content'],
            ats_score=result['new_ats_score'],
            user_id=current_user.id,
            job_description_id=job_description_id
        )

        db.session.add(customized_resume)
        db.session.commit()
        logger.debug("Customized resume saved to database")

        return jsonify({
            'message': 'Resume customized successfully',
            'customized_resume': customized_resume.to_dict(),
            'original_ats_score': result['original_ats_score'],
            'new_ats_score': result['new_ats_score'],
            'improvement': result['improvement']
        }), 201

    except Exception as e:
        logger.error(f"Error customizing resume: {str(e)}")
        return jsonify({'error': str(e)}), 500