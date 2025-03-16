from flask import Blueprint, request, jsonify, make_response
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token
from backend.extensions import db, api_response
from backend.models import User, JobDescription, CustomizedResume
import logging
from backend.services.file_parser import FileParser
from backend.services.ats_analyzer import EnhancedATSAnalyzer
from backend.services.ai_suggestions import AISuggestions
from backend.services.resume_customizer import ResumeCustomizer
from io import BytesIO
import base64
from werkzeug.utils import secure_filename
import os
from datetime import datetime
import json

# Initialize logger
logger = logging.getLogger(__name__)

# Initialize services
file_parser = FileParser()
ats_analyzer = EnhancedATSAnalyzer()
ai_suggestions = AISuggestions()
resume_customizer = ResumeCustomizer()

# Create API blueprint
api_bp = Blueprint('api', __name__, url_prefix='/api')

# Authentication endpoints
@api_bp.route('/auth/login', methods=['POST'])
def login():
    """API endpoint for user login"""
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    
    user = User.query.filter_by(email=email).first()
    
    if not user or not user.check_password(password):
        return api_response(error="Invalid email or password", status_code=401)
    
    # Generate access token
    access_token = create_access_token(identity=user.id)
    
    # Return token and user data
    return api_response(data={
        "token": access_token,
        "user": user.to_dict()
    })

