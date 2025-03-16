from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash, make_response
from flask_login import login_user, logout_user, login_required, current_user
from backend.models import User, db
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required, verify_jwt_in_request, create_refresh_token
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError
import logging
from backend.extensions import api_response, is_api_request, api_route
from datetime import datetime, timedelta
from werkzeug.security import check_password_hash

logger = logging.getLogger(__name__)

auth_bp = Blueprint('auth', __name__)

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=64)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])

# Web-based registration (separate endpoint for web forms)
@auth_bp.route('/web-register', methods=['GET', 'POST'])
def web_register():
    form = RegisterForm()
    if form.validate_on_submit():
        # Check if email is already registered
        if User.query.filter_by(email=form.email.data).first():
            flash('Email already registered', 'danger')
            return render_template('register.html', form=form)

        # Check if username is already taken
        if User.query.filter_by(username=form.username.data).first():
            flash('Username already taken', 'danger')
            return render_template('register.html', form=form)

        # Create new user
        user = User(
            username=form.username.data,
            email=form.email.data
        )
        user.set_password(form.password.data)

        db.session.add(user)
        db.session.commit()

        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('register.html', form=form)

@auth_bp.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'error': 'Email and password are required'}), 400

    user = User.query.filter_by(email=email).first()

    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({'error': 'Invalid email or password'}), 401

    # Create access and refresh tokens
    access_token = create_access_token(identity=user.id)
    refresh_token = create_refresh_token(identity=user.id)

    return jsonify({
        'access_token': access_token,
        'refresh_token': refresh_token,
        'user': {
            'id': user.id,
            'email': user.email,
            'name': user.name
        }
    }), 200

@auth_bp.route('/logout', methods=['GET', 'POST', 'OPTIONS'])
@api_route
def logout():
    # Handle OPTIONS request for CORS preflight
    if request.method == 'OPTIONS':
        response = jsonify({})
        return add_cors_headers(response)
        
    # Check if this is an API request or a browser request
    if is_api_request():
        # API logout
        logout_user()
        response = make_response(api_response(data={"message": "Successfully logged out"})[0])
        response.delete_cookie('access_token_cookie')
        return add_cors_headers(response)
    else:
        # Browser logout
        logout_user()
        response = make_response(redirect(url_for('auth.login')))
        response.delete_cookie('access_token_cookie')
        flash('Logged out successfully', 'success')
        return response

@auth_bp.route('/me', methods=['GET', 'OPTIONS'])
@jwt_required(optional=True)
def get_current_user():
    # Handle OPTIONS request for CORS preflight
    if request.method == 'OPTIONS':
        response = jsonify({})
        return add_cors_headers(response)
        
    # Get user from JWT token
    user_id = get_jwt_identity()
    
    if user_id:
        user = User.query.get(user_id)
        if user:
            response_data, status_code = api_response(data={"user": user.to_dict()})
            return add_cors_headers(response_data), status_code
    
    # Fall back to session-based auth
    if current_user.is_authenticated:
        response_data, status_code = api_response(data={"user": current_user.to_dict()})
        return add_cors_headers(response_data), status_code
    
    response_data, status_code = api_response(error="Not authenticated", status_code=401)
    return add_cors_headers(response_data), status_code

@auth_bp.route('/api/refresh', methods=['POST'])
def refresh():
    try:
        current_user = get_jwt_identity()
        new_token = create_access_token(identity=current_user)
        return jsonify({'access_token': new_token}), 200
    except:
        return jsonify({'error': 'Invalid refresh token'}), 401

# Helper function to add CORS headers to response
def add_cors_headers(response):
    origin = request.headers.get('Origin', 'http://127.0.0.1:3000')
    response.headers.add('Access-Control-Allow-Origin', origin)
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'POST,OPTIONS')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    return response

@auth_bp.route('/register', methods=['POST', 'OPTIONS'])
def api_register():
    """API endpoint for user registration"""
    # Handle OPTIONS request for CORS preflight
    if request.method == 'OPTIONS':
        response = jsonify({})
        return add_cors_headers(response)
        
    if not is_api_request():
        # Redirect non-API requests to the web registration form
        return redirect(url_for('auth.web_register'))
        
    data = request.get_json()
    name = data.get('name') # From Next.js form
    email = data.get('email')
    password = data.get('password')
    
    # Use name as username if username is not provided
    username = data.get('username', name)
    
    # Validate required fields
    if not email or not password:
        return api_response(error="Missing required fields", status_code=400)
    
    if not username:
        username = email.split('@')[0]  # Use part of email as username if not provided
    
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
        
        # Get API response
        response_data, status_code = api_response(data={
            "message": "Registration successful",
            "token": access_token,
            "user": user.to_dict()
        }, status_code=201)
        
        # Add CORS headers to the response
        return add_cors_headers(response_data), status_code
    except Exception as e:
        db.session.rollback()
        logger.error(f"Registration error: {str(e)}")
        response_data, status_code = api_response(error="Registration failed", status_code=500)
        return add_cors_headers(response_data), status_code