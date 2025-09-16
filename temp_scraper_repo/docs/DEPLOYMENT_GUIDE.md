# 🚀 Media Scraper Deployment Guide

## Prerequisites

### System Requirements
- Windows Server with IIS or Windows 10/11 with IIS enabled
- Python 3.8+ installed
- SQL Server Express or full SQL Server
- WSL2 (for development)

### Required Python Packages
```bash
pip install -r requirements.txt
```

Key dependencies:
- Flask and extensions (Flask-SQLAlchemy, Flask-Login, Flask-CORS)
- yt-dlp (for video downloading)
- beautifulsoup4 (for HTML parsing)
- aiohttp (for async HTTP requests)
- playwright (for browser automation)
- pyodbc (for SQL Server connection)

## Development Setup

### 1. Clone Repository
```bash
cd /mnt/c/inetpub/wwwroot
git clone [repository-url] scraper
cd scraper
```

### 2. Environment Configuration
Create `.env` file:
```bash
cp .env.template .env
```

Edit `.env` with your credentials:
```env
DATABASE_URL=mssql+pyodbc://username:password@localhost/scraper_db?driver=ODBC+Driver+17+for+SQL+Server
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
SECRET_KEY=generate_random_secret_key
PAYPAL_CLIENT_ID=your_paypal_client_id
PAYPAL_CLIENT_SECRET=your_paypal_client_secret
ADMIN_EMAIL=admin@example.com
```

### 3. Database Setup
```bash
# Initialize database
python init_db.py

# Or for SQL Server specifically
python init_sqlserver_db.py

# Apply performance indexes
python apply_db_indexes.py
```

### 4. Install Browser Drivers (for Playwright)
```bash
playwright install chromium
playwright install firefox
```

### 5. Run Development Server
```bash
# Using refactored architecture
python app_refactored.py

# Or traditional app
python app.py
```

Access at: `http://localhost/scraper`

## Production Deployment

### 1. IIS Configuration

#### Install Required IIS Features
```powershell
# Run as Administrator
Enable-WindowsOptionalFeature -Online -FeatureName IIS-WebServerRole, IIS-WebServer, IIS-CommonHttpFeatures, IIS-HttpErrors, IIS-HttpRedirect, IIS-ApplicationDevelopment, IIS-NetFxExtensibility45, IIS-HealthAndDiagnostics, IIS-HttpLogging, IIS-Security, IIS-RequestFiltering, IIS-URLAuthorization, IIS-IPSecurity, IIS-Performance, IIS-WebServerManagementTools, IIS-ManagementConsole, IIS-IIS6ManagementCompatibility, IIS-Metabase

# Install URL Rewrite Module
# Download from: https://www.iis.net/downloads/microsoft/url-rewrite
```

#### Configure Application Pool
1. Open IIS Manager
2. Create new Application Pool "ScraperPool"
3. Set .NET CLR Version: No Managed Code
4. Set Pipeline Mode: Integrated
5. Set Identity: ApplicationPoolIdentity or custom service account

#### Create Website/Application
1. Right-click Sites → Add Application
2. Alias: `scraper`
3. Physical Path: `C:\inetpub\wwwroot\scraper`
4. Application Pool: ScraperPool

#### Configure URL Rewrite
The `web.config` is already configured for proper routing:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<configuration>
    <system.webServer>
        <rewrite>
            <rules>
                <rule name="Flask Routes" stopProcessing="true">
                    <match url=".*" />
                    <conditions>
                        <add input="{REQUEST_FILENAME}" matchType="IsFile" negate="true" />
                        <add input="{REQUEST_FILENAME}" matchType="IsDirectory" negate="true" />
                    </conditions>
                    <action type="Rewrite" url="http://localhost:5000/{R:0}" />
                </rule>
            </rules>
        </rewrite>
    </system.webServer>
</configuration>
```

### 2. Production Server Setup

#### Using Windows Service
```bash
# Install as Windows service
python startup_scripts/start_server.py --install

# Start service
net start MediaScraper

# Stop service
net stop MediaScraper
```

#### Using Batch Scripts
```bash
# Start production server
startup_scripts/start.bat

# Stop server
startup_scripts/stop.bat

# Restart server
startup_scripts/restart.bat
```

### 3. SSL/HTTPS Configuration

#### Generate SSL Certificate
```powershell
# For development/testing
New-SelfSignedCertificate -DnsName "localhost" -CertStoreLocation "cert:\LocalMachine\My"

