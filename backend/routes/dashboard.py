from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.extensions import db, api_response, is_api_request, api_route
from backend.models import JobDescription, CustomizedResume, User
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
@api_route
def user_dashboard():
    """Display the user dashboard with all customized resumes."""
    # Get search query if present
    search_query = request.args.get('search', '')
    
    # Determine if it's a session-based or JWT user
    user_id = None
    if current_user.is_authenticated:
        user_id = current_user.id
    elif is_api_request():
        try:
            # For API requests, we might be using JWT
            token_user_id = get_jwt_identity()
            if token_user_id:
                user_id = token_user_id
        except Exception as e:
            return api_response(error="Authentication required", status_code=401)
    
    if not user_id:
        if is_api_request():
            return api_response(error="Authentication required", status_code=401)
        else:
            return redirect(url_for('auth.login'))
    
    # Build query for customized resumes
    query = db.session.query(
        CustomizedResume,
        JobDescription.title.label('job_title'),
        JobDescription.url.label('job_url')
    ).join(
        JobDescription,
        CustomizedResume.job_description_id == JobDescription.id
    ).filter(
        CustomizedResume.user_id == user_id
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
    
    # Process results into the format expected by the template or API
    dashboard_data = []
    for resume_tuple in results:
        resume = resume_tuple[0]  # The CustomizedResume object
        job_title = resume_tuple.job_title  # Using the label from query
        job_url = resume_tuple.job_url      # Using the label from query
        
        # Calculate improvement if possible
        improvement = 0
        if resume.original_ats_score is not None and resume.ats_score is not None:
            improvement = round(resume.ats_score - resume.original_ats_score, 1)
        
        # Create a job object
        job = {
            'title': job_title,
            'url': job_url
        }
        
        # Add to dashboard data
        dashboard_item = {
            'job': job,
            'improvement': improvement,
            'date': resume.created_at.strftime('%Y-%m-%d %H:%M')
        }
        
        # For API response, add the resume dict representation
        if is_api_request():
            dashboard_item['resume'] = resume.to_dict()
        else:
            # For template rendering, include the full resume object
            dashboard_item['resume'] = resume
            
        dashboard_data.append(dashboard_item)
    
    # Calculate overall statistics
    total_resumes = len(dashboard_data)
    avg_improvement = sum(item['improvement'] for item in dashboard_data) / total_resumes if total_resumes > 0 else 0
    
    # Create response data
    response_data = {
        'dashboard_data': dashboard_data,
        'total_resumes': total_resumes,
        'avg_improvement': round(avg_improvement, 1),
        'search_query': search_query
    }
    
    # Return appropriate response
    if is_api_request():
        return response_data, 200
    else:
        return render_template('user_dashboard.html', **response_data)

@dashboard_bp.route('/dashboard/resume/<int:resume_id>/delete', methods=['GET', 'DELETE'])
@login_required
@api_route
def delete_resume(resume_id):
    """Delete a customized resume."""
    resume = CustomizedResume.query.get_or_404(resume_id)
    
    # Determine user ID based on auth method
    user_id = current_user.id if current_user.is_authenticated else get_jwt_identity()
    is_admin = current_user.is_admin if current_user.is_authenticated else User.query.get(user_id).is_admin if user_id else False
    
    # Check if resume belongs to user
    if resume.user_id != user_id and not is_admin:
        if is_api_request():
            return api_response(error="Permission denied", status_code=403)
        else:
            flash('You do not have permission to delete this resume.', 'danger')
            return redirect(url_for('dashboard.user_dashboard'))
    
    # Delete resume
    db.session.delete(resume)
    db.session.commit()
    
    # Return appropriate response
    if is_api_request():
        return {'message': 'Resume deleted successfully'}, 200
    else:
        flash('Resume deleted successfully!', 'success')
        return redirect(url_for('dashboard.user_dashboard'))

# Dedicated API endpoint for dashboard data
@dashboard_bp.route('/api/dashboard', methods=['GET'])
@jwt_required()
def api_dashboard():
    """API endpoint to get dashboard data"""
    user_id = get_jwt_identity()
    
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
        CustomizedResume.user_id == user_id
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
    
    # Process results
    dashboard_data = []
    for resume_tuple in results:
        resume = resume_tuple[0]  # The CustomizedResume object
        job_title = resume_tuple.job_title  # Using the label from query
        job_url = resume_tuple.job_url      # Using the label from query
        
        # Calculate improvement if possible
        improvement = 0
        if resume.original_ats_score is not None and resume.ats_score is not None:
            improvement = round(resume.ats_score - resume.original_ats_score, 1)
        
        # Add to dashboard data
        dashboard_data.append({
            'resume': resume.to_dict(),
            'job': {
                'title': job_title,
                'url': job_url
            },
            'improvement': improvement,
            'date': resume.created_at.strftime('%Y-%m-%d %H:%M')
        })
    
    # Calculate overall statistics
    total_resumes = len(dashboard_data)
    avg_improvement = sum(item['improvement'] for item in dashboard_data) / total_resumes if total_resumes > 0 else 0
    
    # Return API response
    return api_response(data={
        'dashboard_data': dashboard_data,
        'total_resumes': total_resumes,
        'avg_improvement': round(avg_improvement, 1),
        'search_query': search_query
    })