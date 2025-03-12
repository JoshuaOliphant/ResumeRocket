from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session, send_file, Response, stream_with_context, current_app, make_response
from flask_login import login_required, current_user
from datetime import datetime
from io import BytesIO
import json
import uuid
from extensions import db
from models import JobDescription, CustomizedResume, User, OptimizationSuggestion
from services.file_parser import FileParser
from services.ats_analyzer import EnhancedATSAnalyzer
from services.ai_suggestions import AISuggestions
from services.resume_customizer import ResumeCustomizer
import logging
from routes.jobs import handle_job_url_submission, jobs_bp
import os
import time
import base64
import re
import threading
from werkzeug.utils import secure_filename
from markupsafe import Markup

# Initialize logger
logger = logging.getLogger(__name__)

# Initialize services
file_parser = FileParser()
ats_analyzer = EnhancedATSAnalyzer()
ai_suggestions = AISuggestions()
resume_customizer = ResumeCustomizer()

# Create resume blueprint
resume_bp = Blueprint('resume', __name__)

def generate_simple_customization_notes(optimization_plan, comparison_data, level, industry=None):
    """
    Generate basic HTML notes explaining customization changes when the
    full customization_notes are not available from the customization_result.
    """
    try:
        notes = []
        
        # Ensure optimization_plan and comparison_data are dictionaries
        if isinstance(optimization_plan, str):
            try:
                optimization_plan = json.loads(optimization_plan)
            except:
                optimization_plan = {}
                
        if isinstance(comparison_data, str):
            try:
                comparison_data = json.loads(comparison_data)
            except:
                comparison_data = {}
        
        # Overall summary
        if optimization_plan and 'summary' in optimization_plan:
            notes.append(f"<h5 class='text-lg font-semibold mt-2 mb-1'>Summary</h5>")
            notes.append(f"<p class='mb-2'>{optimization_plan.get('summary', 'Resume customized to better match the job requirements.')}</p>")
        
        # Add job analysis
        if optimization_plan and 'job_analysis' in optimization_plan:
            notes.append(f"<h5 class='text-lg font-semibold mt-4 mb-1'>Job Analysis</h5>")
            notes.append(f"<p class='mb-2'>{optimization_plan.get('job_analysis', 'Analysis of key job requirements and their alignment with your resume.')}</p>")
        
        # Customization approach
        notes.append(f"<h5 class='text-lg font-semibold mt-4 mb-1'>Customization Approach</h5>")
        notes.append(f"<p class='mb-2'>Level: <span class='font-medium'>{level.capitalize()}</span>")
        if industry:
            notes.append(f" | Industry: <span class='font-medium'>{industry}</span>")
        notes.append("</p>")
        
        # Add keyword information
        if comparison_data and 'added_keywords' in comparison_data:
            added_keywords = comparison_data.get('added_keywords', [])
            if added_keywords:
                notes.append(f"<h5 class='text-lg font-semibold mt-4 mb-1'>Added Keywords</h5>")
                notes.append("<div class='flex flex-wrap gap-1 mb-3'>")
                for keyword in added_keywords:
                    notes.append(f"<span class='px-2 py-0.5 text-xs font-medium rounded-full bg-accent-light/80 text-white'>{keyword}</span>")
                notes.append("</div>")
        
        # Add simple explanation if detailed data not available
        if not (optimization_plan and comparison_data):
            notes.append("<p>Your resume was customized to better match the job requirements using a " + 
                        f"{level.lower()} approach. Keywords were adjusted and content was optimized " +
                        "to enhance your resume's compatibility with ATS systems.</p>")
        
        return "\n".join(notes)
    except Exception as e:
        logger.error(f"Error generating customization notes: {str(e)}")
        return "<p>Your resume was customized to better match the job requirements. Specific details cannot be displayed.</p>"

@resume_bp.route('/customize-resume', methods=['POST'])
@login_required
def customize_resume():
    """Handle customization of resume based on job description by directly redirecting to streaming view."""
    logger.debug("Handling customize-resume request")
    
    # Get form data
    resume_id = request.form.get('resume_id')
    job_id = request.form.get('job_id')
    customization_level = request.form.get('customization_level', 'balanced')
    industry = request.form.get('industry')
    
    logger.debug(f"Form data received: {request.form}")
    logger.debug(f"Raw values - resume_id: {resume_id}, job_id: {job_id}, level: {customization_level}, industry: {industry}")
    
    # Convert to integers
    try:
        resume_id = int(resume_id) if resume_id else None
        job_id = int(job_id) if job_id else None
    except ValueError:
        flash('Invalid resume or job ID', 'danger')
        return redirect(url_for('resume.analyze_resume'))
    
    # Handle missing values
    if not resume_id or not job_id:
        flash('Missing resume or job information.', 'danger')
        return redirect(url_for('resume.analyze_resume'))
    
    # Load original resume from database
    original_resume = CustomizedResume.query.get(resume_id)
    if not original_resume:
        flash('Resume not found.', 'danger')
        return redirect(url_for('resume.analyze_resume'))
    
    # Check if resume belongs to current user
    if original_resume.user_id != current_user.id and not current_user.is_admin:
        flash('You do not have permission to customize this resume.', 'danger')
        return redirect(url_for('resume.analyze_resume'))
    
    # Load job description from database
    job = JobDescription.query.get(job_id)
    if not job:
        flash('Job description not found.', 'danger')
        return redirect(url_for('resume.analyze_resume'))
    
    # Always redirect to the streaming view - we've removed the old basic view completely
    logger.info(f"Redirecting to streaming view - resume_id={resume_id}, job_id={job_id}")
    streaming_url = url_for('resume.customize_resume_view', 
                           resume_id=resume_id, 
                           job_id=job_id, 
                           customization_level=customization_level, 
                           industry=industry)
    logger.debug(f"Redirecting to streaming URL: {streaming_url}")
    return redirect(streaming_url)

@resume_bp.route('/api/process_resume', methods=['POST'])
@login_required
def process_resume():
    """Process a resume against a job description."""
    # Get resume and job from form
    resume_text = request.form.get('resume')
    job_id = request.form.get('job_id')
    
    # Return error if missing data
    if not resume_text or not job_id:
        return jsonify({'error': 'Missing resume text or job ID'}), 400
    
    # Load job description from database
    job = JobDescription.query.get(job_id)
    if not job:
        return jsonify({'error': 'Job description not found'}), 404
    
    job_description = job.content
    
    logger.debug(f"Processing resume, text length: {len(resume_text)}")
    logger.debug(f"Processing job description, text length: {len(job_description)}")
    
    # Analyze resume against job description
    ats_results = ats_analyzer.analyze(resume_text, job_description)
    
    # Generate AI suggestions for improvements
    suggestions = ai_suggestions.get_suggestions(
        resume_text, 
        job_description
    )
    
    logger.debug(f"Generated {len(suggestions)} AI suggestions")
    
    # Save original resume content to session
    session['original_resume_content'] = resume_text
    
    logger.debug(f"Rendering template with resume_id={None}, job_id={job.id}")
    
    # Return results
    return jsonify({
        'ats_score': ats_results,
        'suggestions': suggestions
    })