# For production, use Let's Encrypt or commercial certificate
```

#### Configure HTTPS Binding in IIS
1. Select site in IIS Manager
2. Click "Bindings" in Actions pane
3. Add HTTPS binding on port 443
4. Select SSL certificate

### 4. Security Hardening

#### Enable Security Features
```bash
# Set production mode in .env
FLASK_ENV=production
DEBUG=False

# Enable all security features
python app.py --secure
```

#### Configure Firewall
```powershell
# Allow HTTP/HTTPS
New-NetFirewallRule -DisplayName "Scraper HTTP" -Direction Inbound -Protocol TCP -LocalPort 80 -Action Allow
New-NetFirewallRule -DisplayName "Scraper HTTPS" -Direction Inbound -Protocol TCP -LocalPort 443 -Action Allow
```

## Monitoring & Maintenance

### Log Files
- Application logs: `logs/server.log`
- Error logs: `logs/error.log`
- Access logs: `logs/access.log`

### Monitoring Commands
```bash
# Monitor real-time logs
python monitor_logs.py

# Check system health
curl http://localhost/scraper/health

# View method statistics
curl http://localhost/scraper/api/method-stats
```

### Database Maintenance
```sql
-- Check database size
SELECT 
    DB_NAME(database_id) AS DatabaseName,
    SUM(size * 8 / 1024) AS SizeMB
FROM sys.master_files
WHERE database_id = DB_ID('scraper_db')
GROUP BY database_id;

-- Clean old jobs (older than 30 days)
DELETE FROM scrape_jobs 
WHERE created_at < DATEADD(day, -30, GETDATE());

-- Optimize indexes
ALTER INDEX ALL ON assets REBUILD;
ALTER INDEX ALL ON scrape_jobs REBUILD;
ALTER INDEX ALL ON method_configs REBUILD;
```

### Backup Strategy
```bash
# Database backup
sqlcmd -S localhost -Q "BACKUP DATABASE scraper_db TO DISK='C:\Backups\scraper_db.bak'"

# File system backup
robocopy C:\inetpub\wwwroot\scraper C:\Backups\scraper /E /ZB /R:3 /W:10

# Automated daily backup (Task Scheduler)
schtasks /create /tn "ScraperBackup" /tr "C:\Scripts\backup_scraper.bat" /sc daily /st 02:00
```

## Troubleshooting

### Common Issues

#### Port Already in Use
```bash
# Find process using port 5000
netstat -ano | findstr :5000

# Kill process
taskkill /PID [process_id] /F
```

#### Database Connection Failed
```bash
# Test SQL Server connection
python verify_sqlserver.py

# Check SQL Server service
sc query MSSQLSERVER

# Restart SQL Server
net stop MSSQLSERVER && net start MSSQLSERVER
```

#### Method Not Working
```python
# Clear method cache for a source
from src.models.method_config import MethodConfig, db
MethodConfig.query.filter_by(source='reddit').delete()
db.session.commit()
```

#### IIS 503 Service Unavailable
1. Check Application Pool is started
2. Verify Python process is running
3. Check Windows Event Viewer for errors
4. Review IIS logs in `C:\inetpub\logs\LogFiles`

## Performance Optimization

### Enable Caching
```python
# In config.py
CACHE_TYPE = "simple"
CACHE_DEFAULT_TIMEOUT = 300
```

### Configure Connection Pool
```python
# In config.py
SQLALCHEMY_ENGINE_OPTIONS = {
    'pool_size': 20,
    'pool_recycle': 3600,
    'pool_pre_ping': True,
    'max_overflow': 40
}
```

### Enable Compression
```xml
<!-- In web.config -->
<system.webServer>
    <urlCompression doStaticCompression="true" doDynamicCompression="true" />
</system.webServer>
```

## Scaling Considerations

### Horizontal Scaling
- Use Redis for session storage
- Configure load balancer (nginx/IIS ARR)
- Share media storage (NAS/S3)

### Vertical Scaling
- Increase worker processes
- Upgrade SQL Server edition
- Add more RAM for caching

### CDN Integration
- Serve static files from CDN
- Cache API responses
- Implement edge caching

## Support

### Getting Help
- Check `docs/` directory for detailed documentation
- Review `CLAUDE.md` for AI assistant guidance
- Check logs for error details

### Reporting Issues
- Include error messages from logs
- Specify source and URL that failed
- Provide steps to reproduce

### Contributing
- Follow existing code patterns
- Add tests for new features
- Update documentation
- Submit pull requests

---

**Deployment Status: READY ✅**

The application is fully configured and ready for deployment in development or production environments.
