# Security Guidelines for TezzaWorks Applications

## Before Deploying to Production

### Critical Security Checklist

#### 1. Change Default Passwords
- [ ] Personalization Platform admin password (currently: admin/admin123)
- [ ] Update in: `personalization_platform/database.py`

#### 2. Generate New Secret Keys
```bash
# Generate a new secret key
python3 -c "import secrets; print(secrets.token_hex(32))"
```

Update in `.env` files:
- `operations_dashboard/backend/.env`
- `personalization_platform/.env`

#### 3. Set Production Environment
In all `.env` files:
```
FLASK_ENV=production
FLASK_DEBUG=0
```

#### 4. Update CORS Origins
In `operations_dashboard/backend/.env`:
```
CORS_ORIGINS=https://maxdexstudio.com,https://ops.maxdexstudio.com
```

#### 5. Database Migration
- Switch from SQLite to PostgreSQL for production
- Set `DATABASE_URL` in `.env`

#### 6. Enable HTTPS
- Set up SSL certificates (Let's Encrypt)
- Configure nginx to redirect HTTP → HTTPS
- Enable HSTS headers (already in code when FLASK_ENV=production)

---

## Security Features Implemented

### ✅ CORS Protection
- Configurable allowed origins via environment variable
- Restricted methods and headers
- No wildcard origins in production

### ✅ Security Headers
- `X-Content-Type-Options: nosniff` - Prevents MIME sniffing
- `X-Frame-Options: DENY` - Prevents clickjacking
- `X-XSS-Protection: 1; mode=block` - XSS protection
- `Strict-Transport-Security` - HTTPS enforcement (production only)

### ✅ SQL Injection Protection
- SQLAlchemy ORM used throughout
- No raw SQL queries in application code
- Parameterized queries only

### ✅ XSS Protection
- Flask auto-escapes templates
- No `dangerouslySetInnerHTML` in React code
- Security headers enabled

### ✅ Input Validation
- File upload size limits (16MB)
- Email validation on client forms
- Type checking via SQLAlchemy models

---

## Still TODO

### High Priority
- [ ] Add rate limiting (flask-limiter)
- [ ] Add request logging
- [ ] Add error monitoring (Sentry)
- [ ] File upload validation (check file types, scan for malware)
- [ ] Add API authentication for sensitive endpoints

### Medium Priority
- [ ] Add CSRF protection for forms
- [ ] Implement proper session management
- [ ] Add password complexity requirements
- [ ] Add account lockout after failed login attempts
- [ ] Set up automated security scanning (Dependabot, Snyk)

### Nice to Have
- [ ] Add Content Security Policy (CSP)
- [ ] Implement API versioning
- [ ] Add audit logging
- [ ] Set up intrusion detection
- [ ] Regular security penetration testing

---

## Production Deployment Security

### Environment Variables
Never commit `.env` files! Always use:
- Environment variables on server
- Secret management service (AWS Secrets Manager, etc.)
- Encrypted config files

### Database
- Use PostgreSQL in production (not SQLite)
- Enable SSL for database connections
- Regular backups with encryption
- Principle of least privilege for DB user

### Server Hardening
- Keep all packages updated
- Disable unnecessary services
- Use firewall (ufw, iptables)
- SSH key authentication only
- Fail2ban for brute force protection

### Monitoring
- Log all security events
- Monitor for suspicious activity
- Set up alerts for:
  - Failed login attempts
  - Unusual traffic patterns
  - Error spikes
  - Database errors

---

## Incident Response

If you suspect a security breach:

1. **Immediately**: Rotate all secrets and API keys
2. **Isolate**: Take affected systems offline
3. **Investigate**: Review logs for unauthorized access
4. **Notify**: Alert affected users if data was compromised
5. **Patch**: Fix the vulnerability
6. **Document**: Record timeline and actions taken

---

## Security Contacts

- Report vulnerabilities: security@maxdexstudio.com (update this!)
- PGP Key: (add if you set one up)

---

**Last Updated**: November 13, 2025
**Next Security Review**: Before production deployment