@resume_bp.route('/api/stream_suggestions', methods=['POST'])
@login_required
def stream_suggestions():
    """Stream AI suggestions for resume improvement"""
    # First, determine how the resume was provided (file or text)
    resume_text = None
    job_id = None
    job_description = None
    
    logger.debug(f"Form data received: {request.form}")
    logger.debug(f"Files received: {request.files}")
    
    # Check if resume is provided as file or text
    if 'resume_file' in request.files and request.files['resume_file'].filename:
        # Get resume file
        file = request.files['resume_file']
        logger.debug(f"Resume file received: {file.filename}")
        
        # Parse resume content from file
        try:
            resume_text = file_parser.parse_to_markdown(file)
            # Determine file format from filename
            file_format = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else 'txt'
            original_filename = file.filename
        except Exception as e:
            return jsonify({'error': f'Error parsing resume file: {str(e)}'}), 400
    else:
        # Get resume from form data
        resume_text = request.form.get('resume')
        
        if not resume_text:
            return jsonify({'error': 'No resume provided'}), 400
    
    # Get job description from form or URL
    job_id = request.form.get('job_id')
    
    if job_id:
        # Load job description from database
        job = JobDescription.query.get(job_id)
        if job:
            job_description = job.content
    else:
        # No job ID provided
        job_url = request.form.get('job_url')
        
        if job_url:
            # Process job URL
            # Create job record via jobs blueprint
            result = handle_job_url_submission(job_url, resume_text)
            
            if 'error' in result:
                return jsonify(result), 400
                
            job_id = result.get('job_id')
            job = JobDescription.query.get(job_id)
            job_description = job.content
            
            logger.debug(f"Job description extracted from URL. Length: {len(job_description or '')}")
        else:
            job_description = request.form.get('job_description')
            
            if not job_description:
                return jsonify({'error': 'No job description or URL provided'}), 400
                
            # Create job record
            job = JobDescription(
                title='Custom Job',
                content=job_description,
                user_id=current_user.id,
                created_at=datetime.utcnow()
            )
            db.session.add(job)
            db.session.commit()
            job_id = job.id
    
    # Save original resume to database
    resume_id = save_resume(resume_text, original_filename if 'original_filename' in locals() else 'resume.txt', 
                           file_format if 'file_format' in locals() else 'text', job_id)
    
    logger.debug(f"Streaming suggestions - Resume length: {len(resume_text)}, Job desc length: {len(job_description if job_description else '')}")
    
    # Create streaming response
    def generate():
        # First, analyze resume against job description
        ats_results = ats_analyzer.analyze(resume_text, job_description)
        
        # Ensure JSON can be serialized (convert objects to suitable format)
        serializable_results = {
            'score': round(ats_results.get('score', 0), 2),
            'confidence': ats_results.get('confidence', 'low'),
            'matching_keywords': ats_results.get('matching_keywords', []),
            'missing_keywords': ats_results.get('missing_keywords', []), 
            'section_scores': ats_results.get('section_scores', {}),
            'job_type': ats_results.get('job_type', 'unknown'),
            'resume_id': resume_id,
            'job_id': job_id
        }
        
        # If suggestions exist, add them to serializable results
        if 'suggestions' in ats_results:
            serializable_results['suggestions'] = ats_results['suggestions']
        
        # Send the ATS results as JSON first
        yield json.dumps({'type': 'ats_results', 'data': serializable_results}) + "\n"
        
        # Then stream the suggestions
        yield json.dumps({'type': 'stream_start'}) + "\n"
        
        # Stream suggestions
        for chunk in ai_suggestions.get_suggestions_stream(resume_text, job_description):
            yield json.dumps({'type': 'chunk', 'content': chunk}) + "\n"
            
        # Signal the end of streaming
        yield json.dumps({'type': 'stream_end'}) + "\n"
    
    # Save original resume content to session
    session['original_resume_content'] = resume_text
    
    return Response(stream_with_context(generate()), 
                    content_type='application/json; charset=utf-8')

@resume_bp.route('/api/customize_resume_streaming', methods=['POST'])
@resume_bp.route('/customize-resume/streaming', methods=['POST'])
@login_required
def customize_resume_streaming():
    """Streaming resume customization endpoint"""
    # Get form data
    resume_id = request.form.get('resume_id')
    job_id = request.form.get('job_id')
    customization_level = request.form.get('customization_level', 'balanced')
    industry = request.form.get('industry')
    selected_recommendations = request.form.getlist('selected_recommendations')
    
    # Validate inputs
    try:
        resume_id = int(resume_id) if resume_id else None
        job_id = int(job_id) if job_id else None
    except ValueError:
        return jsonify({'error': 'Invalid resume or job ID'}), 400
    
    if not resume_id or not job_id:
        return jsonify({'error': 'Missing resume or job information'}), 400
    
    # Load resume from database
    original_resume = CustomizedResume.query.get(resume_id)
    if not original_resume:
        return jsonify({'error': 'Resume not found'}), 404
    
    # Check permissions
    if original_resume.user_id != current_user.id and not current_user.is_admin:
        return jsonify({'error': 'You do not have permission to customize this resume'}), 403
    
    # Load job description
    job = JobDescription.query.get(job_id)
    if not job:
        return jsonify({'error': 'Job description not found'}), 404
    
    # Get original content
    resume_content = original_resume.original_content
    file_format = original_resume.file_format
    
    # Define the streaming generator function
    def generate():
        # First generate a unique ID for this customization session
        session_id = str(uuid.uuid4())
        yield json.dumps({
            'type': 'session_start',
            'session_id': session_id
        }) + "\n"
        
        # Stream the customization process
        try:
            for chunk in resume_customizer.customize_resume_streaming(
                resume_content,
                job.content,
                customization_level=customization_level,
                industry=industry,
                selected_recommendations=selected_recommendations
            ):
                yield chunk
                
            # When customization is complete, the final chunk will have been sent
            # Client-side will handle saving the customization
        except Exception as e:
            logger.error(f"Error in streaming customization: {str(e)}")
            yield json.dumps({
                'type': 'error',
                'message': f"Error customizing resume: {str(e)}"
            }) + "\n"
    
    # Return streaming response with JSON content type (not SSE)
    response = Response(stream_with_context(generate()),
                        content_type='application/json; charset=utf-8')
    
    # Minimal headers needed
    response.headers['Cache-Control'] = 'no-cache'
    response.headers['X-Accel-Buffering'] = 'no'  # Prevent proxy buffering
    
    logger.debug(f"Streaming resume customization response headers: {dict(response.headers)}")
    
    return response

