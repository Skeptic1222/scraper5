# Complete Setup Guide

This guide provides detailed instructions for setting up the Enhanced Media Scraper application in various environments.

## Table of Contents
- [Quick Start](#quick-start)
- [Development Setup](#development-setup)
- [Production Setup](#production-setup)
- [IIS Deployment](#iis-deployment)
- [Google OAuth Configuration](#google-oauth-configuration)
- [Database Configuration](#database-configuration)
- [Troubleshooting](#troubleshooting)

## Quick Start

### Minimal Setup (5 minutes)
```bash
# 1. Clone repository
git clone https://github.com/yourusername/scraper.git
cd scraper

# 2. Install dependencies
pip install -r requirements.txt

# 3. Create .env file
echo "DATABASE_URL=sqlite:///instance/scraper.db" > .env
echo "SECRET_KEY=$(python -c 'import secrets; print(secrets.token_hex(32))')" >> .env
echo "GOOGLE_CLIENT_ID=your-client-id" >> .env
echo "GOOGLE_CLIENT_SECRET=your-secret" >> .env

# 4. Initialize database
python -c "from app import app, db; app.app_context().push(); db.create_all()"

# 5. Run application
python app.py
```

## Development Setup

### Prerequisites
- Python 3.8 or higher
- pip package manager
- Git

### Step-by-Step Setup

#### 1. Environment Preparation
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip
```

#### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

#### 3. Environment Variables
Create a `.env` file in the project root:

```env
# Application Settings
FLASK_ENV=development
DEBUG=true
SECRET_KEY=dev-secret-key-change-in-production

# Database (SQLite for development)
DATABASE_URL=sqlite:///instance/scraper.db

# Server Configuration
HOST=127.0.0.1
PORT=5000

# Google OAuth (get from Google Cloud Console)
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-client-secret
GOOGLE_REDIRECT_URL=/scraper/auth/google/callback

# Admin Configuration
ADMIN_EMAILS=admin@example.com,admin2@example.com

# Optional Settings
LOGIN_REQUIRED=false  # Set to true to require login
SESSION_COOKIE_SECURE=false  # Set to true for HTTPS
```

#### 4. Database Initialization
```bash
# Create database directory
mkdir -p instance

# Initialize database schema
python -c "
from app import app, db
with app.app_context():
    db.create_all()
    print('Database initialized successfully!')
"
```

#### 5. Run Development Server
```bash
python app.py
```

Access at: `http://localhost/scraper` (via IIS proxy; no ports in URLs)

## Production Setup

### Using Gunicorn (Linux/Mac)
```bash
# Install Gunicorn
pip install gunicorn

# Run with Gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 --timeout 120 app:app
```

### Using Waitress (Windows)
```bash
# Install Waitress
pip install waitress

# Run with Waitress
python -c "from waitress import serve; from app import app; serve(app, host='0.0.0.0', port=5000)"
```

### Production Environment Variables
```env
# Production settings
FLASK_ENV=production
DEBUG=false
SECRET_KEY=<generate-strong-secret-key>

# Database (SQL Server for production)
DATABASE_URL=mssql+pyodbc://username:password@server/database?driver=ODBC+Driver+17+for+SQL+Server

# Security
SESSION_COOKIE_SECURE=true
SESSION_COOKIE_HTTPONLY=true
SESSION_COOKIE_SAMESITE=Lax

# Performance
SQLALCHEMY_POOL_SIZE=10
SQLALCHEMY_POOL_RECYCLE=3600
```

## IIS Deployment

### Prerequisites
- Windows Server or Windows 10/11 Pro
- IIS with URL Rewrite Module
- Application Request Routing (ARR)
- Python 3.8+ installed

### IIS Configuration

#### 1. Install IIS Features
```powershell
# Run as Administrator
Enable-WindowsOptionalFeature -Online -FeatureName IIS-WebServerRole, IIS-WebServer, IIS-CommonHttpFeatures, IIS-HttpErrors, IIS-HttpRedirect, IIS-ApplicationDevelopment, IIS-HealthAndDiagnostics, IIS-HttpLogging, IIS-Security, IIS-RequestFiltering, IIS-Performance, IIS-WebServerManagementTools, IIS-ManagementConsole
```

#### 2. Install URL Rewrite and ARR
Download and install:
- [URL Rewrite Module](https://www.iis.net/downloads/microsoft/url-rewrite)
- [Application Request Routing](https://www.iis.net/downloads/microsoft/application-request-routing)

#### 3. Create web.config
```xml
<?xml version="1.0" encoding="UTF-8"?>
<configuration>
    <system.webServer>
        <rewrite>
            <rules>
                <rule name="ReverseProxyInboundRule" stopProcessing="true">
                    <match url="(.*)" />
                    <action type="Rewrite" url="http://localhost:5000/{R:1}" />
                </rule>
            </rules>
        </rewrite>
        <httpErrors errorMode="Detailed" />
        <directoryBrowse enabled="false" />
    </system.webServer>
</configuration>
```

#### 4. Create IIS Site
```powershell
# Create application pool
New-WebAppPool -Name "ScraperAppPool"

# Create website
New-Website -Name "Scraper" -Port 80 -PhysicalPath "C:\inetpub\wwwroot\scraper" -ApplicationPool "ScraperAppPool"
```

#### 5. Start Flask Backend
Create a Windows service or use Task Scheduler to run:
```batch
cd C:\inetpub\wwwroot\scraper
python app.py
```

## Google OAuth Configuration

### 1. Create Google Cloud Project
1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create new project or select existing
3. Enable Google+ API

### 2. Configure OAuth Consent Screen
1. Navigate to "APIs & Services" > "OAuth consent screen"
2. Choose "External" user type
3. Fill in application details:
   - App name: "Enhanced Media Scraper"
   - User support email: your-email@example.com
   - Developer contact: your-email@example.com
4. Add scopes:
   - `.../auth/userinfo.email`
   - `.../auth/userinfo.profile`
   - `openid`

### 3. Create OAuth Credentials
1. Navigate to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "OAuth client ID"
3. Choose "Web application"
4. Add authorized redirect URIs:
   - Development: `http://localhost/scraper/auth/google/callback`
   - Production: `https://yourdomain.com/scraper/auth/google/callback`
5. Save Client ID and Client Secret

### 4. Update .env File
```env
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-client-secret
GOOGLE_REDIRECT_URL=/scraper/auth/google/callback
```

## Database Configuration

### SQLite (Development)
```env
DATABASE_URL=sqlite:///instance/scraper.db
```

### PostgreSQL
```env
DATABASE_URL=postgresql://username:password@localhost:5432/scraper_db
```
Install driver:
```bash
pip install psycopg2-binary
```

### MySQL/MariaDB
```env
DATABASE_URL=mysql+pymysql://username:password@localhost:3306/scraper_db
```
Install driver:
```bash
pip install pymysql
```

### SQL Server
```env
DATABASE_URL=mssql+pyodbc://username:password@server/database?driver=ODBC+Driver+17+for+SQL+Server
```
Install driver:
```bash
pip install pyodbc
```

### Database Migration
```bash
# Create migration
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

## Troubleshooting

### Common Issues and Solutions

#### Port Already in Use
```bash
# Find process using port 5000
# Windows:
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# Linux/Mac:
lsof -i :5000
kill -9 <PID>
```

#### Database Connection Failed
1. Check DATABASE_URL format
2. Verify database server is running
3. Test connection:
```python
from sqlalchemy import create_engine
engine = create_engine('your-database-url')
engine.connect()
```

#### Google OAuth Not Working
1. Verify redirect URI matches exactly
2. Check client ID and secret
3. Ensure cookies are enabled
4. Try incognito/private browsing mode

#### Static Files Not Loading
1. Clear browser cache
2. Check static file paths
3. Verify Flask static folder configuration

#### Import Errors
```bash
# Reinstall all dependencies
pip install --force-reinstall -r requirements.txt
```

### Debug Mode
Enable detailed error messages:
```python
# In app.py, temporarily add:
app.config['PROPAGATE_EXCEPTIONS'] = True
app.config['EXPLAIN_TEMPLATE_LOADING'] = True
```

### Logging
Check application logs:
```bash
# View logs
tail -f logs/app.log

# Clear logs
rm logs/*.log
```

## Performance Optimization

### Database Optimization
```python
# Add to app.py
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_size': 10,
    'pool_recycle': 3600,
    'pool_pre_ping': True,
    'max_overflow': 20
}
```

### Caching
```bash
# Install Redis
pip install redis flask-caching

# Configure caching
CACHE_TYPE=redis
CACHE_REDIS_URL=redis://localhost:6379/0
```

### Production Checklist
- [ ] Change SECRET_KEY
- [ ] Set DEBUG=false
- [ ] Enable HTTPS
- [ ] Configure proper database
- [ ] Set up monitoring
- [ ] Configure backups
- [ ] Review security settings
- [ ] Test all features
- [ ] Set up error tracking
- [ ] Configure rate limiting

## Support

For issues or questions:
1. Check the [README](README.md)
2. Review this setup guide
3. Check application logs
4. Create an issue on GitHub

---

**Last Updated**: 2025-09-09
**Version**: 3.0.0
