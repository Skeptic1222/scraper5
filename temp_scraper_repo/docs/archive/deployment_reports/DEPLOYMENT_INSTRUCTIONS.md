# Enhanced Media Scraper - Deployment Instructions
*Last Updated: 2025-09-13*

## 🚀 Quick Start

### Single Instance Startup (Recommended)
```bash
# This script automatically kills existing instances and starts a clean one
python3 start_single_instance.py
```

### Manual Startup
```bash
# Set environment variables
export FLASK_ENV=production
export ALLOW_MOCK_LOGIN=true
export APP_BASE=/scraper
export DATABASE_URL="mssql+pyodbc://sa:Admin123!@localhost/scraperdb?driver=ODBC+Driver+17+for+SQL+Server"

# Start the application
python3 app.py
```

## 📋 Pre-Deployment Checklist

### 1. Database Setup
- [ ] SQL Server Express installed and running
- [ ] Database `scraperdb` created
- [ ] User credentials configured
- [ ] **NO SQLite** - Application now uses SQL Express exclusively

### 2. Environment Configuration
- [ ] Create `.env` file with secure credentials
- [ ] Set `DATABASE_URL` environment variable
- [ ] Configure Google OAuth credentials
- [ ] Set `SECRET_KEY` for session management

### 3. IIS Configuration
- [ ] Application running on internal port (5050)
- [ ] IIS reverse proxy configured at `/scraper`
- [ ] **NO PORTS IN URLs** - All URLs use `/scraper` prefix only
- [ ] Static files served by IIS where possible

## 🔧 Recent Fixes Applied

### ✅ Navigation Sidebar Fixed
- Created `sidebar-visibility-fix.css`
- Ensures sidebar is always visible on all pages
- Properly positioned with sticky layout

### ✅ SQLite Completely Removed
- Removed all SQLite fallback code
- Application now requires SQL Server Express
- Updated `app.py` to use SQL Express exclusively

### ✅ URL Configuration Verified
- No hardcoded ports in application code
- All JavaScript uses relative paths
- IIS handles port proxying transparently

### ✅ Google OAuth Preserved
- OAuth configuration remains untouched
- Working authentication flow maintained
- Session management properly configured

## 🛠️ Deployment Steps

### Step 1: Clean Up Existing Processes
```bash
# Option 1: Use the single instance starter (recommended)
python3 start_single_instance.py

# Option 2: Manual cleanup
pkill -f "python.*app.py"
pkill -f "python.*start_production.py"
```

### Step 2: Verify Database Connection
```bash
# Test SQL Server connection
python3 -c "
import pyodbc
conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost;DATABASE=scraperdb;UID=sa;PWD=Admin123!')
print('✅ Database connection successful')
conn.close()
"
```

### Step 3: Start Application
```bash
# Production mode with all fixes
FLASK_ENV=production ALLOW_MOCK_LOGIN=true python3 app.py
```

### Step 4: Verify Deployment
1. Check sidebar navigation is visible
2. Test database operations (no SQLite errors)
3. Verify URLs have no port numbers
4. Test Google OAuth login
5. Check all navigation links work

## 📁 Key Files

### Modified Files
- `app.py` - SQL Express configuration, no SQLite
- `templates/base.html` - Added sidebar visibility fix CSS
- `static/css/fixes/sidebar-visibility-fix.css` - New CSS for navigation

### New Files
- `start_single_instance.py` - Single instance manager
- `FUNCTIONALITY_REVIEW_2025.md` - Complete system review
- `DEPLOYMENT_INSTRUCTIONS.md` - This file

### Configuration Files
- `.env` - Environment variables (create from `.env.example`)
- `web.config` - IIS configuration (no changes needed)

## ⚠️ Important Notes

### Database Requirements
- **SQL Server Express is REQUIRED** - No SQLite fallback
- Default connection string uses `sa` account (change in production)
- Database name: `scraperdb`
- Driver: ODBC Driver 17 for SQL Server

### URL Structure
- Application accessed via: `http://localhost/scraper`
- **NEVER** use: `http://localhost:5050/scraper`
- All internal links use `/scraper` prefix
- IIS handles port proxying transparently

### Security Considerations
- Change default database credentials
- Use environment variables for sensitive data
- Enable HTTPS in production
- Re-enable CSRF protection after testing

## 🔍 Troubleshooting

### Sidebar Not Visible
- Check `sidebar-visibility-fix.css` is loaded
- Clear browser cache
- Verify CSS file path in `base.html`

### Database Connection Errors
- Verify SQL Server Express is running
- Check connection string format
- Ensure ODBC Driver 17 is installed
- Test connection with `sqlcmd` tool

### Port Numbers in URLs
- Check IIS reverse proxy configuration
- Verify `APP_BASE` environment variable is set
- Review JavaScript files for hardcoded URLs

### Multiple Process Issues
- Use `start_single_instance.py` to ensure single instance
- Check for rogue Python processes with `ps aux | grep python`
- Kill all instances before starting new one

## 📊 System Requirements

### Software
- Python 3.8+
- SQL Server Express 2019+
- ODBC Driver 17 for SQL Server
- IIS with URL Rewrite module
- pyodbc Python package

### Hardware (Minimum)
- 2 GB RAM
- 10 GB disk space
- 2 CPU cores

### Network
- Port 5050 (internal Flask app)
- Port 80/443 (IIS public access)
- SQL Server port 1433 (local only)

## 🚦 Health Checks

### Application Status
```bash
# Check if app is running
curl -s http://localhost:5050/health || echo "App not running"

# Check via IIS proxy
curl -s http://localhost/scraper || echo "IIS proxy issue"
```

### Database Status
```bash
# Check SQL Server service
systemctl status mssql-server  # Linux
sc query MSSQLSERVER           # Windows
```

### Process Status
```bash
# Check running processes
ps aux | grep -E "python.*app.py" | grep -v grep

# Check port usage
netstat -tlnp | grep 5050      # Linux
netstat -an | findstr :5050    # Windows
```

## 📝 Maintenance

### Log Files
- Application logs: Check console output
- IIS logs: `C:\inetpub\logs\LogFiles\`
- SQL Server logs: Check SQL Server Management Studio

### Backup
- Database: Regular SQL Server backups
- Application: Git repository backups
- Configuration: Backup `.env` and `web.config`

### Updates
1. Stop application gracefully
2. Pull latest code from repository
3. Update dependencies if needed
4. Run database migrations if any
5. Start application with `start_single_instance.py`

## 🆘 Support

For issues:
1. Check `FUNCTIONALITY_REVIEW_2025.md` for known issues
2. Review logs for error messages
3. Verify all requirements are met
4. Test with `start_single_instance.py` for clean start

---

*Remember: No SQLite, No Ports in URLs, Don't Touch OAuth!*