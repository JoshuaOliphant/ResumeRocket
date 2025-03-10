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
        CustomizedResume.job_id == JobDescription.id
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
    
    # Return dashboard template with results
    return render_template(
        'user_dashboard.html',
        resumes=results,
        search_query=search_query
    )

@dashboard_bp.route('/resume/<int:resume_id>/delete', methods=['GET'])
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