# Quick Start Guide - TezzaWorks Personalization Platform

Get up and running in 5 minutes!

## Prerequisites

- Python 3.8+ installed
- Terminal/Command line access

## Installation Steps

### 1. Navigate to Project Directory

```bash
cd /home/mtez/operation_help_maxwell/01_Business_TezzaWorks/tech_implementation/personalization_platform
```

### 2. Create Virtual Environment

```bash
python3 -m venv venv
```

### 3. Activate Virtual Environment

**Linux/Mac:**
```bash
source venv/bin/activate
```

**Windows:**
```bash
venv\Scripts\activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Run the Application

```bash
python app.py
```

## Access the Platform

Once running, open your browser:

### Client Interface
**URL**: http://localhost:5000/

This is where clients submit their design requests.

### Admin Dashboard
**URL**: http://localhost:5000/admin/dashboard

**Default Login:**
- Username: `admin`
- Password: `admin123`

## Quick Test Workflow

### Test as Client

1. Go to http://localhost:5000/
2. Fill out the form:
   - Company Name: Test Company
   - Contact Name: John Doe
   - Email: john@test.com
   - Brand Keywords: Innovation, Modern, Professional
3. Submit the form
4. **Save the gallery link** shown on the success page

### Test as Admin

1. Go to http://localhost:5000/admin/dashboard
2. Log in with default credentials
3. Click "View Details" on the test request
4. Update status to "In Progress"
5. Upload a design:
   - Add a title: "Modern Corporate Design"
   - Add description: "Clean and professional look"
   - Upload any image file (PNG/JPG)
6. Click "Generate PDF" to see the PDF presentation
7. Visit the client gallery link to see the client view

## Next Steps

1. **Change Admin Password** (Production)
2. **Customize Branding** - Update templates with your branding
3. **Set Up Email Notifications** - Add email service integration
4. **Deploy to Production** - See README.md for deployment options

## Common Commands

### Stop the Server
Press `Ctrl + C` in the terminal

### Restart the Server
```bash
python app.py
```

### View Database
```bash
sqlite3 tezzaworks.db
.tables
SELECT * FROM design_requests;
.quit
```

## Troubleshooting

### Port Already in Use
If port 5000 is in use, edit `app.py` and change the port:
```python
app.run(debug=True, host='0.0.0.0', port=5001)
```

### Module Not Found Error
Make sure virtual environment is activated:
```bash
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

Then reinstall dependencies:
```bash
pip install -r requirements.txt
```

## Support

For detailed documentation, see README.md

For issues, contact: info@tezzaworks.com
