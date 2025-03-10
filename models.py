from extensions import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import hashlib

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    # ensure password hash field has length of at least 256
    password_hash = db.Column(db.String(256))
    is_admin = db.Column(db.Boolean, default=False)
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
            'email': self.email,
            'is_admin': self.is_admin
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
    original_id = db.Column(db.Integer, db.ForeignKey('customized_resume.id'), nullable=True)  # ID of the original resume this was customized from
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    original_ats_score = db.Column(db.Float)  # Original ATS score before customization
    ats_score = db.Column(db.Float)  # New ATS score after customization
    matching_keywords = db.Column(db.JSON)
    missing_keywords = db.Column(db.JSON)
    file_format = db.Column(db.String(10), default='md')  # 'md', 'docx', 'pdf'
    original_bytes = db.Column(db.LargeBinary, nullable=True)  # Store original file bytes for non-markdown files
    comparison_data = db.Column(db.JSON, nullable=True)  # Detailed comparison between original and customized
    added_keywords_count = db.Column(db.Integer, default=0)  # Count of keywords added
    changes_count = db.Column(db.Integer, default=0)  # Total number of changes made
    
    # Feedback and outcome tracking fields
    user_rating = db.Column(db.Integer, nullable=True)  # 1-5 star rating
    user_feedback = db.Column(db.Text, nullable=True)   # Text feedback
    was_effective = db.Column(db.Boolean, nullable=True)  # Did they get an interview?
    interview_secured = db.Column(db.Boolean, nullable=True)  # Did they get an interview?
    job_secured = db.Column(db.Boolean, nullable=True)  # Did they get the job?
    feedback_date = db.Column(db.DateTime, nullable=True)  # When feedback was provided
    
    def to_dict(self):
        return {
            'id': self.id,
            'original_content': self.original_content,
            'customized_content': self.customized_content,
            'job_description_id': self.job_description_id,
            'user_id': self.user_id,
            'created_at': self.created_at.isoformat(),
            'original_ats_score': self.original_ats_score,
            'ats_score': self.ats_score,
            'matching_keywords': self.matching_keywords,
            'missing_keywords': self.missing_keywords,
            'file_format': self.file_format,
            'comparison_data': self.comparison_data,
            'added_keywords_count': self.added_keywords_count,
            'changes_count': self.changes_count,
            'user_rating': self.user_rating,
            'user_feedback': self.user_feedback,
            'was_effective': self.was_effective,
            'interview_secured': self.interview_secured,
            'job_secured': self.job_secured,
            'feedback_date': self.feedback_date.isoformat() if self.feedback_date else None
        }

