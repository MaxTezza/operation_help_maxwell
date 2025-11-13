"""
Client-facing routes for design request submission and gallery viewing
"""
import os
import json
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from werkzeug.utils import secure_filename
from models import db, DesignRequest, Design, ClientFeedback
from database import generate_gallery_token, get_request_by_token

client_bp = Blueprint('client', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'svg', 'pdf'}
UPLOAD_FOLDER = 'static/uploads'


def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@client_bp.route('/')
def index():
    """Landing page with client submission form"""
    return render_template('client_form.html')


@client_bp.route('/submit', methods=['POST'])
def submit_request():
    """Handle client design request submission"""
    try:
        # Get form data
        company_name = request.form.get('company_name')
        contact_name = request.form.get('contact_name')
        contact_email = request.form.get('contact_email')
        contact_phone = request.form.get('contact_phone', '')
        brand_keywords = request.form.get('brand_keywords')
        brand_colors = request.form.get('brand_colors', '')
        target_audience = request.form.get('target_audience', '')
        additional_notes = request.form.get('additional_notes', '')

        # Validation
        if not all([company_name, contact_name, contact_email, brand_keywords]):
            flash('Please fill in all required fields.', 'error')
            return redirect(url_for('client.index'))

        # Handle logo upload
        logo_filename = None
        if 'logo' in request.files:
            file = request.files['logo']
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                # Add timestamp to prevent conflicts
                import time
                timestamp = str(int(time.time()))
                logo_filename = f"{timestamp}_{filename}"
                filepath = os.path.join(UPLOAD_FOLDER, logo_filename)
                os.makedirs(UPLOAD_FOLDER, exist_ok=True)
                file.save(filepath)

        # Generate unique gallery token
        gallery_token = generate_gallery_token()

        # Create design request
        design_request = DesignRequest(
            company_name=company_name,
            contact_name=contact_name,
            contact_email=contact_email,
            contact_phone=contact_phone,
            brand_keywords=brand_keywords,
            brand_colors=brand_colors,
            target_audience=target_audience,
            additional_notes=additional_notes,
            logo_filename=logo_filename,
            gallery_token=gallery_token,
            status='pending'
        )

        db.session.add(design_request)
        db.session.commit()

        # Generate gallery URL
        gallery_url = url_for('client.gallery', token=gallery_token, _external=True)

        return render_template('submission_success.html',
                               company_name=company_name,
                               gallery_url=gallery_url)

    except Exception as e:
        db.session.rollback()
        print(f"Error submitting request: {e}")
        flash('An error occurred. Please try again.', 'error')
        return redirect(url_for('client.index'))


@client_bp.route('/gallery/<token>')
def gallery(token):
    """Client gallery view for a specific design request"""
    design_request = get_request_by_token(token)

    if not design_request:
        return render_template('error.html', message='Gallery not found.'), 404

    # Get associated designs
    designs = Design.query.filter_by(request_id=design_request.id).order_by(Design.display_order).all()

    # Get existing feedback if any
    feedback = ClientFeedback.query.filter_by(request_id=design_request.id).first()

    return render_template('gallery.html',
                           request=design_request,
                           designs=designs,
                           feedback=feedback)


@client_bp.route('/gallery/<token>/feedback', methods=['POST'])
def submit_feedback(token):
    """Handle client feedback submission"""
    design_request = get_request_by_token(token)

    if not design_request:
        return jsonify({'error': 'Gallery not found'}), 404

    try:
        # Get feedback data
        selected_designs = request.form.getlist('selected_designs[]')
        overall_feedback = request.form.get('overall_feedback', '')
        rating = request.form.get('rating', None)

        # Convert rating to int if provided
        if rating:
            rating = int(rating)

        # Check if feedback already exists
        feedback = ClientFeedback.query.filter_by(request_id=design_request.id).first()

        if feedback:
            # Update existing feedback
            feedback.selected_designs = json.dumps(selected_designs)
            feedback.overall_feedback = overall_feedback
            feedback.rating = rating
        else:
            # Create new feedback
            feedback = ClientFeedback(
                request_id=design_request.id,
                selected_designs=json.dumps(selected_designs),
                overall_feedback=overall_feedback,
                rating=rating
            )
            db.session.add(feedback)

        # Update selected status on designs
        for design in Design.query.filter_by(request_id=design_request.id).all():
            design.is_selected = str(design.id) in selected_designs

        db.session.commit()

        flash('Thank you for your feedback!', 'success')
        return redirect(url_for('client.gallery', token=token))

    except Exception as e:
        db.session.rollback()
        print(f"Error submitting feedback: {e}")
        flash('An error occurred. Please try again.', 'error')
        return redirect(url_for('client.gallery', token=token))
