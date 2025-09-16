# Windows IIS Deployment Guide
**Enhanced Media Scraper - Flask Application on Windows 11 24H2 with IIS**  
**Date**: June 18, 2025

## 🖥️ WINDOWS ENVIRONMENT CONTEXT

### Current Setup
- **Host OS**: Windows 11 24H2  
- **Web Server**: IIS (Internet Information Services)
- **Application**: Flask-based Enhanced Media Scraper
- **Location**: `C:\inetpub\wwwroot\scraper`
- **Python**: Windows Python installation (not WSL)
- **Database**: SQL Server Express (Windows)

### WSL vs Windows Context
- **WSL Ubuntu**: Used for code review and script creation (current environment)
- **Windows IIS**: Target deployment environment for the Flask application
- **File Access**: WSL can access Windows files via `/c/inetpub/wwwroot/scraper`

## 🚀 WINDOWS IIS DEPLOYMENT STEPS

### Step 1: Windows Python Environment Setup

```cmd
# Open Command Prompt as Administrator on Windows
cd C:\inetpub\wwwroot\scraper

# Verify Python installation
python --version
# Expected: Python 3.13 or later

# Install/verify required modules
pip install -r requirements.txt

# Test Flask import
python -c "import flask; print('Flask version:', flask.__version__)"
```

### Step 2: IIS Configuration for Flask

#### Create Application Pool
1. Open **IIS Manager** on Windows
2. Right-click **Application Pools** → **Add Application Pool**
3. **Name**: `ScraperAppPool`
4. **.NET CLR Version**: No Managed Code
5. **Managed Pipeline Mode**: Integrated
6. **Identity**: ApplicationPoolIdentity or specific user account

#### Configure Website
1. Right-click **Sites** → **Add Website**
2. **Site Name**: `Enhanced Media Scraper`
3. **Physical Path**: `C:\inetpub\wwwroot\scraper`
4. **Port**: 5000 (or preferred port)
5. **Application Pool**: ScraperAppPool

#### Install wfastcgi (Flask on IIS)
```cmd
# Install wfastcgi for Flask on IIS
pip install wfastcgi

# Enable wfastcgi
wfastcgi-enable
```

### Step 3: Create web.config for IIS

```xml
<?xml version="1.0" encoding="utf-8"?>
<configuration>
  <appSettings>
    <add key="PYTHONPATH" value="C:\inetpub\wwwroot\scraper" />
    <add key="WSGI_HANDLER" value="app.app" />
    <add key="WSGI_LOG" value="C:\inetpub\wwwroot\scraper\logs\wfastcgi.log" />
  </appSettings>
  <system.webServer>
    <handlers>
      <add name="PythonHandler" path="*" verb="*" 
           modules="FastCgiModule" 
           scriptProcessor="C:\Python313\python.exe|C:\Python313\Lib\site-packages\wfastcgi.py" 
           resourceType="Unspecified" 
           requireAccess="Script" />
    </handlers>
    <defaultDocument>
      <files>
        <clear />
        <add value="app.py" />
      </files>
    </defaultDocument>
  </system.webServer>
</configuration>
```

### Step 4: Windows-Specific Environment Configuration

#### Update .env for Windows Paths
```env
# Database Configuration - Windows SQL Server Express
DATABASE_URL=mssql+pyodbc://localhost\SQLEXPRESS/Scraped?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes

# Windows-specific paths
UPLOAD_FOLDER=C:\inetpub\wwwroot\scraper\downloads
LOG_FILE_PATH=C:\inetpub\wwwroot\scraper\logs\scraper.log

# IIS Security
DEBUG=False
FLASK_ENV=production
SESSION_COOKIE_SECURE=True
```

#### Create Windows Batch Scripts
**start_scraper.bat**:
```batch
@echo off
cd /d C:\inetpub\wwwroot\scraper
echo Starting Enhanced Media Scraper...
python app.py
pause
```

**restart_iis.bat**:
```batch
@echo off
echo Restarting IIS Application Pool...
%WINDIR%\System32\inetsrv\appcmd.exe recycle apppool "ScraperAppPool"
echo Application pool restarted.
pause
```

### Step 5: Windows Services Integration

#### Create Windows Service (Optional)
```cmd
# Install pywin32 for Windows service support
pip install pywin32

# Create service script (service.py)
# This allows the Flask app to run as a Windows service
```

### Step 6: Windows-Specific Security Configuration

