# Service Management - Enhanced Media Scraper

This document explains how to use the batch files to manage the Flask application on Windows.

## Quick Start

### Basic Commands

1. **Start the application**:
   ```batch
   start.bat
   ```
   - Checks if Python is installed
   - Loads environment variables from `.env` file
   - Starts the Flask application in a new window
   - Opens your browser automatically

2. **Stop the application**:
   ```batch
   stop.bat
   ```
   - Finds and stops the Flask application
   - Frees up port 5000
   - Asks for confirmation before stopping

3. **Restart the application**:
   ```batch
   restart.bat
   ```
   - Stops the running application (if any)
   - Starts it fresh
   - Useful when you've made code changes

4. **Run in production mode** (with logging):
   ```batch
   start_production.bat
   ```
   - Runs with production settings
   - Creates timestamped log files in `logs/` directory
   - Shows live log output
   - Better error handling

## Features

### Environment Variables
All batch files automatically load environment variables from your `.env` file if it exists.

### Port Checking
The scripts check if port 5000 is already in use and handle it appropriately.

### Error Handling
- Checks if Python is installed
- Verifies `app.py` exists
- Provides clear error messages

### Logging (Production Mode)
The production script creates detailed logs with timestamps:
- Log files are stored in `logs/` directory
- Format: `scraper_YYYY-MM-DD_HH-MM-SS.log`
- Live log viewing with PowerShell

## Troubleshooting

### "Python is not installed or not in PATH"
- Install Python from https://python.org
- Make sure to check "Add Python to PATH" during installation

### "Port 5000 is already in use"
- Another application is using port 5000
- Run `stop.bat` to stop the Media Scraper
- Or choose to continue anyway when prompted

### "Access Denied" errors
- Run the batch files as Administrator
- Right-click → "Run as administrator"

### Application won't stop
1. Open Task Manager (Ctrl+Shift+Esc)
2. Look for `python.exe` processes
3. End the process manually
4. Or restart your computer

## Advanced Usage

### Custom Port
To run on a different port, modify the `app.py` file or set an environment variable:
```
set FLASK_PORT=8080
start.bat
```

### Running as a Windows Service
For production deployment, consider using:
- NSSM (Non-Sucking Service Manager)
- Windows Task Scheduler
- IIS with FastCGI

### Monitoring
The production script creates logs that can be monitored with:
- Windows Event Viewer
- PowerShell: `Get-Content logs\latest.log -Wait`
- Third-party tools like Log Expert

## Security Notes

1. **Production Deployment**:
   - Use `start_production.bat` for production
   - Set `FLASK_ENV=production` in your `.env` file
   - Use HTTPS with a reverse proxy (nginx/IIS)

2. **Firewall**:
   - By default, the app listens on `0.0.0.0` (all interfaces)
   - Configure Windows Firewall to allow/block external access

3. **Permissions**:
   - The app runs with your user permissions
   - For production, consider a dedicated service account

## Tips

- Keep the console window open to see real-time logs
- Use `Ctrl+C` in the console to stop the server gracefully
- Check the `logs/` directory for debugging issues
- The browser opens automatically after starting

## File Locations

- **Application**: `C:\inetpub\wwwroot\scraper\`
- **Logs**: `C:\inetpub\wwwroot\scraper\logs\`
- **Database**: SQL Server Express (configured in `.env`)
- **Media Storage**: Database (MediaBlob table) 