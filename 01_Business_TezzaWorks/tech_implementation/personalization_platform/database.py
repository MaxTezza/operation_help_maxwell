"""
Database initialization and helper functions
"""
import secrets
from models import db, DesignRequest, Design, ClientFeedback, AdminUser
from werkzeug.security import generate_password_hash


def init_db(app):
    """Initialize the database"""
    with app.app_context():
        db.create_all()
        print("Database tables created successfully!")


def create_admin_user(username, password, email):
    """Create a new admin user"""
    password_hash = generate_password_hash(password)
    admin = AdminUser(
        username=username,
        password_hash=password_hash,
        email=email
    )
    db.session.add(admin)
    db.session.commit()
    return admin


def generate_gallery_token():
    """Generate a secure random token for client gallery links"""
    return secrets.token_urlsafe(32)


def get_request_by_token(token):
    """Get a design request by its gallery token"""
    return DesignRequest.query.filter_by(gallery_token=token).first()


def get_all_pending_requests():
    """Get all pending design requests"""
    return DesignRequest.query.filter_by(status='pending').order_by(DesignRequest.created_at.desc()).all()


def get_all_requests():
    """Get all design requests"""
    return DesignRequest.query.order_by(DesignRequest.created_at.desc()).all()


def update_request_status(request_id, new_status):
    """Update the status of a design request"""
    request = DesignRequest.query.get(request_id)
    if request:
        request.status = new_status
        db.session.commit()
    return request
