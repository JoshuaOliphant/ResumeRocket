from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash, make_response
from flask_login import login_user, logout_user, login_required, current_user
from backend.models import User, db
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required, verify_jwt_in_request
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError
import logging
from backend.extensions import api_response, is_api_request, api_route
from datetime import datetime, timedelta

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

@auth_bp.route('/login', methods=['GET', 'POST'])
@api_route
def login():
    # Check if this is an API request or a browser request
    if is_api_request():
        # API login
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        
        user = User.query.filter_by(email=email).first()
        
        if not user or not user.check_password(password):
            return api_response(error="Invalid email or password", status_code=401)
        
        # Generate access token
        access_token = create_access_token(identity=user.id)
        
        # Create response with both token and user data
        response_data = {
            "token": access_token,
            "user": user.to_dict()
        }
        
        # For session-based auth too (optional)
        login_user(user)
        
        return response_data, 200
    else:
        # Browser form-based login
        form = LoginForm()
        if form.validate_on_submit():
            user = User.query.filter_by(email=form.email.data).first()
            if user and user.check_password(form.password.data):
                login_user(user)
                access_token = create_access_token(identity=user.id)
                
                response = make_response(redirect(url_for('index')))
                # Set JWT cookie for frontend use
                response.set_cookie(
                    'access_token_cookie',
                    access_token,
                    httponly=True,
                    secure=False,  # Set to True in production with HTTPS
                    max_age=86400  # 1 day
                )
                
                flash('Logged in successfully!', 'success')
                return response

            flash('Invalid email or password', 'danger')
            return redirect(url_for('auth.login'))

        return render_template('login.html', form=form)

@auth_bp.route('/logout', methods=['GET', 'POST'])
@api_route
def logout():
    # Check if this is an API request or a browser request
    if is_api_request():
        # API logout
        logout_user()
        response = make_response(api_response(data={"message": "Successfully logged out"})[0])
        response.delete_cookie('access_token_cookie')
        return response
    else:
        # Browser logout
        logout_user()
        response = make_response(redirect(url_for('auth.login')))
        response.delete_cookie('access_token_cookie')
        flash('Logged out successfully', 'success')
        return response

@auth_bp.route('/me')
@jwt_required(optional=True)
def get_current_user():
    # Get user from JWT token
    user_id = get_jwt_identity()
    
    if user_id:
        user = User.query.get(user_id)
        if user:
            return api_response(data={"user": user.to_dict()})
    
    # Fall back to session-based auth
    if current_user.is_authenticated:
        return api_response(data={"user": current_user.to_dict()})
    
    return api_response(error="Not authenticated", status_code=401)

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required()
def refresh_token():
    """
    Refresh the JWT token for authenticated users.
    This endpoint exchanges a valid but aging JWT token for a new one.
    """
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


@auth_bp.route('/register', methods=['POST'])
def api_register():
    """API endpoint for user registration"""
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
        
        return api_response(data={
            "message": "Registration successful",
            "token": access_token,
            "user": user.to_dict()
        }, status_code=201)
    except Exception as e:
        db.session.rollback()
        logger.error(f"Registration error: {str(e)}")
        return api_response(error="Registration failed", status_code=500)