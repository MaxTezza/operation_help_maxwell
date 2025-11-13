# Deployment Guide - TezzaWorks Personalization Platform

This guide covers deploying the platform to production environments.

## Table of Contents

1. [Pre-Deployment Checklist](#pre-deployment-checklist)
2. [Heroku Deployment](#heroku-deployment)
3. [Railway Deployment](#railway-deployment)
4. [DigitalOcean/VPS Deployment](#digitalocean-vps-deployment)
5. [Post-Deployment Steps](#post-deployment-steps)

---

## Pre-Deployment Checklist

Before deploying, ensure you complete these steps:

### 1. Security Configuration

#### Generate a Strong Secret Key
```bash
python -c 'import secrets; print(secrets.token_hex(32))'
```
Save this output - you'll use it as your SECRET_KEY environment variable.

#### Change Default Admin Credentials
After first deployment, immediately:
1. Log in with default credentials (admin/admin123)
2. Create a new admin user with a strong password
3. Delete the default admin account

### 2. Environment Variables

Prepare these environment variables for your production environment:

```
SECRET_KEY=<your-generated-secret-key>
FLASK_ENV=production
FLASK_DEBUG=0
```

### 3. Code Review

- [ ] Remove any debug print statements
- [ ] Verify all file upload validations are in place
- [ ] Check database models are finalized
- [ ] Test PDF generation locally

---

## Heroku Deployment

### Step 1: Install Heroku CLI

```bash
# Mac
brew tap heroku/brew && brew install heroku

# Ubuntu/Debian
curl https://cli-assets.heroku.com/install.sh | sh

# Windows
# Download installer from https://devcenter.heroku.com/articles/heroku-cli
```

### Step 2: Create Heroku App

```bash
cd /home/mtez/operation_help_maxwell/01_Business_TezzaWorks/tech_implementation/personalization_platform

heroku login
heroku create tezzaworks-platform
```

### Step 3: Create Required Files

#### Procfile
Create a file named `Procfile` (no extension):

```
web: gunicorn app:app
```

#### runtime.txt
Create a file specifying Python version:

```
python-3.11.0
```

### Step 4: Add Gunicorn to Requirements

```bash
echo "gunicorn==21.2.0" >> requirements.txt
```

### Step 5: Set Environment Variables

```bash
heroku config:set SECRET_KEY="your-secret-key-here"
heroku config:set FLASK_ENV=production
heroku config:set FLASK_DEBUG=0
```

### Step 6: Initialize Git (if not already done)

```bash
git init
git add .
git commit -m "Initial commit for TezzaWorks platform"
```

### Step 7: Deploy

```bash
git push heroku main
# or if you're on master branch:
git push heroku master
```

### Step 8: Open Your App

```bash
heroku open
```

### Heroku Database Considerations

For production, consider upgrading to PostgreSQL:

```bash
heroku addons:create heroku-postgresql:mini
```

Then update your `app.py` to use the database URL from environment:

```python
import os
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///tezzaworks.db')
```

---

## Railway Deployment

Railway offers easy deployment with automatic HTTPS.

### Step 1: Create Railway Account

Visit https://railway.app and sign up (can use GitHub).

### Step 2: Install Railway CLI

```bash
npm install -g @railway/cli
# or
brew install railway
```

### Step 3: Login and Initialize

```bash
cd /home/mtez/operation_help_maxwell/01_Business_TezzaWorks/tech_implementation/personalization_platform

railway login
railway init
```

### Step 4: Configure Environment

In Railway dashboard:
1. Go to your project
2. Click "Variables"
3. Add:
   - `SECRET_KEY`: your-secret-key
   - `FLASK_ENV`: production
   - `FLASK_DEBUG`: 0

### Step 5: Deploy

```bash
railway up
```

Railway will automatically:
- Detect it's a Flask app
- Install dependencies
- Generate a public URL with HTTPS

### Step 6: View Deployment

```bash
railway open
```

---

## DigitalOcean/VPS Deployment

For more control, deploy on a VPS with Nginx + Gunicorn.

### Step 1: Create Droplet

1. Create a Ubuntu 22.04 droplet on DigitalOcean
2. SSH into your server:
```bash
ssh root@your-server-ip
```

### Step 2: Install Dependencies

```bash
# Update system
apt update && apt upgrade -y

# Install Python and essentials
apt install python3 python3-pip python3-venv nginx supervisor -y
```

### Step 3: Create Application User

```bash
adduser tezzaworks
usermod -aG sudo tezzaworks
su - tezzaworks
```

### Step 4: Clone/Upload Application

```bash
cd /home/tezzaworks
# Upload your files via SCP or git clone
```

### Step 5: Set Up Virtual Environment

```bash
cd personalization_platform
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install gunicorn
```

### Step 6: Create Gunicorn Service

Create `/etc/supervisor/conf.d/tezzaworks.conf`:

```ini
[program:tezzaworks]
directory=/home/tezzaworks/personalization_platform
command=/home/tezzaworks/personalization_platform/venv/bin/gunicorn -w 4 -b 127.0.0.1:8000 app:app
user=tezzaworks
autostart=true
autorestart=true
stopasgroup=true
killasgroup=true
stderr_logfile=/var/log/tezzaworks/err.log
stdout_logfile=/var/log/tezzaworks/out.log
```

Create log directory:
```bash
mkdir -p /var/log/tezzaworks
chown -R tezzaworks:tezzaworks /var/log/tezzaworks
```

Start the service:
```bash
supervisorctl reread
supervisorctl update
supervisorctl start tezzaworks
```

### Step 7: Configure Nginx

Create `/etc/nginx/sites-available/tezzaworks`:

```nginx
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # File upload size
        client_max_body_size 16M;
    }

    location /static {
        alias /home/tezzaworks/personalization_platform/static;
        expires 30d;
    }
}
```

Enable the site:
```bash
ln -s /etc/nginx/sites-available/tezzaworks /etc/nginx/sites-enabled/
nginx -t
systemctl restart nginx
```

### Step 8: Set Up SSL with Let's Encrypt

```bash
apt install certbot python3-certbot-nginx -y
certbot --nginx -d your-domain.com -d www.your-domain.com
```

Follow the prompts. Certbot will automatically configure HTTPS.

### Step 9: Set Up Firewall

```bash
ufw allow 22/tcp   # SSH
ufw allow 80/tcp   # HTTP
ufw allow 443/tcp  # HTTPS
ufw enable
```

---

## Post-Deployment Steps

### 1. Verify Application is Running

Visit your deployed URL and test:
- [ ] Client form loads correctly
- [ ] Form submission works
- [ ] Gallery pages are accessible
- [ ] Admin login works
- [ ] File uploads work
- [ ] PDF generation works

### 2. Change Default Admin Password

1. Log in to admin dashboard
2. Create new admin user with strong password
3. Consider removing default admin

### 3. Set Up Database Backups

#### For SQLite (VPS):
```bash
# Add to crontab
crontab -e

# Add this line for daily backups at 2 AM:
0 2 * * * cp /home/tezzaworks/personalization_platform/tezzaworks.db /home/tezzaworks/backups/tezzaworks-$(date +\%Y\%m\%d).db
```

#### For PostgreSQL (Heroku/Railway):
Use the platform's built-in backup features.

### 4. Set Up Monitoring

#### Basic Uptime Monitoring
- Use UptimeRobot (free tier: https://uptimerobot.com)
- Monitor your main URL every 5 minutes

#### Application Monitoring
Consider adding:
- Sentry for error tracking
- Google Analytics for usage
- Server monitoring (if VPS)

### 5. Configure Email Notifications (Optional)

For email integration, add to your code:

```python
# Install: pip install Flask-Mail
from flask_mail import Mail, Message

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')

mail = Mail(app)
```

### 6. Set Up Regular Maintenance

Create a maintenance checklist:
- [ ] Weekly: Review new design requests
- [ ] Weekly: Check disk space (if VPS)
- [ ] Monthly: Review and delete old completed requests
- [ ] Monthly: Database backup verification
- [ ] Quarterly: Update dependencies

---

## Rollback Procedure

If something goes wrong:

### Heroku
```bash
heroku releases
heroku rollback v<previous-version-number>
```

### Railway
Use the Railway dashboard to rollback to a previous deployment.

### VPS
```bash
# Restore database backup
cp /home/tezzaworks/backups/tezzaworks-YYYYMMDD.db /home/tezzaworks/personalization_platform/tezzaworks.db

# Restart services
supervisorctl restart tezzaworks
```

---

## Troubleshooting

### Application Won't Start

1. Check logs:
   - Heroku: `heroku logs --tail`
   - Railway: View in dashboard
   - VPS: `tail -f /var/log/tezzaworks/err.log`

2. Verify environment variables are set
3. Check database permissions

### File Uploads Fail

1. Verify upload directory exists and has correct permissions
2. Check `MAX_CONTENT_LENGTH` setting
3. Verify Nginx `client_max_body_size` (if using Nginx)

### PDF Generation Fails

1. Check that ReportLab is installed
2. Verify uploaded images are valid
3. Check write permissions on `static/pdfs` directory

---

## Performance Optimization

### For High Traffic

1. **Use PostgreSQL** instead of SQLite
2. **Add Redis** for session storage
3. **Use CDN** for static files (CloudFlare, AWS CloudFront)
4. **Increase Gunicorn workers**: `-w 8` or `2 * num_cores + 1`
5. **Add caching** with Flask-Caching

### Database Optimization

If using PostgreSQL, add indexes:
```sql
CREATE INDEX idx_gallery_token ON design_requests(gallery_token);
CREATE INDEX idx_request_status ON design_requests(status);
CREATE INDEX idx_request_created ON design_requests(created_at);
```

---

## Support

For deployment issues:
- Check logs first
- Review this guide
- Contact: info@tezzaworks.com

**Remember**: Always test deployments in a staging environment first!
