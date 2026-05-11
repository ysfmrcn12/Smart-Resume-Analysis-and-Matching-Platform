"""Database models."""
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from app import db


class User(db.Model):
    """User account model."""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'hr' or 'applicant'
    name = db.Column(db.String(120))
    company = db.Column(db.String(120))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    cvs = db.relationship('UserCV', backref='user', lazy=True, cascade='all, delete-orphan')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'role': self.role,
            'name': self.name,
            'company': self.company,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class UserCV(db.Model):
    """User uploaded CVs."""
    __tablename__ = 'user_cvs'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    filepath = db.Column(db.String(512), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'filename': self.filename,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class JobPosting(db.Model):
    """Job posting model."""
    __tablename__ = 'job_postings'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    requirements = db.Column(db.JSON, default=[])
    company = db.Column(db.String(200))
    location = db.Column(db.String(200))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    applications = db.relationship('Application', backref='job_posting', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'requirements': self.requirements or [],
            'company': self.company or '',
            'location': self.location or '',
            'user_id': self.user_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }


class Application(db.Model):
    """Candidate application model."""
    __tablename__ = 'applications'

    id = db.Column(db.Integer, primary_key=True)
    job_posting_id = db.Column(db.Integer, db.ForeignKey('job_postings.id'), nullable=False)
    candidate_name = db.Column(db.String(200))
    candidate_email = db.Column(db.String(200))
    resume_text = db.Column(db.Text, nullable=False)
    resume_filename = db.Column(db.String(255))
    compatibility_score = db.Column(db.Float, default=0.0)
    extracted_skills = db.Column(db.JSON)  # List of extracted skills
    extracted_experience = db.Column(db.JSON)  # List of experience entries
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'job_posting_id': self.job_posting_id,
            'candidate_name': self.candidate_name,
            'candidate_email': self.candidate_email,
            'resume_filename': self.resume_filename,
            # Store similarity internally as a 0..1 score.
            # Expose it to the frontend as a percent (0..100).
            'compatibility_score': round(self.compatibility_score * 100, 2) if self.compatibility_score else 0,
            'extracted_skills': self.extracted_skills or [],
            'extracted_experience': self.extracted_experience or [],
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
