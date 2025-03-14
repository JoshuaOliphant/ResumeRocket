import os
import secrets
import logging
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session, send_file
from flask import make_response
from flask_login import LoginManager, login_required, login_user, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import JWTManager
from flask_wtf.csrf import CSRFProtect
from flask_wtf import FlaskForm
from wtforms import HiddenField
from services.ats_analyzer import EnhancedATSAnalyzer
from services.ai_suggestions import AISuggestions
from services.file_parser import FileParser
from services.resume_customizer import ResumeCustomizer
from extensions import db
from models import JobDescription, CustomizedResume, User, ABTest, OptimizationSuggestion
from io import BytesIO
from sqlalchemy import func
from functools import wraps

# Import blueprints
from routes.auth import auth_bp
from routes.jobs import jobs_bp
from routes.dashboard import dashboard_bp
from routes.admin import admin_bp
from routes.resume import resume_bp

# Import the feedback loop service
from services.feedback_loop import FeedbackLoop

logging.basicConfig(level=logging.DEBUG, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("app")

# Create Flask app
app = Flask(__name__)
# Set the absolute path for the database
db_path = os.path.join(os.getcwd(), 'resumerocket.db')
print(f"Using database at: {db_path}")

app.config.from_mapping(
    SECRET_KEY=os.environ.get('SECRET_KEY', 'dev_key'),
    SQLALCHEMY_DATABASE_URI=f"sqlite:///{db_path}",
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
    JWT_SECRET_KEY=os.environ.get('JWT_SECRET_KEY', 'jwt_dev_key'),
    UPLOAD_FOLDER=os.path.join(os.getcwd(), 'uploads'),
    MAX_CONTENT_LENGTH=16 * 1024 * 1024  # 16MB max file size
)

# Initialize Flask extensions
db.init_app(app)
csrf = CSRFProtect(app)
jwt = JWTManager(app)

# Initialize login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'

# Load user
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Initialize services
file_parser = FileParser()
ats_analyzer = EnhancedATSAnalyzer()
ai_suggestions = AISuggestions()
resume_customizer = ResumeCustomizer()
feedback_loop = FeedbackLoop()

# Register blueprints
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(jobs_bp, url_prefix='/api')
app.register_blueprint(dashboard_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(resume_bp)

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

@app.route('/')
def index():
    """Render the homepage."""
    return render_template('index.html')

@app.route('/partials/toggle-input')
def toggle_input_partial():
    """Render the toggle input partial template."""
    input_type = request.args.get('type', 'file')
    upload_type = request.args.get('uploadType')
    return render_template('partials/toggle_input.html', type=input_type, upload_type=upload_type)

@app.route('/partials/toggle-job-input')
def toggle_job_input_partial():
    """Render the toggle job input partial template."""
    input_type = request.args.get('type', 'url')
    return render_template('partials/toggle_job_input.html', type=input_type)

# Create uploads directory if it doesn't exist
with app.app_context():
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Check if database exists and create tables if not
    try:
        if not os.path.exists(db_path):
            logger.info("Database does not exist. Creating tables...")
            db.create_all()
            logger.info("Tables created successfully.")
        
        # Get admin credentials from environment variables
        admin_username = os.environ.get('ADMIN_USERNAME', 'admin')
        admin_password = os.environ.get('ADMIN_PASSWORD', 'admin')
        admin_email = os.environ.get('ADMIN_EMAIL', 'admin@example.com')
        
        # First check if a user with the admin email already exists
        user_with_email = User.query.filter_by(email=admin_email).first()
        
        if user_with_email:
            # If the user exists but username doesn't match the admin username,
            # we'll just update this user to have admin privileges
            if user_with_email.username != admin_username:
                logger.info(f"User with email {admin_email} already exists with username {user_with_email.username}")
                logger.info(f"Granting admin privileges to existing user {user_with_email.username}")
                user_with_email.is_admin = True
                
                # Optionally update the password if specified and not default
                if admin_password != 'admin':
                    user_with_email.password_hash = generate_password_hash(admin_password)
                    logger.info(f"Updated password for user {user_with_email.username}")
                
                db.session.commit()
            else:
                # Email exists with matching username - this is the admin user
                # Update password if needed
                if admin_password != 'admin':
                    user_with_email.password_hash = generate_password_hash(admin_password)
                    db.session.commit()
                    logger.info(f"Updated password for admin user {admin_username}")
        else:
            # No user with this email exists, check by username
            admin_exists = User.query.filter_by(username=admin_username).first()
        
            # Create or update the admin user
            if not admin_exists:
                # Create new admin user
                admin_user = User(
                    username=admin_username,
                    email=admin_email,
                    password_hash=generate_password_hash(admin_password),
                    is_admin=True
                )
                db.session.add(admin_user)
                db.session.commit()
                logger.info(f"Admin user '{admin_username}' created successfully.")
            else:
                # Admin with this username exists but different email
                # Update email and password if needed
                if admin_exists.email != admin_email:
                    admin_exists.email = admin_email
                    logger.info(f"Updated email for admin user {admin_username}")
                
                # Update password if needed
                if admin_password != 'admin':
                    admin_exists.password_hash = generate_password_hash(admin_password)
                    logger.info(f"Updated password for admin user {admin_username}")
                
                db.session.commit()
    except Exception as ex:
        logger.error(f"Error setting up admin user: {str(ex)}")

# Uncomment below to run directly from this file (not recommended)
# if __name__ == "__main__":
#    app.run(host='0.0.0.0', port=8080, debug=True)