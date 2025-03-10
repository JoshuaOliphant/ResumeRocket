from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from extensions import db
from models import JobDescription, CustomizedResume, User
from sqlalchemy import func
from functools import wraps

# Create dashboard blueprint
dashboard_bp = Blueprint('dashboard', __name__)

# Admin required decorator
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if user is authenticated
        if not current_user.is_authenticated:
            return redirect(url_for('auth.login'))
        
        # Check if user is admin
        if not current_user.is_admin:
            flash('Admin access required.', 'danger')
            return redirect(url_for('dashboard.user_dashboard'))
            
        return f(*args, **kwargs)
    return decorated_function

@dashboard_bp.route('/dashboard', methods=['GET'])
@login_required
def user_dashboard():
    """Display the user dashboard with all customized resumes."""
    # Get search query if present
    search_query = request.args.get('search', '')
    
    # Build query for customized resumes
    query = db.session.query(
        CustomizedResume,
        JobDescription.title.label('job_title'),
        JobDescription.url.label('job_url')
    ).join(
        JobDescription,
        CustomizedResume.job_description_id == JobDescription.id
    ).filter(
        CustomizedResume.user_id == current_user.id
    )
    
    # Apply search filter if provided
    if search_query:
        query = query.filter(
            JobDescription.title.ilike(f'%{search_query}%') |
            JobDescription.url.ilike(f'%{search_query}%') |
            JobDescription.content.ilike(f'%{search_query}%')
        )
    
    # Get all results
    results = query.order_by(CustomizedResume.created_at.desc()).all()
    
    # Process results into the format expected by the template
    dashboard_data = []
    for resume_tuple in results:
        resume = resume_tuple[0]  # The CustomizedResume object
        job_title = resume_tuple.job_title  # Using the label from query
        job_url = resume_tuple.job_url      # Using the label from query
        
        # Calculate improvement if possible
        improvement = 0
        if resume.original_ats_score is not None and resume.ats_score is not None:
            improvement = round(resume.ats_score - resume.original_ats_score, 1)
        
        # Create a job object for the template
        job = {
            'title': job_title,
            'url': job_url
        }
        
        # Add to dashboard data
        dashboard_data.append({
            'resume': resume,
            'job': job,
            'improvement': improvement,
            'date': resume.created_at.strftime('%Y-%m-%d %H:%M')
        })
    
    # Calculate overall statistics
    total_resumes = len(dashboard_data)
    avg_improvement = sum(item['improvement'] for item in dashboard_data) / total_resumes if total_resumes > 0 else 0
    
    # Return dashboard template with results
    return render_template(
        'user_dashboard.html',
        dashboard_data=dashboard_data,
        total_resumes=total_resumes,
        avg_improvement=round(avg_improvement, 1),
        search_query=search_query
    )

@dashboard_bp.route('/dashboard/resume/<int:resume_id>/delete', methods=['GET'])
@login_required
def delete_resume(resume_id):
    """Delete a customized resume."""
    resume = CustomizedResume.query.get_or_404(resume_id)
    
    # Check if resume belongs to current user
    if resume.user_id != current_user.id and not current_user.is_admin:
        flash('You do not have permission to delete this resume.', 'danger')
        return redirect(url_for('dashboard.user_dashboard'))
    
    # Delete resume and redirect
    db.session.delete(resume)
    db.session.commit()
    flash('Resume deleted successfully!', 'success')
    return redirect(url_for('dashboard.user_dashboard')) 