#### IIS Security Settings
1. **Authentication**: 
   - Disable Anonymous Authentication
   - Enable Windows Authentication (if needed)
   - Configure OAuth redirect URLs for Windows domain

2. **SSL/TLS Configuration**:
   - Install SSL certificate in IIS
   - Force HTTPS redirects
   - Update CSP headers for HTTPS

3. **File Permissions**:
   - Grant IIS_IUSRS read/write access to `logs/` directory
   - Grant read access to application files
   - Secure `downloads/` directory

#### Windows Firewall
```cmd
# Open Windows Firewall for the application port
netsh advfirewall firewall add rule name="Enhanced Media Scraper" dir=in action=allow protocol=TCP localport=5000
```

## 🔧 WINDOWS-SPECIFIC FIXES NEEDED

### Update Python Paths in Scripts
The migration and monitoring scripts need Windows paths:

**apply_db_indexes_windows.bat**:
```batch
@echo off
cd /d C:\inetpub\wwwroot\scraper
echo Applying database indexes...
python apply_db_indexes.py
pause
```

**monitor_logs_windows.bat**:
```batch
@echo off
cd /d C:\inetpub\wwwroot\scraper
echo Starting log monitoring...
python monitor_logs.py
pause
```

### Windows SQL Server Configuration
```cmd
# Verify SQL Server Express is running
sc query "MSSQL$SQLEXPRESS"

# Test database connection
sqlcmd -S localhost\SQLEXPRESS -E -Q "SELECT @@VERSION"
```

## 🖥️ WINDOWS DEPLOYMENT CHECKLIST

### Pre-Deployment
- [ ] IIS installed and configured
- [ ] Python 3.13+ installed on Windows
- [ ] SQL Server Express running
- [ ] All Python dependencies installed
- [ ] Web.config created
- [ ] Application pool configured

### Security Configuration
- [ ] .env file updated with production settings
- [ ] SSL certificate installed (for HTTPS)
- [ ] Windows firewall configured
- [ ] File permissions set correctly
- [ ] Authentication method configured

### Testing
- [ ] Application starts without errors
- [ ] Database connectivity verified
- [ ] Google OAuth working (with Windows redirect URLs)
- [ ] File uploads/downloads functional
- [ ] Logging working in Windows environment

### Performance
- [ ] Database indexes applied via SQL Server Management Studio
- [ ] IIS application pool optimized
- [ ] Static file caching configured
- [ ] Log rotation configured

## 🚀 WINDOWS STARTUP PROCEDURE

### Method 1: Direct Python Execution
```cmd
cd C:\inetpub\wwwroot\scraper
python app.py
```

### Method 2: IIS Integration
1. Start IIS Manager
2. Start "Enhanced Media Scraper" site
3. Application available at `http://localhost/scraper` (IIS proxy)

### Method 3: Windows Service (Advanced)
```cmd
# Install as Windows service
python service.py install

# Start service
net start "Enhanced Media Scraper"
```

## 📊 WINDOWS-SPECIFIC MONITORING

### Windows Event Log Integration
```python
# Add to logging configuration for Windows Event Log
import logging.handlers

# Windows Event Log handler
event_handler = logging.handlers.NTEventLogHandler(
    'Enhanced Media Scraper',
    logtype='Application'
)
```

### Performance Counters
- Monitor IIS application pool health
- Track SQL Server Express performance
- Monitor Windows file system usage

### Windows Management Tools
- **IIS Manager**: Application pool and site management
- **SQL Server Management Studio**: Database optimization
- **Windows Task Manager**: Resource monitoring
- **Windows Event Viewer**: Application logs

## 🔄 MAINTENANCE ON WINDOWS

### Daily Operations
```batch
# Check application status
iisreset /status

# Monitor logs
type C:\inetpub\wwwroot\scraper\logs\scraper.log | findstr ERROR

# Check database
sqlcmd -S localhost\SQLEXPRESS -E -Q "SELECT COUNT(*) FROM assets"
```

### Updates and Patches
1. **Python Updates**: Update Windows Python installation
2. **IIS Updates**: Windows Update for IIS patches
3. **SQL Server**: SQL Server Express maintenance
4. **SSL Certificates**: Renewal via IIS Manager

---

**Windows Deployment Status**: Ready for IIS Configuration  
**Environment**: Windows 11 24H2 with IIS  
**Database**: SQL Server Express  
**Application**: Flask with wfastcgi integration
