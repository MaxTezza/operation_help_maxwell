"""
Database models for the TezzaWorks Personalization Platform
"""
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class DesignRequest(db.Model):
    """Model for client design consultation requests"""
    __tablename__ = 'design_requests'

    id = db.Column(db.Integer, primary_key=True)

    # Client Information
    company_name = db.Column(db.String(200), nullable=False)
    contact_name = db.Column(db.String(200), nullable=False)
    contact_email = db.Column(db.String(200), nullable=False)
    contact_phone = db.Column(db.String(50), nullable=True)

    # Brand Information
    brand_keywords = db.Column(db.Text, nullable=False)
    brand_colors = db.Column(db.String(500), nullable=True)
    target_audience = db.Column(db.String(500), nullable=True)
    additional_notes = db.Column(db.Text, nullable=True)

    # File Upload
    logo_filename = db.Column(db.String(500), nullable=True)

    # Status Tracking
    status = db.Column(db.String(50), default='pending')  # pending, in_progress, completed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Unique link for client gallery
    gallery_token = db.Column(db.String(100), unique=True, nullable=False)

    # Relationships
    designs = db.relationship('Design', backref='request', lazy=True, cascade='all, delete-orphan')
    feedback = db.relationship('ClientFeedback', backref='request', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<DesignRequest {self.company_name}>'


class Design(db.Model):
    """Model for uploaded design options"""
    __tablename__ = 'designs'

    id = db.Column(db.Integer, primary_key=True)
    request_id = db.Column(db.Integer, db.ForeignKey('design_requests.id'), nullable=False)

    # Design Details
    filename = db.Column(db.String(500), nullable=False)
    title = db.Column(db.String(200), nullable=True)
    description = db.Column(db.Text, nullable=True)

    # Client Selection
    is_selected = db.Column(db.Boolean, default=False)

    # Order for display
    display_order = db.Column(db.Integer, default=0)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Design {self.filename}>'


class ClientFeedback(db.Model):
    """Model for client feedback on designs"""
    __tablename__ = 'client_feedback'

    id = db.Column(db.Integer, primary_key=True)
    request_id = db.Column(db.Integer, db.ForeignKey('design_requests.id'), nullable=False)

    # Feedback Content
    selected_designs = db.Column(db.Text, nullable=True)  # JSON string of selected design IDs
    overall_feedback = db.Column(db.Text, nullable=True)
    rating = db.Column(db.Integer, nullable=True)  # 1-5 stars

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<ClientFeedback for Request {self.request_id}>'


class AdminUser(db.Model):
    """Model for admin users (simple auth for MVP)"""
    __tablename__ = 'admin_users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(200), unique=True, nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<AdminUser {self.username}>'