@api_bp.route('/auth/register', methods=['POST'])
def register():
    """API endpoint for user registration"""
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    
    # Validate required fields
    if not username or not email or not password:
        return api_response(error="Missing required fields", status_code=400)
    
    # Check if email is already registered
    if User.query.filter_by(email=email).first():
        return api_response(error="Email already registered", status_code=409)
    
    # Check if username is already taken
    if User.query.filter_by(username=username).first():
        return api_response(error="Username already taken", status_code=409)
    
    # Create new user
    try:
        user = User(
            username=username,
            email=email
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        # Generate access token for immediate login
        access_token = create_access_token(identity=user.id)
        
        return api_response(data={
            "message": "Registration successful",
            "token": access_token,
            "user": user.to_dict()
        }, status_code=201)
    except Exception as e:
        db.session.rollback()
        logger.error(f"Registration error: {str(e)}")
        return api_response(error="Registration failed", status_code=500)

@api_bp.route('/auth/refresh', methods=['POST'])
@jwt_required()
def refresh_token():
    """Refresh JWT token endpoint"""
    try:
        # Get the identity from the current token
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return api_response(error="User not found", status_code=404)
            
        # Create a new token with a fresh expiration date
        access_token = create_access_token(identity=current_user_id)
        
        # Return the new token
        return api_response(data={
            "token": access_token,
            "user": user.to_dict()
        })
        
    except Exception as e:
        logger.error(f"Token refresh failed: {str(e)}")
        return api_response(error="Token refresh failed", status_code=401)

@api_bp.route('/auth/me', methods=['GET', 'OPTIONS'])
@jwt_required(optional=True)
def get_current_user():
    """Get current authenticated user information"""
    # Handle OPTIONS request for CORS preflight
    if request.method == 'OPTIONS':
        response = jsonify({})
        response.headers.add('Access-Control-Allow-Origin', request.headers.get('Origin', 'http://127.0.0.1:3000'))
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,OPTIONS')
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        return response
        
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user:
        response_data, status_code = api_response(error="User not found", status_code=404)
    else:
        response_data, status_code = api_response(data={"user": user.to_dict()})
    
    # Add CORS headers to the response
    response = make_response(response_data, status_code)
    response.headers.add('Access-Control-Allow-Origin', request.headers.get('Origin', 'http://127.0.0.1:3000'))
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,OPTIONS')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    return response

# Dashboard endpoints
@api_bp.route('/dashboard', methods=['GET'])
@jwt_required()
def get_dashboard():
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

# Resume endpoints
@api_bp.route('/resumes', methods=['GET'])
@jwt_required()
def get_resumes():
    """API endpoint to get all resumes for the current user"""
    user_id = get_jwt_identity()
    
    # Query for the user's resumes
    resumes = CustomizedResume.query.filter_by(user_id=user_id).order_by(
        CustomizedResume.created_at.desc()
    ).all()
    
    # Convert to dictionary format
    resume_data = [resume.to_dict() for resume in resumes]
    
    # Return API response
    return api_response(data={'resumes': resume_data})
    
@api_bp.route('/resumes/<int:resume_id>', methods=['GET'])
@jwt_required()
def get_resume(resume_id):
    """API endpoint to get a specific resume"""
    user_id = get_jwt_identity()
    
    # Query for the specific resume
    resume = CustomizedResume.query.get_or_404(resume_id)
    
    # Check if the resume belongs to the user
    if resume.user_id != user_id:
        return api_response(error="Permission denied", status_code=403)
    
    # Get the associated job description
    job = JobDescription.query.get(resume.job_description_id)
    
    # Return API response with resume and job data
    return api_response(data={
        'resume': resume.to_dict(), 
        'job': job.to_dict() if job else None
    })

@api_bp.route('/resumes/<int:resume_id>', methods=['DELETE'])
@jwt_required()
def delete_resume(resume_id):
    """API endpoint to delete a resume"""
    user_id = get_jwt_identity()
    
    # Query for the specific resume
    resume = CustomizedResume.query.get_or_404(resume_id)
    
    # Check if the resume belongs to the user
    if resume.user_id != user_id:
        user = User.query.get(user_id)
        is_admin = user.is_admin if user else False
        
        if not is_admin:
            return api_response(error="Permission denied", status_code=403)
    
    # Delete the resume
    try:
        db.session.delete(resume)
        db.session.commit()
        return api_response(data={'message': 'Resume deleted successfully'})
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error deleting resume: {str(e)}")
        return api_response(error="Failed to delete resume", status_code=500)

@api_bp.route('/process-resume', methods=['POST', 'OPTIONS'])
# Temporarily comment out JWT requirement for debugging
# @jwt_required()
def process_resume():
    """API endpoint to process and analyze a resume"""
    # Handle OPTIONS request for CORS preflight
    if request.method == 'OPTIONS':
        response = jsonify({})
        response.headers.add('Access-Control-Allow-Origin', request.headers.get('Origin', 'http://localhost:3000'))
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'POST,OPTIONS')
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        return response
        
    # Since we commented out @jwt_required(), we need to handle the case where there's no JWT token
    try:
        user_id = get_jwt_identity()
    except RuntimeError:
        # No JWT token, set user_id to None
        user_id = None
    
    # Check if this is a file upload (multipart/form-data) or JSON request
    resume_text = None
    resume_file = None
    
    if request.content_type and 'multipart/form-data' in request.content_type:
        # Handle form data with file upload
        if 'file' not in request.files:
            return api_response(error="No file part in the request", status_code=400)
        
        file = request.files['file']
        if file.filename == '':
            return api_response(error="No file selected", status_code=400)
        
        # Get file extension
        filename = secure_filename(file.filename)
        file_ext = os.path.splitext(filename)[1].lower()
        
        # Extract text based on file type
        try:
            if file_ext == '.pdf':
                resume_text = file_parser.pdf_extractor.extract_text(file.read())
                file.seek(0)  # Reset file pointer position
            elif file_ext == '.docx':
                resume_text = file_parser.parse_to_markdown(file)
            elif file_ext == '.txt':
                resume_text = file.read().decode('utf-8')
            elif file_ext == '.md':
                resume_text = file.read().decode('utf-8')
            else:
                return api_response(error=f"Unsupported file format: {file_ext}", status_code=400)
        except Exception as e:
            logger.error(f"Error parsing file: {str(e)}")
            return api_response(error=f"Error parsing file: {str(e)}", status_code=500)
    else:
        # Handle JSON request
        data = request.get_json()
        if not data:
            return api_response(error="No data provided", status_code=400)
        
        resume_text = data.get('resume')
        resume_file = data.get('file')
        
        if resume_file:
            # Handle base64 encoded file
            try:
                file_data = base64.b64decode(resume_file.split(',')[1] if ',' in resume_file else resume_file)
                filename = data.get('filename', 'uploaded_resume.pdf')
                file_ext = os.path.splitext(filename)[1].lower()
                
                # Extract text from file
                if file_ext == '.pdf':
                    resume_text = file_parser.pdf_extractor.extract_text(file_data)
                elif file_ext == '.docx':
                    # Use BytesIO to create a file-like object from the bytes
                    file_obj = BytesIO(file_data)
                    file_obj.name = filename  # Set filename attribute for parse_to_markdown
                    resume_text = file_parser.parse_to_markdown(file_obj)
                elif file_ext == '.md':
                    # For markdown, just decode the text
                    resume_text = file_data.decode('utf-8')
                else:
                    return api_response(error=f"Unsupported file format: {file_ext}", status_code=400)
            except Exception as e:
                logger.error(f"Error decoding base64 file: {str(e)}")
                return api_response(error=f"Error processing file: {str(e)}", status_code=500)
    
    # Verify we have resume text at this point
    if not resume_text:
        return api_response(error="No resume content could be extracted", status_code=400)
    
    # Process the resume
    try:
        # Analyze resume with ATS analyzer
        ats_result = ats_analyzer.analyze(resume_text, "Generic Job Description")
        
        # Return processed resume data
        response_data, status_code = api_response(data={
            'resume_text': resume_text,
            'ats_score': ats_result['score'],
            'confidence': ats_result['confidence'],
            'matching_keywords': ats_result['matching_keywords'],
            'missing_keywords': ats_result['missing_keywords']
        })
        response = make_response(response_data, status_code)
        response.headers.add('Access-Control-Allow-Origin', request.headers.get('Origin', 'http://localhost:3000'))
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'POST,OPTIONS')
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        return response
    except Exception as e:
        logger.error(f"Resume processing error: {str(e)}")
        response_data, status_code = api_response(error=f"Failed to process resume: {str(e)}", status_code=500)
        response = make_response(response_data, status_code)
        response.headers.add('Access-Control-Allow-Origin', request.headers.get('Origin', 'http://localhost:3000'))
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'POST,OPTIONS')
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        return response

