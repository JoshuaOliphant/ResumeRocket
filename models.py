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
    file_format = db.Column(db.String(10), default='md')  # 'md', 'docx', 'pdf'
    original_bytes = db.Column(db.LargeBinary, nullable=True)  # Store original file bytes for non-markdown files

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
            'missing_keywords': self.missing_keywords,
            'file_format': self.file_format
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