@resume_bp.route('/save_customized_resume', methods=['POST'])
@login_required
def save_customized_resume():
    """Save a customized resume after streaming completion"""
    # Get data from form
    original_content = request.form.get('original_content')
    customized_content = request.form.get('customized_content')
    original_score = float(request.form.get('original_score', 0))
    new_score = float(request.form.get('new_score', 0))
    improvement = float(request.form.get('improvement', 0))
    resume_id = request.form.get('original_id')
    job_id = request.form.get('job_id')
    customization_level = request.form.get('customization_level', 'balanced')
    industry = request.form.get('industry')
    
    # Parse JSON data
    try:
        optimization_plan = json.loads(request.form.get('optimization_plan', '{}'))
        comparison_data = json.loads(request.form.get('comparison_data', '{}'))
    except json.JSONDecodeError:
        return jsonify({'error': 'Invalid JSON data'}), 400
    
    # Validate inputs
    try:
        resume_id = int(resume_id) if resume_id else None
        job_id = int(job_id) if job_id else None
    except ValueError:
        return jsonify({'error': 'Invalid resume or job ID'}), 400
    
    if not resume_id or not job_id:
        return jsonify({'error': 'Missing resume or job information'}), 400
    
    # Load original resume
    original_resume = CustomizedResume.query.get(resume_id)
    if not original_resume:
        return jsonify({'error': 'Original resume not found'}), 404
    
    # Check permissions
    if original_resume.user_id != current_user.id and not current_user.is_admin:
        return jsonify({'error': 'You do not have permission to save this resume'}), 403
    
    # Load job
    job = JobDescription.query.get(job_id)
    if not job:
        return jsonify({'error': 'Job description not found'}), 404
    
    # Create new customized resume
    new_customized_resume = CustomizedResume(
        original_id=resume_id,
        job_description_id=job_id,
        user_id=current_user.id,
        title=f"{original_resume.title} (Customized for {job.title})",
        original_content=original_content,
        customized_content=customized_content,
        file_format=original_resume.file_format,
        ats_score=new_score,
        original_ats_score=original_score,
        improvement=improvement,
        confidence=0.8,  # Default confidence value
        customization_level=customization_level,
        industry=industry,
        optimization_data=json.dumps(optimization_plan),
        comparison_data=json.dumps(comparison_data),
        customization_notes=generate_simple_customization_notes(optimization_plan, comparison_data, customization_level, industry)
    )
    
    # Save to database
    db.session.add(new_customized_resume)
    db.session.commit()
    
    # Redirect to comparison view
    return redirect(url_for('resume.compare_resume', resume_id=new_customized_resume.id))

@resume_bp.route('/api/analyze_resume', methods=['POST'])
@login_required
def analyze_resume():
    """Analyze a resume against a job description."""
    # Debug log the incoming form data
    logger.debug(f"Form data received: {request.form}")
    logger.debug(f"Files received: {request.files}")
    
    # Check if resume is provided as file or text
    if 'resume_file' in request.files and request.files['resume_file'].filename:
        # Get resume file
        file = request.files['resume_file']
        logger.debug(f"Resume file received: {file.filename}")
        
        # Parse resume content from file
        try:
            resume_content = file_parser.parse_to_markdown(file)
            # Determine file format from filename
            file_format = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else 'txt'
            original_filename = file.filename
        except Exception as e:
            return jsonify({'error': f'Error parsing resume file: {str(e)}'}), 400
    else:
        # Get resume from form data
        resume_content = request.form.get('resume')
        file_format = 'text'
        original_filename = 'resume.txt'
        
        if not resume_content:
            return jsonify({'error': 'No resume provided'}), 400
    
    # Get job description from form or URL
    job_id = request.form.get('job_id')
    job_description = None
    
    if job_id:
        # Load job description from database
        job = JobDescription.query.get(job_id)
        if job:
            job_description = job.content
    else:
        # No job ID provided
        job_url = request.form.get('job_url')
        
        if job_url:
            # Process job URL
            # Create job record via jobs blueprint
            result = handle_job_url_submission(job_url, resume_content)
            
            if 'error' in result:
                return jsonify(result), 400
                
            job_id = result.get('job_id')
            job = JobDescription.query.get(job_id)
            job_description = job.content
            
            logger.debug(f"Job description extracted from URL. Length: {len(job_description or '')}")
        else:
            job_description = request.form.get('job_description')
            
            if not job_description:
                return jsonify({'error': 'No job description or URL provided'}), 400
                
            # Create job record
            job = JobDescription(
                title='Custom Job',
                content=job_description,
                user_id=current_user.id,
                created_at=datetime.utcnow()
            )
            db.session.add(job)
            db.session.commit()
            job_id = job.id
    
    # Save original resume to database
    resume_id = save_resume(resume_content, original_filename, file_format, job_id)
    
    # Analyze resume against job description
    ats_results = ats_analyzer.analyze(resume_content, job_description)
    
    # Generate AI suggestions for improvements
    suggestions = ai_suggestions.get_suggestions(
        resume_content, 
        job_description
    )
    
    logger.debug(f"Generated {len(suggestions)} AI suggestions")
    
    logger.debug(f"Rendering template with resume_id={resume_id}, job_id={job.id}")
    
    # Render the analysis results template
    return render_template('partials/analysis_results.html', 
        resume_id=resume_id,
        job_id=job.id,
        ats_score=ats_results,
        suggestions=suggestions
    )

@resume_bp.route('/customized-resume/<int:resume_id>')
@login_required
def view_customized_resume(resume_id):
    """Redirect to the comparison view for a more detailed experience."""
    # Create a response that redirects to the comparison view
    response = redirect(url_for('resume.compare_resume', resume_id=resume_id))
    
    # Add cache-busting headers to ensure browsers don't use cached versions
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    
    return response

def resume_to_dict(resume):
    """Convert a CustomizedResume object to a serializable dictionary"""
    if not resume:
        return None
        
    result = {
        'id': resume.id,
        'user_id': resume.user_id,
        'job_description_id': resume.job_description_id,
        'title': resume.title,
        'original_content': resume.original_content,
        'customized_content': resume.customized_content,
        'file_format': resume.file_format,
        'ats_score': resume.ats_score,
        'original_ats_score': resume.original_ats_score,
        'improvement': resume.improvement,
        'confidence': resume.confidence,
        'customization_level': resume.customization_level,
        'industry': resume.industry,
        'created_at': resume.created_at.isoformat() if resume.created_at else None,
        'user_rating': resume.user_rating,
        'user_feedback': resume.user_feedback,
        'original_id': resume.original_id,
        'interview_secured': resume.interview_secured,
        'job_secured': resume.job_secured,
        'was_effective': resume.was_effective
    }
    
    # Handle JSON fields
    if resume.comparison_data:
        if isinstance(resume.comparison_data, str):
            try:
                result['comparison_data'] = json.loads(resume.comparison_data)
            except json.JSONDecodeError:
                result['comparison_data'] = {}
        else:
            result['comparison_data'] = resume.comparison_data
            
    if resume.optimization_data:
        if isinstance(resume.optimization_data, str):
            try:
                result['optimization_data'] = json.loads(resume.optimization_data)
            except json.JSONDecodeError:
                result['optimization_data'] = {}
        else:
            result['optimization_data'] = resume.optimization_data
            
    if resume.selected_recommendations:
        if isinstance(resume.selected_recommendations, str):
            try:
                result['selected_recommendations'] = json.loads(resume.selected_recommendations)
            except json.JSONDecodeError:
                result['selected_recommendations'] = []
        else:
            result['selected_recommendations'] = resume.selected_recommendations
            
    if resume.recommendation_feedback:
        if isinstance(resume.recommendation_feedback, str):
            try:
                result['recommendation_feedback'] = json.loads(resume.recommendation_feedback)
            except json.JSONDecodeError:
                result['recommendation_feedback'] = {}
        else:
            result['recommendation_feedback'] = resume.recommendation_feedback
    
    return result

