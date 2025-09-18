# Enhanced Media Scraper - Windows Enterprise Deployment Guide

This guide covers deploying the Enhanced Media Scraper application in a Windows enterprise environment using IIS FastCGI and SQL Server Express.

## Overview

The Enhanced Media Scraper is designed for enterprise Windows deployment with:
- **IIS FastCGI Integration**: Production-ready deployment using IIS with FastCGI and wfastcgi
- **SQL Server Express**: Native support with Windows Authentication and secure encrypted connections
- **Enterprise Security**: Comprehensive security headers, CSRF protection, and least-privilege permissions
- **WSGI Architecture**: Proper Flask WSGI deployment without standalone HTTP servers

## Prerequisites

### System Requirements
- **Windows Server 2016+** or **Windows 10/11 Pro**
- **Python 3.8+** (recommended: Python 3.11)
- **IIS with FastCGI support**
- **SQL Server Express 2019+** (LocalDB or full instance)
- **PowerShell 5.1+** (for installation scripts)
- **Administrator privileges** (for service installation)

### Required Software
1. **Python for Windows** with pip
2. **IIS** with URL Rewrite Module and FastCGI
3. **SQL Server Express** with SQL Server Management Studio (optional)
4. **Microsoft Visual C++ Redistributable** (for pyodbc)
5. **ODBC Driver 18 for SQL Server**

## Quick Installation

### 1. Automated Installation
Run the PowerShell installation script as Administrator:

```powershell
# Download and extract the application
cd C:\inetpub\wwwroot
git clone <repository-url> enhanced_media_scraper
cd enhanced_media_scraper

# Run automated installation
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.\deployment\windows\install.ps1
```

### 2. Manual Installation

#### Step 1: Python Environment Setup
```powershell
# Install Python dependencies
pip install -r requirements.txt
pip install -r deployment\windows\requirements_windows.txt
```

#### Step 2: Database Configuration
```powershell
# Create SQL Server Express database
sqlcmd -S .\SQLEXPRESS -E -Q "CREATE DATABASE enhanced_media_scraper;"

# Environment variables will be set via IIS Configuration Editor (secure method)
# See Environment Variables section below for secure configuration
```

#### Step 3: IIS Configuration
1. Copy `web.config.enterprise` to `web.config`
2. Configure IIS site pointing to application directory
3. Set up FastCGI handler for Python
4. Configure application pool for Python FastCGI

#### Step 4: Configure FastCGI Mapping
```powershell
# Enable FastCGI for the application
wfastcgi-enable

# Copy web.config to application root
Copy-Item "deployment\windows\web.config.enterprise" "web.config"

# Configure IIS application
Import-Module WebAdministration
New-WebApplication -Site "Default Web Site" -Name "scraper" -PhysicalPath "C:\inetpub\wwwroot\enhanced_media_scraper"
```

## Configuration

### Database Configuration

#### SQL Server Express with Windows Authentication (Enterprise Secure)
```
DATABASE_URL=mssql+pyodbc://./\SQLEXPRESS/enhanced_media_scraper?driver=ODBC Driver 18 for SQL Server&trusted_connection=yes&Encrypt=yes&TrustServerCertificate=no
```

#### SQL Server with SQL Authentication (Enterprise Secure)
```
DATABASE_URL=mssql+pyodbc://username:password@localhost\SQLEXPRESS/enhanced_media_scraper?driver=ODBC Driver 18 for SQL Server&Encrypt=yes&TrustServerCertificate=no
```

### IIS Configuration

The `web.config.enterprise` file provides:
- **FastCGI Handler**: Python script execution through IIS
- **URL Rewriting**: Proper routing for Flask application
- **Static File Handling**: Optimized serving of CSS, JS, and media files
- **Security Headers**: HSTS, X-Frame-Options, Content Security Policy
- **MIME Types**: Support for modern web formats
- **Compression**: Gzip compression for better performance

FastCGI configuration is handled by wfastcgi-enable and install.ps1:
- Python paths are dynamically detected during installation
- FastCGI application is registered via applicationHost.config
- Environment variables are set securely via IIS Configuration Editor
- No hardcoded paths or secrets in web.config

Entry point: `index.py` → `app.application` (Flask WSGI object)

### FastCGI Configuration

The FastCGI deployment provides:
- **Production Performance**: High-performance WSGI execution through IIS
- **Process Management**: Automatic process recycling and resource management
- **Security**: Least-privilege execution under application pool identity
- **Reliability**: Built-in error handling and process monitoring

FastCGI features:
- Uses proper WSGI entry point (app.app)
- No standalone HTTP server conflicts
- Integrated with IIS request pipeline
- Automatic process scaling and recycling

### Environment Variables

Set these environment variables for production:

**CRITICAL: Set environment variables securely via IIS Configuration Editor**

1. Open IIS Manager → Select your application
2. Go to Configuration Editor
3. Navigate to system.webServer/fastCgi → Select your application
4. Add environment variables:

