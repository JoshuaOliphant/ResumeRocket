from extensions import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    # ensure password hash field has length of at least 256
    password_hash = db.Column(db.String(256))
    job_descriptions = db.relationship('JobDescription', backref='user', lazy='dynamic')
    customized_resumes = db.relationship('CustomizedResume', backref='user', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email
        }

class JobDescription(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    url = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'url': self.url,
            'created_at': self.created_at.isoformat(),
            'user_id': self.user_id
        }

class CustomizedResume(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    original_content = db.Column(db.Text, nullable=False)
    customized_content = db.Column(db.Text, nullable=False)
    job_description_id = db.Column(db.Integer, db.ForeignKey('job_description.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    ats_score = db.Column(db.Float)
    matching_keywords = db.Column(db.JSON)
    missing_keywords = db.Column(db.JSON)

    def to_dict(self):
        return {
            'id': self.id,
            'original_content': self.original_content,
            'customized_content': self.customized_content,
            'job_description_id': self.job_description_id,
            'user_id': self.user_id,
            'created_at': self.created_at.isoformat(),
            'ats_score': self.ats_score,
            'matching_keywords': self.matching_keywords,
            'missing_keywords': self.missing_keywords
        }