# Job description endpoints
@api_bp.route('/jobs', methods=['GET'])
@jwt_required()
def get_jobs():
    """API endpoint to get all job descriptions for the current user"""
    user_id = get_jwt_identity()
    
    # Query for the user's job descriptions
    jobs = JobDescription.query.filter_by(user_id=user_id).order_by(
        JobDescription.created_at.desc()
    ).all()
    
    # Convert to dictionary format
    job_data = [job.to_dict() for job in jobs]
    
    # Return API response
    return api_response(data={'jobs': job_data})

@api_bp.route('/jobs/<int:job_id>', methods=['GET'])
@jwt_required()
def get_job(job_id):
    """API endpoint to get a specific job description"""
    user_id = get_jwt_identity()
    
    # Query for the specific job
    job = JobDescription.query.get_or_404(job_id)
    
    # Check if the job belongs to the user
    if job.user_id != user_id:
        user = User.query.get(user_id)
        is_admin = user.is_admin if user else False
        
        if not is_admin:
            return api_response(error="Permission denied", status_code=403)
    
    # Return API response
    return api_response(data={'job': job.to_dict()})

@api_bp.route('/jobs/url', methods=['POST'])
@jwt_required()
def submit_job_url():
    """API endpoint to submit a job URL"""
    user_id = get_jwt_identity()
    data = request.get_json()
    
    # Get URL from request
    job_url = data.get('url')
    
    if not job_url:
        return api_response(error="No URL provided", status_code=400)
    
    # Process the job URL
    # Note: Implement the actual URL scraping logic here
    job_title = "Job Title from URL"  # Placeholder
    job_content = "Job Description Content from URL"  # Placeholder
    
    # Save the job description
    try:
        job = JobDescription(
            title=job_title,
            content=job_content,
            url=job_url,
            user_id=user_id
        )
        db.session.add(job)
        db.session.commit()
        
        return api_response(data={'job': job.to_dict()}, status_code=201)
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error saving job from URL: {str(e)}")
        return api_response(error="Failed to save job description", status_code=500)

@api_bp.route('/jobs/text', methods=['POST'])
@jwt_required()
def submit_job_text():
    """API endpoint to submit job description text"""
    user_id = get_jwt_identity()
    data = request.get_json()
    
    # Get data from request
    job_title = data.get('title')
    job_content = data.get('content')
    
    if not job_title or not job_content:
        return api_response(error="Missing required fields", status_code=400)
    
    # Save the job description
    try:
        job = JobDescription(
            title=job_title,
            content=job_content,
            user_id=user_id
        )
        db.session.add(job)
        db.session.commit()
        
        return api_response(data={'job': job.to_dict()}, status_code=201)
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error saving job from text: {str(e)}")
        return api_response(error="Failed to save job description", status_code=500)

