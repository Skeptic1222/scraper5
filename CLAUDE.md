# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## CRITICAL RULES

### ⚠️ NEVER ADD PORTS TO URLS ⚠️
- **NEVER**: `http://localhost:5050/scraper` or any `:port` in URLs
- **ALWAYS**: `http://localhost/scraper` (no port!)
- **WHY**: IIS reverse proxy handles routing; browser must never see Flask port 5050
- **API CALLS**: Always use `/scraper/api/...` prefix
- **ENFORCEMENT**: See `CRITICAL_NO_PORTS_RULE.md` for complete details

## Project Overview

**Enhanced Media Scraper v3.0** - A Flask web application for content aggregation from 118+ sources with:
- **Backend**: Flask + SQLAlchemy + Google OAuth
- **Database**: SQL Server Express (production) / SQLite (development)
- **Web Server**: IIS with reverse proxy + FastCGI
- **Platform**: Windows Server/Windows 10/11 Pro
- **Access URL**: `http://localhost/scraper` (via IIS, no ports!)

## Architecture

### Request Flow
```
Browser → IIS (port 80) → Reverse Proxy → Flask (port 5050/8080)
         ↓
    SQL Server Express
```

### Key Components
- **app.py**: Main Flask application (1000+ lines, comprehensive routing)
- **auth.py**: Google OAuth implementation with role-based access
- **models.py**: SQLAlchemy models (User, Asset, ScrapeJob, Role)
- **scrapers/**: 118+ scraper modules for different sources
- **static/js/fixes/**: Critical JavaScript fixes for API routing
- **templates/**: Jinja2 templates with base.html as master layout

## Common Commands

### Development (WSL)
```bash
# Start server (from WSL)
cd /mnt/c/inetpub/wwwroot/scraper/scraper4
python3 app.py

# Check if running
ps aux | grep python

# Kill all instances
pkill -f python

# View logs
tail -f logs/app.log
```

### Database Management
```bash
# Initialize SQLite (development)
python3 init_db.py

# Create SQL Server database (production)
python3 create_database.py
```

### Windows Administration (via MCP servers)
```bash
# Manage IIS
mcp__windows-command__manage_iis action="status"
mcp__windows-command__manage_iis action="restart"

# SQL Server operations
mcp__windows-command__manage_sql_server action="status"
mcp__windows-command__manage_sql_server action="execute-query" database="Scraped" query="SELECT COUNT(*) FROM users"
```

## Deployment Process

### Prerequisites Check
1. **IIS Features**: URL Rewrite, ARR, FastCGI
2. **SQL Server Express**: Instance at `localhost\SQLEXPRESS`
3. **Python 3.8+**: With pip and virtualenv
4. **ODBC Driver 17/18**: For SQL Server connectivity

### Step-by-Step Deployment

#### 1. Database Setup
```sql
-- Run setup_sql_server.sql in SSMS
-- Creates database 'Scraped' with user 'dbuser'
-- Password: Qwerty1234!
```

#### 2. Environment Configuration
Create `.env` file:
```env
# Core settings
FLASK_ENV=production
SECRET_KEY=<generate-strong-key>
DATABASE_URL=mssql+pyodbc://dbuser:Qwerty1234!@localhost\SQLEXPRESS/Scraped?driver=ODBC+Driver+17+for+SQL+Server

# Google OAuth
GOOGLE_CLIENT_ID=<your-client-id>
GOOGLE_CLIENT_SECRET=<your-secret>
GOOGLE_REDIRECT_URL=/scraper/auth/google/callback

# Admin
ADMIN_EMAIL=sop1973@gmail.com
```

#### 3. IIS Configuration
- **Site**: Create at `/scraper` path
- **Handler**: FastCGI or Reverse Proxy to port 5050/8080
- **web.config**: Already configured for reverse proxy
- **Static files**: Handled by Flask (not ideal but working)

#### 4. Install Dependencies
```bash
pip install -r requirements.txt
pip install -r requirements-windows.txt  # Windows-specific
```

#### 5. Initialize Database
```bash
python3 create_database.py  # For SQL Server
# OR
python3 init_db.py         # For SQLite
```

#### 6. Start Application
```bash
# Development
python3 app.py

# Production (via service or scheduled task)
python3 deployment/windows/enhanced_media_scraper_service.py
```

## Database Schema

### Core Tables
- **users**: Authentication, subscription, credits
- **assets**: Downloaded media metadata
- **scrape_jobs**: Job tracking with progress
- **roles**: RBAC roles (admin, user, premium)
- **user_roles**: Many-to-many user-role mapping
- **sources**: Available scraper sources

### Key Relationships
- User → many Assets (one-to-many)
- User → many ScrapeJobs (one-to-many)
- User ↔ Roles (many-to-many via user_roles)

## Authentication Flow

1. User clicks "Sign in with Google"
2. Redirect to Google OAuth
3. Callback to `/scraper/auth/google/callback`
4. Create/update user in database
5. Set Flask session
6. Admin check: `email == ADMIN_EMAIL` → full access

## API Endpoints

### Public
- `GET /scraper` - Main application
- `GET /scraper/login` - Login page
- `GET /scraper/auth/google` - OAuth initiation

### Authenticated
- `GET /scraper/api/sources` - List available sources
- `POST /scraper/api/comprehensive-search` - Start scraping job
- `GET /scraper/api/job-status/<job_id>` - Check job progress
- `GET /scraper/api/assets` - List user's assets
- `DELETE /scraper/api/assets/<id>` - Delete asset

### Admin Only
- `GET /scraper/admin` - Admin dashboard
- `POST /scraper/admin/users/<id>/credits` - Manage credits
- `GET /scraper/admin/system/logs` - View system logs

## Known Issues & Solutions

### "Sources Not Loading"
- Click "Fix Sources NOW" button (bottom right)
- Or restart Flask server

### OAuth Redirect Issues
- Ensure `GOOGLE_REDIRECT_URL=/scraper/auth/google/callback`
- Clear browser cookies
- Use incognito mode for testing

### Database Connection Failed
- Check SQL Server service is running
- Verify connection string in `.env`
- Test with `sqlcmd -S .\SQLEXPRESS -E`

### IIS 500 Errors
- Check `C:\inetpub\logs\LogFiles\`
- Verify Flask is running on correct port
- Check web.config proxy rules

## File Structure Highlights

```
scraper4/
├── app.py                 # Main application (1000+ lines)
├── auth.py                # OAuth implementation (450+ lines)
├── models.py              # Database models (600+ lines)
├── web.config             # IIS configuration (CRITICAL)
├── .env                   # Environment variables (create from .env.example)
├── requirements.txt       # Python dependencies
├── deployment/
│   └── windows/          # Windows-specific deployment scripts
├── static/
│   └── js/
│       └── fixes/        # Critical JavaScript fixes (NO PORTS!)
└── templates/
    └── base.html         # Master template (window.APP_BASE = '/scraper')
```

## Testing Checklist

Before deployment:
- [ ] Test login: `http://localhost/scraper`
- [ ] Verify no ports in any URLs
- [ ] Check database connectivity
- [ ] Test source loading
- [ ] Verify admin access (sop1973@gmail.com)
- [ ] Check IIS logs for errors
- [ ] Test API endpoints through browser
- [ ] Verify static files load correctly

## Security Notes

- **SQL Server**: Using SQL authentication (consider Windows Auth for production)
- **Passwords**: Currently hardcoded in SQL scripts (rotate in production)
- **SECRET_KEY**: Must be strong random string in production
- **HTTPS**: Configure SSL certificate in IIS for production
- **CSRF**: Enabled by default via Flask-WTF

## Performance Considerations

- **Database Pool**: Configure `SQLALCHEMY_POOL_SIZE=10`
- **IIS Recycling**: Set appropriate app pool recycling rules
- **Static Files**: Consider serving directly via IIS (not Flask)
- **Caching**: Redis configuration available but not enabled

## Monitoring

- **Logs**: `/logs/app.log`, `/debug_logs/*.log`
- **IIS Logs**: `C:\inetpub\logs\LogFiles\`
- **SQL Server**: Use SSMS Activity Monitor
- **Health Check**: `GET /scraper/health` endpoint available