@resume_bp.route('/compare/<int:resume_id>')
@login_required
def compare_resume(resume_id):
    """Compare original and customized resume."""
    # Load customized resume from database
    resume = CustomizedResume.query.get_or_404(resume_id)
    
    # Check if resume belongs to current user
    if resume.user_id != current_user.id and not current_user.is_admin:
        flash('You do not have permission to view this resume.', 'danger')
        return redirect(url_for('dashboard.user_dashboard'))
    
    # Get original resume if available
    original = None
    if resume.original_id:
        original = CustomizedResume.query.get(resume.original_id)
    
    # Get job description
    job = JobDescription.query.get(resume.job_description_id)
    
    # Parse JSON fields if they are strings
    if resume.comparison_data and isinstance(resume.comparison_data, str):
        try:
            resume.comparison_data = json.loads(resume.comparison_data)
        except json.JSONDecodeError:
            logger.error(f"Error parsing comparison_data JSON for resume ID {resume_id}")
            resume.comparison_data = {}
    
    if resume.optimization_data and isinstance(resume.optimization_data, str):
        try:
            resume.optimization_data = json.loads(resume.optimization_data)
        except json.JSONDecodeError:
            logger.error(f"Error parsing optimization_data JSON for resume ID {resume_id}")
            resume.optimization_data = {}
    
    if resume.selected_recommendations and isinstance(resume.selected_recommendations, str):
        try:
            resume.selected_recommendations = json.loads(resume.selected_recommendations)
        except json.JSONDecodeError:
            logger.error(f"Error parsing selected_recommendations JSON for resume ID {resume_id}")
            resume.selected_recommendations = []
    
    if resume.recommendation_feedback and isinstance(resume.recommendation_feedback, str):
        try:
            resume.recommendation_feedback = json.loads(resume.recommendation_feedback)
        except json.JSONDecodeError:
            logger.error(f"Error parsing recommendation_feedback JSON for resume ID {resume_id}")
            resume.recommendation_feedback = {}
    
    # Enhanced server-side content preparation
    # Ensure the content is proper HTML and won't require client-side processing
    if resume.customized_content:
        # Simple markdown processing if needed
        resume.customized_content = resume.customized_content.replace('\n', '<br>')
    
    if original and original.original_content:
        original.original_content = original.original_content.replace('\n', '<br>')
    
    # Convert resume and original to dictionaries for JSON serialization
    resume_dict = resume_to_dict(resume)
    original_dict = resume_to_dict(original)
    
    # Also prepare job as a dictionary if needed
    job_dict = {
        'id': job.id,
        'title': job.title,
        'content': job.content
    } if job else None
    
    # Log detailed information for debugging
    logger.info(f"Rendering comparison view for resume ID {resume_id}")
    logger.debug(f"Resume content length: {len(resume.customized_content or '')}")
    logger.debug(f"Original content length: {len(original.original_content or '') if original else 0}")
    
    # Add cache-busting headers to the response
    response = make_response(render_template(
        'customized_resume_comparison.html',
        resume=resume,
        resume_json=resume_dict,
        original=original,
        original_json=original_dict,
        job=job,
        job_json=job_dict,
        enumerate=enumerate
    ))
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    
    return response

@resume_bp.route('/download/<int:resume_id>/<format>')
@login_required
def download_resume(resume_id, format):
    """Download a resume in specified format."""
    # Load resume from database
    resume = CustomizedResume.query.get_or_404(resume_id)
    
    # Check if resume belongs to current user
    if resume.user_id != current_user.id and not current_user.is_admin:
        flash('You do not have permission to download this resume.', 'danger')
        return redirect(url_for('dashboard.user_dashboard'))
    
    # Generate PDF or appropriate format
    if format == 'pdf':
        # Convert to PDF
        from services.pdf_extractor import generate_pdf
        pdf_bytes = generate_pdf(resume.customized_content, resume.file_format)
        
        # Create file-like object
        file_obj = BytesIO(pdf_bytes)
        
        # Generate filename
        filename = f"resume_{resume_id}.pdf"
        
        # Send file
        return send_file(
            file_obj,
            as_attachment=True,
            download_name=filename,
            mimetype='application/pdf'
        )
    else:
        # Handle other formats
        flash('Format not supported yet.', 'warning')
        return redirect(url_for('resume.view_customized_resume', resume_id=resume_id))

@resume_bp.route('/export/<int:resume_id>')
@resume_bp.route('/export/<int:resume_id>/<version>')
@login_required
def export_resume(resume_id, version=None):
    """Export a resume to various formats."""
    # Load resume from database
    resume = CustomizedResume.query.get_or_404(resume_id)
    
    # Check if resume belongs to current user
    if resume.user_id != current_user.id and not current_user.is_admin:
        flash('You do not have permission to export this resume.', 'danger')
        return redirect(url_for('dashboard.user_dashboard'))
    
    # Get export format
    format_type = request.args.get('format', 'pdf')
    
    # Generate appropriate format
    if format_type == 'pdf':
        # Generate PDF
        return redirect(url_for('resume.download_resume', resume_id=resume_id, format='pdf'))
    elif format_type == 'docx':
        # Generate DOCX
        flash('DOCX export not implemented yet.', 'warning')
        return redirect(url_for('resume.view_customized_resume', resume_id=resume_id))
    else:
        # Handle unsupported format
        flash(f'Unsupported format: {format_type}', 'danger')
        return redirect(url_for('resume.view_customized_resume', resume_id=resume_id))

@resume_bp.route('/api/feedback/<int:resume_id>', methods=['POST'])
@login_required
def submit_feedback(resume_id):
    """Submit feedback for a customized resume."""
    # Load resume from database
    resume = CustomizedResume.query.get_or_404(resume_id)
    
    # Check if resume belongs to current user
    if resume.user_id != current_user.id and not current_user.is_admin:
        return jsonify({'error': 'You do not have permission to submit feedback for this resume.'}), 403
    
    # Get feedback data from JSON payload
    data = request.json
    if not data:
        # Fallback to form data if JSON not provided
        data = request.form
    
    rating = data.get('rating')
    if rating is not None:
        try:
            rating = int(rating)
        except (ValueError, TypeError):
            return jsonify({'error': 'Invalid rating format. Must be a number.'}), 400
    
    feedback = data.get('feedback')
    was_effective = data.get('was_effective', False)
    interview_secured = data.get('interview_secured', False)
    job_secured = data.get('job_secured', False)
    
    # Validate data
    if rating is None or rating < 1 or rating > 5:
        return jsonify({'error': 'Invalid rating. Must be between 1 and 5.'}), 400
        
    # Update resume with feedback
    resume.user_rating = rating
    resume.user_feedback = feedback
    resume.was_effective = was_effective
    resume.interview_secured = interview_secured
    resume.job_secured = job_secured
    
    # Save changes
    db.session.commit()
    
    # Return success
    return jsonify({'success': True})

