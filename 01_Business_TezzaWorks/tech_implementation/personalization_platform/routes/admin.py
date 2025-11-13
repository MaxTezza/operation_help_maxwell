"""
Admin routes for managing design requests and uploads
"""
import os
import json
from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file, session
from werkzeug.utils import secure_filename
from werkzeug.security import check_password_hash
from models import db, DesignRequest, Design, ClientFeedback, AdminUser
from database import get_all_requests, update_request_status
from utils.pdf_generator import generate_design_pdf

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf'}
UPLOAD_FOLDER = 'static/uploads'


def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def login_required(f):
    """Decorator to require admin login"""
    from functools import wraps

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_logged_in'):
            return redirect(url_for('admin.login'))
        return f(*args, **kwargs)

    return decorated_function


@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Admin login page"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        admin = AdminUser.query.filter_by(username=username).first()

        if admin and check_password_hash(admin.password_hash, password):
            session['admin_logged_in'] = True
            session['admin_username'] = username
            flash('Login successful!', 'success')
            return redirect(url_for('admin.dashboard'))
        else:
            flash('Invalid credentials', 'error')

    return render_template('admin_login.html')


@admin_bp.route('/logout')
def logout():
    """Admin logout"""
    session.pop('admin_logged_in', None)
    session.pop('admin_username', None)
    flash('Logged out successfully', 'success')
    return redirect(url_for('admin.login'))


@admin_bp.route('/dashboard')
@login_required
def dashboard():
    """Admin dashboard showing all design requests"""
    requests = get_all_requests()

    # Categorize requests by status
    pending_requests = [r for r in requests if r.status == 'pending']
    in_progress_requests = [r for r in requests if r.status == 'in_progress']
    completed_requests = [r for r in requests if r.status == 'completed']

    return render_template('admin_dashboard.html',
                           pending_requests=pending_requests,
                           in_progress_requests=in_progress_requests,
                           completed_requests=completed_requests)


@admin_bp.route('/request/<int:request_id>')
@login_required
def view_request(request_id):
    """View detailed information about a specific request"""
    design_request = DesignRequest.query.get_or_404(request_id)
    designs = Design.query.filter_by(request_id=request_id).order_by(Design.display_order).all()
    feedback = ClientFeedback.query.filter_by(request_id=request_id).first()

    return render_template('admin_request_detail.html',
                           request=design_request,
                           designs=designs,
                           feedback=feedback)


@admin_bp.route('/request/<int:request_id>/update_status', methods=['POST'])
@login_required
def update_status(request_id):
    """Update the status of a design request"""
    new_status = request.form.get('status')

    if new_status in ['pending', 'in_progress', 'completed']:
        update_request_status(request_id, new_status)
        flash(f'Status updated to {new_status}', 'success')
    else:
        flash('Invalid status', 'error')

    return redirect(url_for('admin.view_request', request_id=request_id))


@admin_bp.route('/request/<int:request_id>/upload_design', methods=['POST'])
@login_required
def upload_design(request_id):
    """Upload a design option for a request"""
    design_request = DesignRequest.query.get_or_404(request_id)

    try:
        # Check if file was uploaded
        if 'design_file' not in request.files:
            flash('No file uploaded', 'error')
            return redirect(url_for('admin.view_request', request_id=request_id))

        file = request.files['design_file']

        if file.filename == '':
            flash('No file selected', 'error')
            return redirect(url_for('admin.view_request', request_id=request_id))

        if file and allowed_file(file.filename):
            # Save file
            filename = secure_filename(file.filename)
            import time
            timestamp = str(int(time.time()))
            unique_filename = f"design_{request_id}_{timestamp}_{filename}"
            filepath = os.path.join(UPLOAD_FOLDER, unique_filename)
            os.makedirs(UPLOAD_FOLDER, exist_ok=True)
            file.save(filepath)

            # Get design details
            title = request.form.get('design_title', '')
            description = request.form.get('design_description', '')

            # Get current max display order
            max_order = db.session.query(db.func.max(Design.display_order)).filter_by(
                request_id=request_id).scalar() or 0

            # Create design record
            design = Design(
                request_id=request_id,
                filename=unique_filename,
                title=title,
                description=description,
                display_order=max_order + 1
            )

            db.session.add(design)
            db.session.commit()

            flash('Design uploaded successfully!', 'success')
        else:
            flash('Invalid file type. Allowed types: png, jpg, jpeg, pdf', 'error')

    except Exception as e:
        db.session.rollback()
        print(f"Error uploading design: {e}")
        flash('An error occurred while uploading the design.', 'error')

    return redirect(url_for('admin.view_request', request_id=request_id))


@admin_bp.route('/request/<int:request_id>/delete_design/<int:design_id>', methods=['POST'])
@login_required
def delete_design(request_id, design_id):
    """Delete a design option"""
    design = Design.query.get_or_404(design_id)

    try:
        # Delete file from filesystem
        filepath = os.path.join(UPLOAD_FOLDER, design.filename)
        if os.path.exists(filepath):
            os.remove(filepath)

        # Delete database record
        db.session.delete(design)
        db.session.commit()

        flash('Design deleted successfully', 'success')
    except Exception as e:
        db.session.rollback()
        print(f"Error deleting design: {e}")
        flash('An error occurred while deleting the design.', 'error')

    return redirect(url_for('admin.view_request', request_id=request_id))


@admin_bp.route('/request/<int:request_id>/generate_pdf')
@login_required
def generate_pdf(request_id):
    """Generate and download PDF presentation"""
    design_request = DesignRequest.query.get_or_404(request_id)
    designs = Design.query.filter_by(request_id=request_id).order_by(Design.display_order).all()

    if not designs:
        flash('No designs to include in PDF. Please upload designs first.', 'error')
        return redirect(url_for('admin.view_request', request_id=request_id))

    try:
        # Generate PDF
        pdf_path = generate_design_pdf(design_request, designs)

        # Send file for download
        return send_file(
            pdf_path,
            as_attachment=True,
            download_name=f"TezzaWorks_Presentation_{design_request.company_name}.pdf"
        )

    except Exception as e:
        print(f"Error generating PDF: {e}")
        flash('An error occurred while generating the PDF.', 'error')
        return redirect(url_for('admin.view_request', request_id=request_id))


@admin_bp.route('/request/<int:request_id>/update_design/<int:design_id>', methods=['POST'])
@login_required
def update_design(request_id, design_id):
    """Update design title and description"""
    design = Design.query.get_or_404(design_id)

    try:
        design.title = request.form.get('design_title', '')
        design.description = request.form.get('design_description', '')
        db.session.commit()

        flash('Design updated successfully', 'success')
    except Exception as e:
        db.session.rollback()
        print(f"Error updating design: {e}")
        flash('An error occurred while updating the design.', 'error')

    return redirect(url_for('admin.view_request', request_id=request_id))
