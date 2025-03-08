from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from models import User, db
from flask_jwt_extended import create_access_token
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired, Email

auth_bp = Blueprint('auth', __name__)

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        data = request.form

        if not data or not data.get('email') or not data.get('password') or not data.get('username'):
            flash('Missing required fields', 'danger')
            return redirect(url_for('auth.register'))

        if User.query.filter_by(email=data['email']).first():
            flash('Email already registered', 'danger')
            return redirect(url_for('auth.register'))

        if User.query.filter_by(username=data['username']).first():
            flash('Username already taken', 'danger')
            return redirect(url_for('auth.register'))

        user = User(
            username=data['username'],
            email=data['email']
        )
        user.set_password(data['password'])

        db.session.add(user)
        db.session.commit()

        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            access_token = create_access_token(identity=user.id)
            flash('Logged in successfully!', 'success')
            return redirect(url_for('index'))

        flash('Invalid email or password', 'danger')
        return redirect(url_for('auth.login'))

    return render_template('login.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully', 'success')
    return redirect(url_for('auth.login'))

@auth_bp.route('/me')
@login_required
def get_current_user():
    return jsonify(current_user.to_dict())