@resume_bp.route('/review-recommendations/<int:resume_id>/<int:job_id>', methods=['GET', 'POST'])
@login_required
def review_recommendations(resume_id, job_id):
    """
    Display optimization recommendations and allow user to select which ones to implement
    """
    # Load original resume from database
    original_resume = CustomizedResume.query.get_or_404(resume_id)
    
    # Check if resume belongs to current user
    if original_resume.user_id != current_user.id and not current_user.is_admin:
        flash('You do not have permission to customize this resume.', 'danger')
        return redirect(url_for('dashboard.user_dashboard'))
    
    # Load job description from database
    job = JobDescription.query.get_or_404(job_id)
    
    # Check if the form was submitted
    if request.method == 'POST':
        # Get the selected recommendations
        selected_recommendations = request.form.getlist('recommendation')
        customization_level = request.form.get('customization_level', 'balanced')
        industry = request.form.get('industry')
        
        # Get original resume content
        original_content = original_resume.original_content
        file_format = original_resume.file_format
        
        try:
            # Process resume customization with selected recommendations
            logger.info(f"Starting selective resume customization with {len(selected_recommendations)} recommendations")
            
            customization_result = resume_customizer.customize_resume(
                original_content, 
                job.content,
                customization_level=customization_level,
                industry=industry,
                selected_recommendations=selected_recommendations
            )
            
            # Ensure numeric values are properly handled
            improvement = customization_result.get('improvement')
            if not isinstance(improvement, (int, float)):
                if isinstance(improvement, str):
                    if improvement.lower() in ['low', 'medium', 'high']:
                        # Convert text confidence to numeric values
                        improvement_map = {'low': 1.0, 'medium': 5.0, 'high': 10.0}
                        improvement = improvement_map.get(improvement.lower(), 0.0)
                    else:
                        try:
                            improvement = float(improvement)
                        except (ValueError, TypeError):
                            improvement = 0.0
                else:
                    improvement = 0.0
            
            confidence = customization_result.get('confidence')
            if not isinstance(confidence, (int, float)):
                if isinstance(confidence, str):
                    if confidence.lower() in ['low', 'medium', 'high']:
                        # Convert text confidence to numeric values
                        confidence_map = {'low': 0.3, 'medium': 0.6, 'high': 0.9}
                        confidence = confidence_map.get(confidence.lower(), 0.5)
                    else:
                        try:
                            confidence = float(confidence)
                        except (ValueError, TypeError):
                            confidence = 0.5
                else:
                    confidence = 0.5
            
            # Create a new customized resume entry
            new_customized_resume = CustomizedResume(
                original_id=resume_id,
                job_description_id=job_id,
                user_id=current_user.id,
                title=f"{original_resume.title} (Custom Select for {job.title})",
                original_content=original_content,
                customized_content=customization_result['customized_content'],
                file_format=file_format,
                ats_score=float(customization_result['new_score']),
                original_ats_score=float(customization_result['original_score']),
                improvement=improvement,
                confidence=confidence,
                customization_level=customization_level,
                industry=industry,
                optimization_data=json.dumps(customization_result['optimization_plan']),
                comparison_data=json.dumps(customization_result['comparison_data']),
                selected_recommendations=json.dumps(selected_recommendations),
                customization_notes=customization_result.get('customization_notes')
            )
            
            db.session.add(new_customized_resume)
            db.session.commit()
            
            logger.info(f"Selective resume customization successful: new_id={new_customized_resume.id}")
            
            # Redirect to the comparison view
            return redirect(url_for('resume.compare_resume', resume_id=new_customized_resume.id))
            
        except Exception as e:
            logger.error(f"Error in selective resume customization: {str(e)}")
            flash(f"Error customizing resume: {str(e)}", 'danger')
            return redirect(url_for('dashboard.user_dashboard'))
    
    # For GET request, generate recommendations first to show user
    try:
        # Get customization options for form
        customization_levels = [
            ('conservative', 'Conservative - Minimal changes, focus on essential alignment'),
            ('balanced', 'Balanced - Default level with reasonable optimization'),
            ('extensive', 'Extensive - More aggressive optimization')
        ]
        
        industries = [
            ('technology', 'Technology'),
            ('healthcare', 'Healthcare'),
            ('finance', 'Finance'),
            ('marketing', 'Marketing'),
            ('education', 'Education'),
            ('manufacturing', 'Manufacturing'),
            ('retail', 'Retail')
        ]
        
        # Get current customization stage (analysis only)
        original_content = original_resume.original_content
        
        # Generate optimization plan only (stage 1 of customization)
        analysis_result = resume_customizer._analyze_and_plan(
            original_content, 
            job.content,
            resume_customizer.ats_analyzer.analyze(original_content, job.content),
            'balanced'
        )
        
        # Extract recommendations from the optimization plan
        recommendations = analysis_result.get('recommendations', [])
        
        # Render the recommendations review template
        return render_template(
            'review_recommendations.html',
            resume=original_resume,
            job=job,
            recommendations=recommendations,
            customization_levels=customization_levels,
            industries=industries,
            analysis_summary=analysis_result.get('summary', ''),
            job_analysis=analysis_result.get('job_analysis', ''),
            enumerate=enumerate
        )
        
    except Exception as e:
        logger.error(f"Error generating recommendations: {str(e)}")
        flash(f"Error generating recommendations: {str(e)}", 'danger')
        return redirect(url_for('dashboard.user_dashboard'))

@resume_bp.route('/customize-resume-view')
@login_required
def customize_resume_view():
    """
    Show the resume customization view with streaming updates.
    This is step 1 - display the page that will show streaming updates.
    """
    # Get query parameters
    resume_id = request.args.get('resume_id')
    job_id = request.args.get('job_id')
    customization_level = request.args.get('customization_level', 'balanced')
    industry = request.args.get('industry', '')
    
    # Debug log query parameters
    logger.debug(f"customize_resume_view parameters: resume_id={resume_id}, job_id={job_id}")
    logger.debug(f"customize_resume_view options: level={customization_level}, industry={industry}")
    logger.debug(f"All request args: {request.args}")
    
    # Convert to integers
    try:
        resume_id = int(resume_id) if resume_id else None
        job_id = int(job_id) if job_id else None
    except ValueError:
        flash('Invalid resume or job ID', 'danger')
        return redirect(url_for('dashboard.user_dashboard'))
    
    # Load resume and job
    resume = CustomizedResume.query.get_or_404(resume_id)
    job = JobDescription.query.get_or_404(job_id)
    
    # Check permissions
    if resume.user_id != current_user.id and not current_user.is_admin:
        flash('You do not have permission to customize this resume.', 'danger')
        return redirect(url_for('dashboard.user_dashboard'))
    
    # Create a placeholder entry for the customized resume
    placeholder = CustomizedResume(
        original_id=resume_id,
        job_description_id=job_id,
        user_id=current_user.id,
        title=f"{resume.title} (Customizing for {job.title}...)",
        original_content=resume.original_content,
        customized_content="Customizing your resume... Please wait...",
        file_format=resume.file_format,
        ats_score=0.0,
        original_ats_score=resume.ats_score or 0.0,
        improvement=0.0,
        confidence=0.0,
        customization_level=customization_level,
        industry=industry,
        is_placeholder=True,  # This is a placeholder flag for tracking
        streaming_progress=0,
        streaming_status="Initializing customization process..."
    )
    
    db.session.add(placeholder)
    db.session.commit()
    
    logger.info(f"Created placeholder for streaming customization: id={placeholder.id}")
    
    # Render the streaming customization page - we let the frontend handle the streaming now
    return render_template(
        'customized_resume_streaming.html',
        resume=placeholder,
        original=resume,
        job=job,
        customization_level=customization_level,
        industry=industry
    )
    
