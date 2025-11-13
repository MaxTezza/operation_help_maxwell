"""
TezzaWorks Operations Dashboard - Main Flask Application
"""
from flask import Flask, jsonify
from flask_cors import CORS
from database import init_db, SessionLocal
from routes.clients import clients_bp
from routes.products import products_bp
from routes.orders import orders_bp
from routes.export import export_bp
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def create_app():
    """Create and configure an instance of the Flask application."""
    app = Flask(__name__)

    # Configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    app.config['JSON_SORT_KEYS'] = False

    # Enable CORS for frontend communication
    # In production, restrict to actual domain
    allowed_origins = os.getenv('CORS_ORIGINS', 'http://localhost:3000,http://localhost:3001').split(',')
    CORS(app, resources={
        r"/api/*": {
            "origins": allowed_origins,
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })

    # Register blueprints
    app.register_blueprint(clients_bp)
    app.register_blueprint(products_bp)
    app.register_blueprint(orders_bp)
    app.register_blueprint(export_bp)

    # Health check endpoint
    @app.route('/')
    def index():
        return jsonify({
            'message': 'TezzaWorks Operations Dashboard API',
            'version': '1.0.0',
            'status': 'running'
        })

    @app.route('/api/health')
    def health_check():
        """Health check endpoint"""
        return jsonify({'status': 'healthy'}), 200

    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Endpoint not found'}), 404

    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({'error': 'Internal server error'}), 500

    # Security headers
    @app.after_request
    def set_security_headers(response):
        """Add security headers to all responses"""
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        if os.getenv('FLASK_ENV') == 'production':
            response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        return response

    # Database session cleanup
    @app.teardown_appcontext
    def shutdown_session(exception=None):
        """Clean up database session"""
        SessionLocal.remove()

    return app

if __name__ == '__main__':
    init_db()
    app = create_app()
    # Development server
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_ENV', 'development') == 'development'

    print(f"\nStarting TezzaWorks Operations Dashboard API...")
    print(f"Server running on http://localhost:{port}")
    print(f"Debug mode: {debug}\n")

    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug
    )