class PDFCache(db.Model):
    """
    Cache for extracted PDF content to improve performance for large files.
    """
    id = db.Column(db.Integer, primary_key=True)
    # SHA-256 hash of the PDF content (used as cache key)
    content_hash = db.Column(db.String(64), unique=True, nullable=False, index=True)
    # The extracted text content
    extracted_text = db.Column(db.Text, nullable=False)
    # File size in bytes
    file_size = db.Column(db.Integer, nullable=False)
    # Pages in the PDF
    page_count = db.Column(db.Integer, nullable=False)
    # When the cache entry was created
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    # When the cache entry was last accessed
    last_accessed = db.Column(db.DateTime, default=datetime.utcnow)
    # Number of times this cache entry has been used
    hit_count = db.Column(db.Integer, default=1)
    
    @staticmethod
    def generate_hash(pdf_bytes):
        """
        Generate a SHA-256 hash from PDF bytes to use as cache key.
        """
        return hashlib.sha256(pdf_bytes).hexdigest()
        
    @classmethod
    def get_from_cache(cls, pdf_bytes):
        """
        Try to retrieve cached content using the PDF file's hash.
        Returns None if not found in cache.
        """
        content_hash = cls.generate_hash(pdf_bytes)
        cache_entry = cls.query.filter_by(content_hash=content_hash).first()
        
        if cache_entry:
            # Update access statistics
            cache_entry.last_accessed = datetime.utcnow()
            cache_entry.hit_count += 1
            db.session.commit()
            return cache_entry.extracted_text
            
        return None
        
    @classmethod
    def add_to_cache(cls, pdf_bytes, extracted_text, page_count):
        """
        Add extracted PDF content to cache.
        """
        content_hash = cls.generate_hash(pdf_bytes)
        file_size = len(pdf_bytes)
        
        # Check if already exists (shouldn't happen normally, but just in case)
        existing = cls.query.filter_by(content_hash=content_hash).first()
        if existing:
            existing.extracted_text = extracted_text
            existing.file_size = file_size
            existing.page_count = page_count
            existing.last_accessed = datetime.utcnow()
            existing.hit_count += 1
        else:
            # Create new cache entry
            cache_entry = cls(
                content_hash=content_hash,
                extracted_text=extracted_text,
                file_size=file_size,
                page_count=page_count
            )
            db.session.add(cache_entry)
            
        db.session.commit()
        return extracted_text
        
    @classmethod
    def clean_old_entries(cls, max_age_days=30, keep_min=100):
        """
        Remove old cache entries to prevent unlimited growth.
        Keeps at least keep_min most recently used entries.
        """
        # Calculate cutoff date using timedelta instead of day replacement
        cutoff_date = datetime.utcnow() - timedelta(days=max_age_days)
        
        # Count total entries
        total_entries = cls.query.count()
        
        if total_entries <= keep_min:
            return 0
            
        # Find old entries to delete
        old_entries = cls.query.filter(
            cls.last_accessed < cutoff_date
        ).order_by(
            cls.hit_count,  # Delete least used first
            cls.last_accessed  # Then oldest
        ).limit(total_entries - keep_min).all()
        
        # Delete entries
        deleted_count = 0
        for entry in old_entries:
            db.session.delete(entry)
            deleted_count += 1
            
        db.session.commit()
        return deleted_count

class CustomizationEvaluation(db.Model):
    """
    Stores evaluations of resume customizations based on metrics and feedback
    """
    id = db.Column(db.Integer, primary_key=True)
    customized_resume_id = db.Column(db.Integer, db.ForeignKey('customized_resume.id'))
    customized_resume = db.relationship('CustomizedResume', backref=db.backref('evaluations', lazy='dynamic'))
    evaluation_text = db.Column(db.Text, nullable=False)
    metrics = db.Column(db.JSON, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    applied_to_model = db.Column(db.Boolean, default=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'customized_resume_id': self.customized_resume_id,
            'evaluation_text': self.evaluation_text,
            'metrics': self.metrics,
            'created_at': self.created_at.isoformat(),
            'applied_to_model': self.applied_to_model
        }


class OptimizationSuggestion(db.Model):
    """
    Stores system optimization suggestions based on analysis of multiple evaluations
    """
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    based_on_evaluations = db.Column(db.Integer, nullable=False)  # Number of evaluations used
    implemented = db.Column(db.Boolean, default=False)
    implementation_date = db.Column(db.DateTime, nullable=True)
    implementation_notes = db.Column(db.Text, nullable=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'content': self.content,
            'created_at': self.created_at.isoformat(),
            'based_on_evaluations': self.based_on_evaluations,
            'implemented': self.implemented,
            'implementation_date': self.implementation_date.isoformat() if self.implementation_date else None,
            'implementation_notes': self.implementation_notes
        }


class ABTest(db.Model):
    """
    Stores A/B test configurations for testing optimization suggestions
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    variants = db.Column(db.JSON, nullable=False)  # Different prompt variants being tested
    start_date = db.Column(db.DateTime, default=datetime.utcnow)
    end_date = db.Column(db.DateTime, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    results = db.Column(db.JSON, nullable=True)  # Metrics for each variant
    winner = db.Column(db.String(50), nullable=True)  # Which variant performed best
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'variants': self.variants,
            'start_date': self.start_date.isoformat(),
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'is_active': self.is_active,
            'results': self.results,
            'winner': self.winner
        }