@resume_bp.route('/api/resume-updates/<int:resume_id>')
@login_required
def resume_updates(resume_id):
    """
    Stream updates for a resume being customized.
    Uses server-sent events to push updates to the client.
    """
    logger.info(f"Server-Sent Events stream requested for resume ID {resume_id}")
    resume = CustomizedResume.query.get_or_404(resume_id)
    
    # Check permissions
    if resume.user_id != current_user.id and not current_user.is_admin:
        logger.warning(f"Permission denied for resume updates: User {current_user.id} attempted to access resume {resume_id} belonging to user {resume.user_id}")
        return jsonify({'error': 'Permission denied'}), 403
    
    logger.debug(f"Streaming updates for resume {resume_id}. Current status: '{resume.streaming_status}', progress: {resume.streaming_progress}")
    
    def generate():
        """
        Generator function for SSE - yields events with explicit flush directives
        """
        # Always start with a heartbeat to confirm connection
        logger.debug(f"Starting SSE stream for resume {resume_id}, sending heartbeat")
        data = f": heartbeat\n\n"
        yield data
        
        # Send initial status - make sure it has proper formatting for SSE
        initial_status = {'message': resume.streaming_status or 'Starting...', 'progress': resume.streaming_progress or 0}
        logger.debug(f"Sending initial status: {initial_status}")
        data = f"event: status\ndata: {json.dumps(initial_status)}\n\n"
        yield data
        
        # Check for updates until process is complete
        placeholder_id = resume.id
        last_progress = resume.streaming_progress or 0
        last_status = resume.streaming_status or 'Starting...'
        last_content = resume.customized_content
        
        # Debug counter
        iterations = 0
        
        while True:
            iterations += 1
            if iterations % 5 == 0:
                logger.debug(f"SSE stream polling iteration {iterations} for resume {placeholder_id}")
            
            # Refresh the resume from the database
            db.session.rollback()  # Release any existing transaction
            try:
                current_resume = CustomizedResume.query.get(placeholder_id)
                
                if not current_resume:
                    # Resume was deleted
                    logger.warning(f"Resume {placeholder_id} not found during streaming")
                    data = f"event: error\ndata: {json.dumps({'message': 'Resume not found'})}\n\n"
                    yield data
                    break
                    
                # Send a periodic heartbeat to keep the connection alive
                if iterations % 10 == 0:
                    logger.debug(f"Sending heartbeat for resume {placeholder_id}")
                    data = f": heartbeat {iterations}\n\n"
                    yield data
                    
            except Exception as e:
                logger.error(f"Error querying resume during streaming: {str(e)}")
                data = f"event: error\ndata: {json.dumps({'message': f'Error: {str(e)}'})}\n\n"
                yield data
                break
                
            # Check if status has changed
            if current_resume.streaming_status != last_status or current_resume.streaming_progress != last_progress:
                logger.debug(f"Status changed for resume {placeholder_id}: '{current_resume.streaming_status}', progress: {current_resume.streaming_progress}")
                data = f"event: status\ndata: {json.dumps({'message': current_resume.streaming_status or '', 'progress': current_resume.streaming_progress or 0})}\n\n"
                yield data
                last_status = current_resume.streaming_status
                last_progress = current_resume.streaming_progress
            
            # Check if content has changed
            if current_resume.customized_content != last_content:
                logger.debug(f"Content changed for resume {placeholder_id}, length: {len(current_resume.customized_content or '')}")
                data = f"event: content\ndata: {json.dumps({'content': current_resume.customized_content})}\n\n"
                yield data
                last_content = current_resume.customized_content
            
            # Check if process is complete (no longer a placeholder)
            if not current_resume.is_placeholder:
                logger.info(f"Resume {placeholder_id} is no longer a placeholder, streaming complete")
                
                # Send final data
                try:
                    optimization_data = {}
                    if current_resume.optimization_data:
                        if isinstance(current_resume.optimization_data, str):
                            optimization_data = json.loads(current_resume.optimization_data)
                        else:
                            optimization_data = current_resume.optimization_data
                    
                    complete_data = {
                        'optimization_data': optimization_data,
                        'scores': {
                            'original_score': current_resume.original_ats_score,
                            'new_score': current_resume.ats_score,
                            'improvement': current_resume.improvement
                        }
                    }
                    logger.debug(f"Sending completion event for resume {placeholder_id}")
                    data = f"event: complete\ndata: {json.dumps(complete_data)}\n\n"
                    yield data
                except Exception as e:
                    logger.error(f"Error sending completion event: {str(e)}")
                    data = f"event: error\ndata: {json.dumps({'message': f'Error during completion: {str(e)}'})}\n\n"
                    yield data
                
                break
            
            # Wait before checking again
            from time import sleep
            sleep(0.5)  # Poll every 500ms
    
    # Create a response with appropriate headers for SSE
    response = Response(stream_with_context(generate()),
                        content_type='text/event-stream')
    
    # Set required headers for SSE
    response.headers['Cache-Control'] = 'no-cache'
    response.headers['Connection'] = 'keep-alive'
    response.headers['X-Accel-Buffering'] = 'no'  # Prevent proxy buffering
    
    # Set CORS headers to ensure SSE works across different origins
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
    response.headers['Access-Control-Allow-Credentials'] = 'true'
    
    # Set chunked encoding explicitly
    response.headers['Transfer-Encoding'] = 'chunked'
    
    logger.debug(f"Response headers for SSE stream: {dict(response.headers)}")
    
    return response

