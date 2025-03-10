from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from extensions import db
from models import User, ABTest, OptimizationSuggestion
from functools import wraps
from services.feedback_loop import FeedbackLoop

# Create admin blueprint
admin_bp = Blueprint('admin', __name__)

# Initialize feedback loop service
feedback_loop = FeedbackLoop()

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

@admin_bp.route('/admin/feedback-loop/evaluations', methods=['GET'])
@admin_required
def feedback_evaluations():
    """Display the resume evaluations."""
    evaluations = feedback_loop.list_evaluations()
    return render_template(
        'admin/feedback_evaluations.html', 
        evaluations=evaluations
    )

@admin_bp.route('/admin/feedback-loop/optimize', methods=['POST'])
@admin_required
def optimize_resume():
    """Generate optimization suggestions for a resume."""
    resume_id = request.form.get('resume_id', type=int)
    optimization = feedback_loop.generate_optimization(resume_id)
    return jsonify({'optimization_id': optimization.id})

@admin_bp.route('/admin/feedback-loop/ab-test/<int:optimization_id>', methods=['POST'])
@admin_required
def create_ab_test(optimization_id):
    """Create A/B test from optimization suggestion."""
    test_id = feedback_loop.create_ab_test(optimization_id)
    return jsonify({'test_id': test_id})

@admin_bp.route('/admin/feedback-loop/ab-test/<int:test_id>/analyze', methods=['POST'])
@admin_required
def analyze_test(test_id):
    """Analyze A/B test results."""
    result = feedback_loop.analyze_test(test_id)
    return jsonify(result)

@admin_bp.route('/admin/feedback-loop/ab-test/<int:test_id>/apply/<int:optimization_id>', methods=['POST'])
@admin_required
def apply_optimization(test_id, optimization_id):
    """Apply optimization to all future resumes."""
    feedback_loop.apply_optimization(test_id, optimization_id)
    return jsonify({'success': True})

@admin_bp.route('/admin/feedback-loop/dashboard', methods=['GET'])
@admin_required
def feedback_dashboard():
    """Display the feedback dashboard."""
    # Get feedback data from feedback loop
    evaluations = feedback_loop.list_evaluations()
    optimizations = feedback_loop.list_optimizations()
    tests = feedback_loop.list_ab_tests()
    
    # Render template with data
    return render_template(
        'admin/feedback_dashboard.html',
        evaluations=evaluations,
        optimizations=optimizations,
        tests=tests
    )

@admin_bp.route('/admin/users', methods=['GET'])
@admin_required
def manage_users():
    """Display user management interface."""
    users = User.query.all()
    return render_template('admin/users.html', users=users)

@admin_bp.route('/admin/users/<int:user_id>/toggle-admin', methods=['POST'])
@admin_required
def toggle_admin(user_id):
    """Toggle admin status for a user."""
    user = User.query.get_or_404(user_id)
    
    # Prevent removing admin from yourself
    if user.id == current_user.id:
        flash('You cannot remove admin status from yourself.', 'danger')
    else:
        # Toggle admin status
        user.is_admin = not user.is_admin
        db.session.commit()
        action = 'granted' if user.is_admin else 'revoked'
        flash(f'Admin privileges {action} for {user.username}.', 'success')
    
    return redirect(url_for('admin.manage_users')) 