# Resume customization endpoints
@api_bp.route('/customize-resume', methods=['POST'])
@jwt_required()
def customize_resume():
    """API endpoint to customize a resume for a job"""
    user_id = get_jwt_identity()
    data = request.get_json()
    
    # Get data from request
    resume_content = data.get('resume')
    job_id = data.get('job_id')
    customization_level = data.get('level', 'balanced')
    industry = data.get('industry')
    
    if not resume_content or not job_id:
        return api_response(error="Missing required fields", status_code=400)
    
    # Get the job description
    job = JobDescription.query.get(job_id)
    if not job:
        return api_response(error="Job description not found", status_code=404)
    
    # Verify job belongs to user
    if job.user_id != user_id:
        return api_response(error="Permission denied", status_code=403)
    
    # Analyze original resume
    original_ats_score, original_confidence, original_matching, original_missing = ats_analyzer.analyze(resume_content, job.content)
    
    # Customize the resume
    try:
        result = resume_customizer.customize_resume(
            resume_content=resume_content,
            job_description=job.content,
            customization_level=customization_level,
            industry=industry
        )
        
        # Get customized content from result
        customized_content = result.get('customized_resume', '')
        
        # Analyze the customized resume
        ats_score, confidence, matching_keywords, missing_keywords = ats_analyzer.analyze(customized_content, job.content)
        
        # Calculate improvement
        improvement = round(ats_score - original_ats_score, 1) if original_ats_score is not None and ats_score is not None else 0
        
        # Get optimization data from result
        optimization_data = result.get('optimization_data', {})
        comparison_data = result.get('comparison_data', {})
        customization_notes = result.get('customization_notes', '')
        
        # Create customized resume record
        customized_resume = CustomizedResume(
            original_content=resume_content,
            customized_content=customized_content,
            job_description_id=job.id,
            user_id=user_id,
            original_ats_score=original_ats_score,
            ats_score=ats_score,
            improvement=improvement,
            confidence=confidence,
            matching_keywords=matching_keywords,
            missing_keywords=missing_keywords,
            file_format='md',
            comparison_data=comparison_data,
            optimization_data=optimization_data,
            customization_level=customization_level,
            industry=industry,
            customization_notes=customization_notes
        )
        
        db.session.add(customized_resume)
        db.session.commit()
        
        # Return customization results
        return api_response(data={
            'resume': customized_resume.to_dict(),
            'job': job.to_dict()
        }, status_code=201)
    
    except Exception as e:
        db.session.rollback()
        logger.error(f"Resume customization error: {str(e)}")
        return api_response(error=f"Failed to customize resume: {str(e)}", status_code=500)

@api_bp.route('/compare/<int:resume_id>', methods=['GET'])
@jwt_required()
def compare_resume(resume_id):
    """API endpoint to get comparison data between original and customized resume"""
    user_id = get_jwt_identity()
    
    # Get the customized resume
    resume = CustomizedResume.query.get_or_404(resume_id)
    
    # Check if resume belongs to user
    if resume.user_id != user_id:
        return api_response(error="Permission denied", status_code=403)
    
    # Get job description
    job = JobDescription.query.get(resume.job_description_id)
    
    # Return comparison data
    return api_response(data={
        'resume': resume.to_dict(),
        'job': job.to_dict() if job else None,
        'comparison': resume.comparison_data,
        'improvement': resume.improvement,
        'original_ats_score': resume.original_ats_score,
        'customized_ats_score': resume.ats_score
    })

# Statistics and analytics endpoints
@api_bp.route('/statistics', methods=['GET'])
@jwt_required()
def get_statistics():
    """API endpoint to get usage statistics for the current user"""
    user_id = get_jwt_identity()
    
    # Get user's customized resumes
    resumes = CustomizedResume.query.filter_by(user_id=user_id).all()
    
    # Get user's job descriptions
    jobs = JobDescription.query.filter_by(user_id=user_id).all()
    
    # Calculate statistics
    total_resumes = len(resumes)
    total_jobs = len(jobs)
    
    # Calculate average improvement
    if total_resumes > 0:
        valid_scores = [r.improvement for r in resumes if r.improvement is not None]
        avg_improvement = sum(valid_scores) / len(valid_scores) if valid_scores else 0
    else:
        avg_improvement = 0
    
    # Return statistics
    return api_response(data={
        'total_resumes': total_resumes,
        'total_jobs': total_jobs,
        'avg_improvement': round(avg_improvement, 1),
        'last_customization': resumes[0].created_at.isoformat() if resumes else None
    })

@api_bp.route('/test', methods=['GET'])
def test_api():
    """Simple endpoint to test API connectivity"""
    return api_response(data={"message": "API is working correctly"})