def process_resume_streaming(placeholder_id, original_content, job_content, customization_level, industry):
    """Background function to process resume customization with streaming updates"""
    try:
        logger.info(f"Starting streaming customization process for resume ID {placeholder_id}")
        logger.debug(f"Customization level: {customization_level}, Industry: {industry}")
        logger.debug(f"Original content length: {len(original_content)}, Job content length: {len(job_content)}")
        
        # Make sure we have an application context
        if not current_app:
            logger.error("No application context found. This is a critical error.")
            return
            
        # Get the placeholder resume
        resume = CustomizedResume.query.get(placeholder_id)
        if not resume:
            logger.error(f"Placeholder resume {placeholder_id} not found")
            return
            
        # Update status to analyzing
        logger.debug(f"Updating placeholder {placeholder_id} status to 'Analyzing'")
        resume.streaming_status = "Analyzing resume and job requirements..."
        resume.streaming_progress = 10
        db.session.commit()
        
        # Update status - starting customization
        resume.streaming_status = "Analyzing resume and job description..."
        resume.streaming_progress = 20
        db.session.commit()
        logger.debug(f"Updated placeholder {placeholder_id} status to 'Analyzing', progress: 20%")
        
        # Short delay to ensure UI can see this status
        from time import sleep
        sleep(1)
        
        # Update status - planning optimization
        resume.streaming_status = "Planning resume optimization..."
        resume.streaming_progress = 30
        db.session.commit()
        logger.debug(f"Updated placeholder {placeholder_id} status to 'Planning', progress: 30%")
        sleep(1)
        
        # Start the customization
        logger.debug(f"Starting actual customization for resume {placeholder_id}")
        customization_result = resume_customizer.customize_resume(
            original_content, 
            job_content,
            customization_level=customization_level,
            industry=industry
        )
        
        # Update with intermediate results
        resume.streaming_status = "Applying optimization plan..."
        resume.streaming_progress = 50
        resume.customized_content = customization_result['customized_content']
        db.session.commit()
        logger.debug(f"Updated placeholder {placeholder_id} with optimization plan, progress: 50%")
        
        # Short delay to ensure UI can see the intermediate state
        sleep(1)
        
        # Update with more progress
        resume.streaming_status = "Refining customized content..."
        resume.streaming_progress = 75
        db.session.commit()
        logger.debug(f"Updated placeholder {placeholder_id} status to 'Refining', progress: 75%")
        sleep(1)
        
        # Update status to finalizing
        resume.streaming_status = "Finalizing customization..."
        resume.streaming_progress = 75
        db.session.commit()
        
        # Ensure numeric values are properly handled
        improvement = customization_result.get('improvement')
        if not isinstance(improvement, (int, float)):
            if isinstance(improvement, str):
                if improvement.lower() in ['low', 'medium', 'high']:
                    # Convert text confidence to numeric values
                    improvement_map = {'low': 1.0, 'medium': 5.0, 'high': 10.0}
                    improvement = improvement_map.get(improvement.lower(), 0.0)
                else:
                    try:
                        improvement = float(improvement)
                    except (ValueError, TypeError):
                        improvement = 0.0
            else:
                improvement = 0.0
        
        confidence = customization_result.get('confidence')
        if not isinstance(confidence, (int, float)):
            if isinstance(confidence, str):
                if confidence.lower() in ['low', 'medium', 'high']:
                    # Convert text confidence to numeric values
                    confidence_map = {'low': 0.3, 'medium': 0.6, 'high': 0.9}
                    confidence = confidence_map.get(confidence.lower(), 0.5)
                else:
                    try:
                        confidence = float(confidence)
                    except (ValueError, TypeError):
                        confidence = 0.5
            else:
                confidence = 0.5
                
        # Update with final results
        resume.streaming_status = "Customization complete"
        resume.streaming_progress = 100
        resume.title = f"Resume Customized for {JobDescription.query.get(resume.job_description_id).title}"
        resume.customized_content = customization_result['customized_content']
        resume.ats_score = float(customization_result['new_score'])
        resume.original_ats_score = float(customization_result['original_score'])
        resume.improvement = improvement
        resume.confidence = confidence
        resume.optimization_data = json.dumps(customization_result['optimization_plan'])
        resume.comparison_data = json.dumps(customization_result['comparison_data'])
        resume.is_placeholder = False  # Mark as no longer a placeholder
        
        # Save the final results
        db.session.commit()
        
        logger.info(f"Completed streaming customization for resume {placeholder_id}")
        
    except Exception as e:
        logger.error(f"Error in streaming customization: {str(e)}", exc_info=True)
        # Update the placeholder with error status
        try:
            # Make sure we're in an application context
            if not current_app:
                logger.error("No application context in exception handler")
                return
            
            # Refresh the db session to avoid stale data issues
            db.session.rollback()
            
            # Get the resume and update its status
            resume = CustomizedResume.query.get(placeholder_id)
            if resume:
                logger.debug(f"Updating placeholder {placeholder_id} with error status")
                resume.streaming_status = f"Error: {str(e)}"
                resume.streaming_progress = 0
                # Explicitly mark as not a placeholder to trigger completion
                resume.is_placeholder = False
                db.session.commit()
                logger.debug(f"Successfully updated placeholder with error status")
            else:
                logger.error(f"Cannot find placeholder {placeholder_id} to update with error status")
        except Exception as inner_e:
            logger.error(f"Error updating placeholder status: {str(inner_e)}", exc_info=True)
        return

@resume_bp.route('/api/test-sse')
def test_sse():
    """Test route for server-sent events"""
    def generate():
        # Send 5 test events
        for i in range(5):
            logger.debug(f"Sending test SSE event {i+1}/5")
            
            # Heartbeat
            data = f": heartbeat\n\n"
            yield data
            
            # Test event
            data = f"event: test\ndata: {json.dumps({'message': f'Test event {i+1}/5', 'timestamp': datetime.utcnow().isoformat()})}\n\n"
            yield data
            
            # Sleep to simulate delays
            from time import sleep
            sleep(1)
            
        # Final event
        data = f"event: complete\ndata: {json.dumps({'message': 'Test complete'})}\n\n"
        yield data
    
    # Create response with appropriate headers
    response = Response(stream_with_context(generate()), content_type='text/event-stream')
    response.headers['Cache-Control'] = 'no-cache'
    response.headers['Connection'] = 'keep-alive'
    response.headers['X-Accel-Buffering'] = 'no'
    response.headers['Access-Control-Allow-Origin'] = '*'
    
    return response