```
DATABASE_URL=mssql+pyodbc://./\SQLEXPRESS/enhanced_media_scraper?driver=ODBC Driver 18 for SQL Server&trusted_connection=yes&Encrypt=yes&TrustServerCertificate=no
SECRET_KEY=generate-a-secure-random-key-here
FLASK_ENV=production
```

**Never commit secrets to web.config or repository files.**

## Security Considerations

### Windows Authentication
- Uses Windows Authentication with SQL Server Express
- No database credentials stored in application
- Integrates with Active Directory for user management

### IIS Security
- HTTPS redirection enabled
- Security headers configured
- CSRF protection enabled
- Content Security Policy (CSP) implemented

### File System Security
- Application runs with minimal privileges
- Files stored in protected directories
- Temporary files cleaned up automatically

## Troubleshooting

### Common Issues

#### 1. Service Won't Start
```powershell
# Check service status
.\service_manager.ps1 status

# Check Windows Event Log
Get-EventLog -LogName Application -Source "Enhanced Media Scraper" -Newest 10
```

#### 2. Database Connection Issues
```powershell
# Test database connection
sqlcmd -S .\SQLEXPRESS -E -Q "SELECT 1"

# Check ODBC driver
odbcad32.exe
```

#### 3. IIS 500 Errors
- Check IIS logs in `C:\inetpub\logs\LogFiles`
- Verify Python path in web.config
- Ensure FastCGI is installed and configured
- Check application pool configuration

#### 4. Permission Issues
```powershell
# Grant IIS_IUSRS permissions to application directory
icacls "C:\inetpub\wwwroot\enhanced_media_scraper" /grant "IIS_IUSRS:(OI)(CI)F" /T
```

### Logging

Logs are stored in multiple locations:
- **Application Logs**: `C:\ProgramData\EnhancedMediaScraper\logs\`
- **Service Logs**: Windows Event Log (Application source)
- **IIS Logs**: `C:\inetpub\logs\LogFiles\`
- **Debug Logs**: Application directory `logs\` folder

## Performance Optimization

### IIS Optimizations
- Enable static file compression
- Configure output caching
- Use dedicated application pool
- Set appropriate memory limits

### Database Optimizations
- Enable connection pooling
- Configure appropriate timeout values
- Set up database maintenance plans
- Monitor query performance

### Application Optimizations
- Use production WSGI server (Waitress)
- Enable asset compression
- Configure caching headers
- Optimize image processing

## Monitoring and Maintenance

### Health Checks
The application provides health check endpoints:
- `/health` - Basic application health
- `/api/stats` - Application statistics
- Application pool status via IIS Manager

### Backup Procedures
```powershell
# Database backup
sqlcmd -S .\SQLEXPRESS -E -Q "BACKUP DATABASE enhanced_media_scraper TO DISK = 'C:\Backups\enhanced_media_scraper.bak'"

# Application backup
xcopy "C:\inetpub\wwwroot\enhanced_media_scraper" "C:\Backups\Application\" /E /I /Y
```

### Updates and Upgrades
1. Stop IIS application pool
2. Backup database and application files
3. Deploy new application files
4. Run database migrations if needed
5. Restart IIS application pool
6. Verify functionality

## Advanced Configuration

### Load Balancing
For multiple server deployments:
- Use IIS Application Request Routing (ARR)
- Configure SQL Server for multi-server access
- Implement session state management
- Set up health monitoring

### SSL/TLS Configuration
```xml
<!-- In web.config for HTTPS enforcement -->
<system.webServer>
  <rewrite>
    <rules>
      <rule name="Redirect to HTTPS" stopProcessing="true">
        <match url=".*" />
        <conditions>
          <add input="{HTTPS}" pattern="off" ignoreCase="true" />
        </conditions>
        <action type="Redirect" url="https://{HTTP_HOST}/{R:0}" redirectType="Permanent" />
      </rule>
    </rules>
  </rewrite>
</system.webServer>
```

### Active Directory Integration
Configure Windows Authentication in IIS:
1. Enable Windows Authentication
2. Disable Anonymous Authentication
3. Configure appropriate authentication providers
4. Set up user group permissions

## Support and Documentation

### Log Analysis
Use PowerShell for log analysis:
```powershell
# Analyze application logs
Get-Content "C:\inetpub\wwwroot\enhanced_media_scraper\logs\*.log" | 
  Where-Object {$_ -match "ERROR|WARN"} |
  Select-Object -Last 20

# Analyze IIS logs
Get-Content "C:\inetpub\logs\LogFiles\W3SVC1\*.log" | 
  Select-String "500|error" | 
  Select-Object -Last 10
```

### Performance Monitoring
```powershell
# Monitor application performance
Get-Counter "\Process(python)\% Processor Time"
Get-Counter "\Process(python)\Working Set"
```

For additional support:
1. Check application logs for specific error messages
2. Review IIS configuration and logs
3. Verify database connectivity and permissions
4. Test application functionality via web interface

This deployment guide ensures a secure, scalable, and maintainable installation of the Enhanced Media Scraper in Windows enterprise environments.