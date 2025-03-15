from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash, make_response
from flask_login import login_user, logout_user, login_required, current_user
from models import User, db
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError
import logging

logger = logging.getLogger(__name__)

auth_bp = Blueprint('auth', __name__)

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=64)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
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
def login():
    # Check if this is an API request or a browser request
    if request.is_json:
        # API login
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        
        user = User.query.filter_by(email=email).first()
        
        if not user or not user.check_password(password):
            return jsonify({"error": "Invalid email or password"}), 401
        
        # Generate access token
        access_token = create_access_token(identity=user.id)
        
        # Create response with both token and user data
        response_data = {
            "token": access_token,
            "user": user.to_dict()
        }
        
        # For session-based auth too (optional)
        login_user(user)
        
        return jsonify(response_data), 200
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
def logout():
    # Check if this is an API request or a browser request
    if request.is_json or request.method == 'POST':
        # API logout
        logout_user()
        response = jsonify({"message": "Successfully logged out"})
        response.delete_cookie('access_token_cookie')
        return response, 200
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
            return jsonify({"user": user.to_dict()}), 200
    
    # Fall back to session-based auth
    if current_user.is_authenticated:
        return jsonify({"user": current_user.to_dict()}), 200
    
    return jsonify({"error": "Not authenticated"}), 401


@auth_bp.route('/register', methods=['POST'])
def api_register():
    """API endpoint for user registration"""
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400
        
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    
    # Validate required fields
    if not username or not email or not password:
        return jsonify({"error": "Missing required fields"}), 400
    
    # Check if email is already registered
    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email already registered"}), 409
    
    # Check if username is already taken
    if User.query.filter_by(username=username).first():
        return jsonify({"error": "Username already taken"}), 409
    
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
        
        return jsonify({
            "message": "Registration successful",
            "token": access_token,
            "user": user.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        logger.error(f"Registration error: {str(e)}")
        return jsonify({"error": "Registration failed"}), 500