@resume_bp.route('/test-sse-page')
def test_sse_page():
    """Test page for SSE functionality"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>SSE Test</title>
        <style>
            body { font-family: sans-serif; margin: 20px; }
            #events { border: 1px solid #ccc; padding: 10px; min-height: 200px; }
        </style>
    </head>
    <body>
        <h1>Server-Sent Events Test</h1>
        <div id="connection-status">Connecting...</div>
        <div id="events"></div>
        
        <script>
            document.addEventListener('DOMContentLoaded', function() {
                const eventsDiv = document.getElementById('events');
                const statusDiv = document.getElementById('connection-status');
                
                // Create EventSource connection
                const eventSource = new EventSource('/api/test-sse');
                
                // Connection opened
                eventSource.addEventListener('open', function(e) {
                    console.log('EventSource connection opened');
                    statusDiv.innerHTML = '<span style="color: green;">Connected</span>';
                    eventsDiv.innerHTML += '<p>Connection established</p>';
                });
                
                // Handle generic messages
                eventSource.onmessage = function(e) {
                    console.log('Generic message:', e.data);
                    eventsDiv.innerHTML += `<p>Generic message: ${e.data}</p>`;
                };
                
                // Handle test events
                eventSource.addEventListener('test', function(e) {
                    console.log('Test event:', e.data);
                    const data = JSON.parse(e.data);
                    eventsDiv.innerHTML += `<p>Test event: ${data.message} (${data.timestamp})</p>`;
                });
                
                // Handle completion
                eventSource.addEventListener('complete', function(e) {
                    console.log('Test complete:', e.data);
                    const data = JSON.parse(e.data);
                    eventsDiv.innerHTML += `<p>Complete: ${data.message}</p>`;
                    eventSource.close();
                    statusDiv.innerHTML = '<span style="color: blue;">Test complete</span>';
                });
                
                // Handle errors
                eventSource.addEventListener('error', function(e) {
                    console.error('SSE error:', e);
                    statusDiv.innerHTML = '<span style="color: red;">Connection error</span>';
                    eventsDiv.innerHTML += '<p>Error: Connection failed</p>';
                    eventSource.close();
                });
            });
        </script>
    </body>
    </html>
    """

@resume_bp.route('/api/recommendation_feedback', methods=['POST'])
@login_required
def recommendation_feedback():
    """
    Endpoint to record user feedback on which recommendations were most valuable
    """
    try:
        resume_id = request.json.get('resume_id')
        recommendation_id = request.json.get('recommendation_id')
        feedback_type = request.json.get('feedback_type')  # 'helpful' or 'not_helpful'
        
        # Validate input
        if not resume_id or not recommendation_id or not feedback_type:
            return jsonify({'success': False, 'error': 'Missing required parameters'}), 400
            
        # Get the resume
        resume = CustomizedResume.query.get_or_404(resume_id)
        
        # Check permissions
        if resume.user_id != current_user.id and not current_user.is_admin:
            return jsonify({'success': False, 'error': 'Permission denied'}), 403
            
        # Store the feedback
        # First, get existing feedback if any
        feedback_data = json.loads(resume.recommendation_feedback or '{}')
        
        # Update the feedback for this recommendation
        feedback_data[recommendation_id] = feedback_type
        
        # Save back to the database
        resume.recommendation_feedback = json.dumps(feedback_data)
        db.session.commit()
        
        return jsonify({'success': True})
        
    except Exception as e:
        logger.error(f"Error saving recommendation feedback: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@resume_bp.route('/api/save_customized_resume', methods=['POST'])
@login_required
def api_save_customized_resume():
    """API endpoint to save a customized resume after streaming completion"""
    try:
        # Get data from form
        original_content = request.form.get('original_content')
        customized_content = request.form.get('customized_content')
        original_score = float(request.form.get('original_score', 0))
        new_score = float(request.form.get('new_score', 0))
        improvement = float(request.form.get('improvement', 0))
        resume_id = request.form.get('original_id')
        job_id = request.form.get('job_id')
        customization_level = request.form.get('customization_level', 'balanced')
        industry = request.form.get('industry')
        placeholder_id = request.form.get('placeholder_id')
        
        # Parse JSON data
        try:
            optimization_plan = json.loads(request.form.get('optimization_plan', '{}'))
            comparison_data = json.loads(request.form.get('comparison_data', '{}'))
        except json.JSONDecodeError:
            return jsonify({'error': 'Invalid JSON data'}), 400
        
        # Validate inputs
        try:
            resume_id = int(resume_id) if resume_id else None
            job_id = int(job_id) if job_id else None
            placeholder_id = int(placeholder_id) if placeholder_id else None
        except ValueError:
            return jsonify({'error': 'Invalid resume or job ID'}), 400
        
        if not resume_id or not job_id:
            return jsonify({'error': 'Missing resume or job information'}), 400
        
        # Load original resume
        original_resume = CustomizedResume.query.get(resume_id)
        if not original_resume:
            return jsonify({'error': 'Original resume not found'}), 404
        
        # Check permissions
        if original_resume.user_id != current_user.id and not current_user.is_admin:
            return jsonify({'error': 'You do not have permission to save this resume'}), 403
        
        # Load job
        job = JobDescription.query.get(job_id)
        if not job:
            return jsonify({'error': 'Job description not found'}), 404
        
        # Create new customized resume
        new_customized_resume = CustomizedResume(
            original_id=resume_id,
            job_description_id=job_id,
            user_id=current_user.id,
            title=f"{original_resume.title} (Customized for {job.title})",
            original_content=original_content,
            customized_content=customized_content,
            file_format=original_resume.file_format,
            ats_score=new_score,
            original_ats_score=original_score,
            improvement=improvement,
            confidence=0.8,  # Default confidence value
            customization_level=customization_level,
            industry=industry,
            optimization_data=optimization_plan if isinstance(optimization_plan, dict) else json.dumps(optimization_plan),
            comparison_data=comparison_data if isinstance(comparison_data, dict) else json.dumps(comparison_data),
            is_placeholder=False,
            streaming_progress=100,
            streaming_status="Completed",
            customization_notes=generate_simple_customization_notes(optimization_plan, comparison_data, customization_level, industry)
        )
        
        # Save to database
        db.session.add(new_customized_resume)
        
        # If a placeholder ID was provided, delete the placeholder
        if placeholder_id:
            placeholder = CustomizedResume.query.get(placeholder_id)
            if placeholder and placeholder.is_placeholder and (placeholder.user_id == current_user.id or current_user.is_admin):
                db.session.delete(placeholder)
                logger.info(f"Deleted placeholder resume with ID {placeholder_id}")
        
        db.session.commit()
        
        logger.info(f"Saved customized resume with ID {new_customized_resume.id}")
        
        # Return success with the new resume ID
        return jsonify({
            'success': True,
            'resume_id': new_customized_resume.id,
            'comparison_url': url_for('resume.compare_resume', resume_id=new_customized_resume.id)
        })
        
    except Exception as e:
        logger.error(f"Error in API save_customized_resume: {str(e)}")
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Helper function to save a resume to the database
def save_resume(content, filename, file_format, job_id):
    """Save a resume to the database."""
    # Create resume record
    resume = CustomizedResume(
        user_id=current_user.id,
        job_description_id=job_id,
        original_content=content,
        customized_content=content,  # Initially, customized content is the same as original
        file_format=file_format,
        created_at=datetime.utcnow(),
        is_placeholder=False,  # Not a placeholder by default
        streaming_progress=100,  # Full progress by default
        title=filename  # Use filename as default title
    )
    
    # Add and commit to database
    db.session.add(resume)
    db.session.commit()
    
    return resume.id 

# Add a redirect route for incorrect URL pattern
@resume_bp.route('/resume/compare/<int:resume_id>')
@login_required
def compare_resume_redirect(resume_id):
    """Redirect from incorrect URL pattern to correct one."""
    logger.info(f"Redirecting from incorrect URL /resume/compare/{resume_id} to correct URL /compare/{resume_id}")
    return redirect(url_for('resume.compare_resume', resume_id=resume_id)) 