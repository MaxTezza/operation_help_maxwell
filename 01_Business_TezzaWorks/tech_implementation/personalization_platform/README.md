# TezzaWorks Customer Personalization Platform - Phase 1 MVP

A "Wizard of Oz" web application for collecting client brand information and manually curating AI-generated designs. This platform enables TezzaWorks to showcase custom design options to clients through personalized galleries and generate professional PDF presentations.

## Table of Contents

1. [Features](#features)
2. [Technology Stack](#technology-stack)
3. [Project Structure](#project-structure)
4. [Installation](#installation)
5. [Configuration](#configuration)
6. [Running the Application](#running-the-application)
7. [Admin Workflow](#admin-workflow)
8. [Client Workflow](#client-workflow)
9. [Database Schema](#database-schema)
10. [Deployment](#deployment)
11. [Troubleshooting](#troubleshooting)

## Features

### Client-Facing Features
- Clean, professional form for brand information submission
- Optional logo upload
- Unique personalized gallery link for each request
- Design viewing with zoom functionality
- Design selection and feedback system
- Star rating system

### Admin Features
- Secure admin login
- Dashboard with request status tracking (Pending, In Progress, Completed)
- Detailed view of each design request
- Multi-design upload capability
- Design management (edit descriptions, delete)
- Professional PDF generation with TezzaWorks branding
- Status tracking and updates
- Direct access to client galleries

## Technology Stack

- **Backend**: Flask 3.0.0 (Python web framework)
- **Database**: SQLite (with Flask-SQLAlchemy ORM)
- **Frontend**: HTML5, Tailwind CSS, Font Awesome icons
- **PDF Generation**: ReportLab
- **Image Processing**: Pillow
- **Security**: Werkzeug password hashing

## Project Structure

```
personalization_platform/
├── app.py                          # Main Flask application
├── models.py                       # Database models
├── database.py                     # Database utilities
├── requirements.txt                # Python dependencies
├── README.md                       # This file
│
├── routes/
│   ├── __init__.py
│   ├── client.py                   # Client-facing routes
│   └── admin.py                    # Admin routes
│
├── templates/
│   ├── base.html                   # Base template
│   ├── client_form.html            # Client submission form
│   ├── submission_success.html     # Thank you page
│   ├── gallery.html                # Client design gallery
│   ├── admin_login.html            # Admin login page
│   ├── admin_dashboard.html        # Admin dashboard
│   ├── admin_request_detail.html   # Request detail page
│   └── error.html                  # Error page
│
├── static/
│   ├── css/                        # Custom CSS (if needed)
│   ├── js/                         # Custom JavaScript (if needed)
│   ├── uploads/                    # Uploaded files (logos, designs)
│   └── pdfs/                       # Generated PDFs
│
└── utils/
    ├── __init__.py
    └── pdf_generator.py            # PDF generation utility
```

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Virtual environment (recommended)

### Step 1: Clone or Navigate to Project Directory

```bash
cd /home/mtez/operation_help_maxwell/01_Business_TezzaWorks/tech_implementation/personalization_platform
```

### Step 2: Create Virtual Environment

```bash
python3 -m venv venv
```

### Step 3: Activate Virtual Environment

**Linux/Mac:**
```bash
source venv/bin/activate
```

**Windows:**
```bash
venv\Scripts\activate
```

### Step 4: Install Dependencies

```bash
pip install -r requirements.txt
```

## Configuration

### Environment Variables

For production, set these environment variables:

```bash
export SECRET_KEY="your-secret-key-here"
```

For development, the app will use default values.

### Default Admin Credentials

On first run, the application creates a default admin user:

- **Username**: `admin`
- **Password**: `admin123`

**IMPORTANT**: Change these credentials immediately in production!

## Running the Application

### Development Server

```bash
python app.py
```

The application will be available at:
- **Client Form**: http://localhost:5000/
- **Admin Dashboard**: http://localhost:5000/admin/dashboard

### Production Server

For production, use a production-grade WSGI server like Gunicorn:

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## Admin Workflow

### 1. Log In

Navigate to `/admin/dashboard` and log in with admin credentials.

### 2. Review Pending Requests

The dashboard shows all requests categorized by status:
- **Pending**: New requests waiting for designs
- **In Progress**: Requests being worked on
- **Completed**: Finished requests with client feedback

### 3. Process a Design Request

1. Click "View Details" on any request
2. Review the client's brand information, keywords, and uploaded logo
3. Update status to "In Progress"

### 4. Create Designs Manually

Use external tools (Midjourney, DALL-E, Canva, etc.) to create 3-4 design options based on the client's brand profile.

### 5. Upload Design Options

1. In the request detail page, use the upload form
2. Add a title and description for each design
3. Upload the design file (PNG, JPG, or PDF)
4. Repeat for all design options (recommended: 3-4 designs)

### 6. Generate PDF Presentation

Once designs are uploaded:
1. Click "Generate PDF" button
2. A professional PDF will be created with:
   - TezzaWorks branding
   - Client company name
   - Brand profile
   - All design options with descriptions
   - Next steps information

### 7. Notify Client

1. Copy the gallery link from the sidebar
2. Send an email to the client with:
   - Notification that designs are ready
   - Link to their personalized gallery
   - PDF attachment (optional)
3. Update status to "Completed"

### 8. Review Client Feedback

When clients submit feedback:
- View their selected designs (marked with hearts)
- See their star rating
- Read their comments
- Use this information for refinement

## Client Workflow

### 1. Submit Design Request

1. Visit the homepage
2. Fill out the form with:
   - Company information
   - Brand keywords and values
   - Brand colors (optional)
   - Target audience (optional)
   - Logo upload (optional)
   - Additional notes (optional)
3. Submit the request

### 2. Receive Gallery Link

After submission:
- Get a unique gallery link
- Bookmark this link for future access
- Wait for email notification when designs are ready

### 3. View Design Options

When notified:
1. Visit the gallery link
2. Review brand profile summary
3. View all design options
4. Click images to zoom/expand

### 4. Provide Feedback

1. Select favorite designs using checkboxes
2. Rate overall satisfaction (1-5 stars)
3. Add comments or suggestions
4. Submit feedback

## Database Schema

### Tables

**design_requests**
- Stores client information and brand details
- Tracks request status
- Contains unique gallery token

**designs**
- Stores uploaded design files
- Links to parent request
- Tracks client selections

**client_feedback**
- Stores client ratings and comments
- Links selected designs to requests

**admin_users**
- Stores admin credentials (hashed passwords)

## Deployment

### Option 1: Heroku

1. Create a `Procfile`:
```
web: gunicorn app:app
```

2. Deploy:
```bash
heroku create tezzaworks-platform
git push heroku main
```

### Option 2: Railway

1. Connect your GitHub repository
2. Railway will auto-detect Flask
3. Set environment variables in Railway dashboard

### Option 3: VPS (DigitalOcean, AWS, etc.)

1. Set up a Linux server
2. Install Python and dependencies
3. Use Nginx as reverse proxy
4. Use Gunicorn as WSGI server
5. Set up SSL with Let's Encrypt

## Security Considerations

### For Production:

1. **Change Default Admin Password**
   - Log in and create a new admin user
   - Delete the default admin

2. **Set Strong SECRET_KEY**
   ```bash
   export SECRET_KEY=$(python -c 'import secrets; print(secrets.token_hex(32))')
   ```

3. **Enable HTTPS**
   - Use SSL certificate (Let's Encrypt)
   - Force HTTPS redirects

4. **Database Backups**
   - Regular backups of SQLite database
   - Or migrate to PostgreSQL for production

5. **File Upload Security**
   - Already implemented: file type validation
   - Already implemented: secure filename generation
   - Consider: virus scanning for uploaded files

## Troubleshooting

### Issue: Database not found

**Solution**: Run the app once to create the database automatically.

```bash
python app.py
```

### Issue: Permission denied for uploads folder

**Solution**: Ensure proper permissions:

```bash
chmod 755 static/uploads
chmod 755 static/pdfs
```

### Issue: PDF generation fails

**Solution**: Check that uploaded images exist and are valid formats.

### Issue: Can't log in to admin

**Solution**: Check if admin user exists in database. If not, run:

```python
python -c "from app import create_app; from database import create_admin_user; app = create_app(); app.app_context().push(); create_admin_user('admin', 'admin123', 'admin@tezzaworks.com')"
```

## API Endpoints

### Client Routes
- `GET /` - Client submission form
- `POST /submit` - Submit design request
- `GET /gallery/<token>` - View client gallery
- `POST /gallery/<token>/feedback` - Submit feedback

### Admin Routes
- `GET /admin/login` - Admin login page
- `POST /admin/login` - Process login
- `GET /admin/logout` - Logout
- `GET /admin/dashboard` - Admin dashboard
- `GET /admin/request/<id>` - View request details
- `POST /admin/request/<id>/update_status` - Update status
- `POST /admin/request/<id>/upload_design` - Upload design
- `POST /admin/request/<id>/delete_design/<design_id>` - Delete design
- `GET /admin/request/<id>/generate_pdf` - Generate PDF

## Future Enhancements

### Phase 2 Considerations
- Email notifications (SendGrid/Mailgun integration)
- User authentication for clients
- Multiple admin users with roles
- Design commenting system
- Automated AI design generation
- Analytics dashboard
- Payment integration
- Template library

## Support

For questions or issues:
- **Email**: info@tezzaworks.com
- **Phone**: (555) 123-4567

## License

Copyright 2024 TezzaWorks. All rights reserved.

---

**Built with Flask for TezzaWorks by Maxwell**
