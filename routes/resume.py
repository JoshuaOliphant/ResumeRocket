from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session, send_file
from flask_login import login_required, current_user
from datetime import datetime
from io import BytesIO
from extensions import db
from models import JobDescription, CustomizedResume, User, OptimizationSuggestion
from services.file_parser import FileParser
from services.ats_analyzer import EnhancedATSAnalyzer
from services.ai_suggestions import AISuggestions
from services.resume_customizer import ResumeCustomizer
import logging

# Initialize logger
logger = logging.getLogger(__name__)

# Initialize services
file_parser = FileParser()
ats_analyzer = EnhancedATSAnalyzer()
ai_suggestions = AISuggestions()
resume_customizer = ResumeCustomizer()

# Create resume blueprint
resume_bp = Blueprint('resume', __name__)

@resume_bp.route('/customize-resume', methods=['POST'])
@login_required
def customize_resume():
    """Handle customization of resume based on job description."""
    logger.debug("Handling customize-resume request")
    
    # Get form data
    resume_id = request.form.get('resume_id')
    job_id = request.form.get('job_id')
    
    logger.debug(f"Form data received: {request.form}")
    logger.debug(f"Raw values - resume_id: {resume_id}, job_id: {job_id}")
    
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
    
    # Get original resume content and format
    original_content = original_resume.original_content
    file_format = original_resume.file_format
    
    logger.debug(f"Found original resume content with format: {file_format}")
    
    # Customize resume based on job description
    customized_content, changes, keywords = resume_customizer.customize(
        original_content, 
        job.content,
        file_format
    )
    
    logger.debug("Generated customized resume content")
    
    # Save customized resume to database
    added_keywords_count = len(keywords['added'])
    changes_count = sum(len(changes[section]) for section in changes)
    
    logger.debug(f"Customization added {added_keywords_count} keywords with {changes_count} total changes")
    
    # Create new customized resume record
    customized_resume = CustomizedResume(
        user_id=current_user.id, 
        job_description_id=job.id,
        original_id=resume_id,
        original_content=original_content,
        customized_content=customized_content,
        file_format=file_format,
        original_ats_score=original_resume.original_ats_score,
        ats_score=original_resume.ats_score,
        added_keywords_count=added_keywords_count,
        changes_count=changes_count,
        created_at=datetime.utcnow()
    )
    
    # Add and commit to database
    db.session.add(customized_resume)
    db.session.commit()
    
    logger.debug(f"Created customized resume with ID: {customized_resume.id}")
    
    # Redirect to view customized resume
    return redirect(url_for('resume.view_customized_resume', resume_id=customized_resume.id))

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
    suggestions = ai_suggestions.generate_suggestions(
        resume_text, 
        job_description, 
        ats_results
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

@resume_bp.route('/api/analyze_resume', methods=['POST'])
@login_required
def analyze_resume():
    """Analyze a resume against a job description."""
    # Debug log the incoming form data
    logger.debug(f"Form data received: {request.form}")
    logger.debug(f"Files received: {request.files}")
    
    # Check if resume is provided as file or text
    if 'resume' in request.files and request.files['resume'].filename:
        # Get resume file
        file = request.files['resume']
        logger.debug(f"Resume file received: {file.filename}")
        
        # Parse resume content from file
        try:
            resume_content = file_parser.parse(file)
            file_format = file_parser.determine_format(file)
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
            from routes.jobs import jobs_bp
            
            # Create job record via jobs blueprint
            result = jobs_bp.handle_job_url_submission(job_url, resume_content)
            
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
    suggestions = ai_suggestions.generate_suggestions(
        resume_content, 
        job_description, 
        ats_results
    )
    
    logger.debug(f"Generated {len(suggestions)} AI suggestions")
    
    logger.debug(f"Rendering template with resume_id={resume_id}, job_id={job.id}")
    
    # Return results as JSON
    return jsonify({
        'resume_id': resume_id,
        'job_id': job.id,
        'ats_score': ats_results,
        'suggestions': suggestions
    })

@resume_bp.route('/customized-resume/<int:resume_id>')
@login_required
def view_customized_resume(resume_id):
    """View a customized resume."""
    # Load customized resume from database
    resume = CustomizedResume.query.get_or_404(resume_id)
    
    # Check if resume belongs to current user
    if resume.user_id != current_user.id and not current_user.is_admin:
        flash('You do not have permission to view this resume.', 'danger')
        return redirect(url_for('dashboard.user_dashboard'))
    
    # Get job description
    job = JobDescription.query.get(resume.job_description_id)
    
    # Render template with data
    return render_template(
        'customized_resume.html',
        resume=resume,
        job=job
    )

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
    
    # Render template with data
    return render_template(
        'customized_resume_comparison.html',
        resume=resume,
        original=original,
        job=job
    )

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
    
    # Get feedback data
    rating = request.form.get('rating', type=int)
    comments = request.form.get('comments')
    status = request.form.get('status')
    
    # Validate data
    if rating is None or rating < 1 or rating > 5:
        return jsonify({'error': 'Invalid rating. Must be between 1 and 5.'}), 400
        
    # Update resume with feedback
    resume.user_rating = rating
    resume.user_feedback = comments
    resume.status = status if status else resume.status
    
    # Save changes
    db.session.commit()
    
    # Return success
    return jsonify({'success': True})

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
        created_at=datetime.utcnow()
    )
    
    # Add and commit to database
    db.session.add(resume)
    db.session.commit()
    
    return resume.id 