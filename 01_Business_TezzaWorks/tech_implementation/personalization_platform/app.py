"""
TezzaWorks Customer Personalization Platform - Main Application
"""
import os
from flask import Flask, render_template
from models import db
from database import init_db, create_admin_user
from routes.client import client_bp
from routes.admin import admin_bp


def create_app():
    """Create and configure the Flask application"""
    app = Flask(__name__)

    # Configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tezzaworks.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

    # Initialize database
    db.init_app(app)

    # Register blueprints
    app.register_blueprint(client_bp)
    app.register_blueprint(admin_bp)

    # Create upload directories
    os.makedirs('static/uploads', exist_ok=True)
    os.makedirs('static/pdfs', exist_ok=True)

    # Initialize database tables
    with app.app_context():
        db.create_all()
        print("Database initialized successfully!")

        # Create default admin user if none exists
        from models import AdminUser
        if AdminUser.query.count() == 0:
            create_admin_user('admin', 'admin123', 'admin@tezzaworks.com')
            print("Default admin user created!")
            print("Username: admin")
            print("Password: admin123")
            print("IMPORTANT: Change this password in production!")

    # Error handlers
    @app.errorhandler(404)
    def not_found(e):
        return render_template('error.html', message='Page not found'), 404

    @app.errorhandler(500)
    def server_error(e):
        return render_template('error.html', message='Internal server error'), 500

    return app


if __name__ == '__main__':
    app = create_app()
    print("\n" + "=" * 60)
    print("TezzaWorks Customer Personalization Platform")
    print("=" * 60)
    print("\nServer starting...")
    print("Client Form: http://localhost:5001/")
    print("Admin Dashboard: http://localhost:5001/admin/dashboard")
    print("\nDefault Admin Credentials:")
    print("  Username: admin")
    print("  Password: admin123")
    print("\n" + "=" * 60 + "\n")

    app.run(debug=True, host='0.0.0.0', port=5001)
