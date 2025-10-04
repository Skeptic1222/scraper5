# Auto-Start Setup Instructions

## Quick Start (Windows Service with NSSM)

Your Flask application will automatically start on boot and restart if it crashes.

### Step 1: Run Setup Script

1. **Open PowerShell as Administrator**
   - Press `Win + X`
   - Click "Windows PowerShell (Admin)" or "Terminal (Admin)"

2. **Run the setup script:**
   ```powershell
   cd C:\inetpub\wwwroot\scraper
   .\setup-autostart.ps1
   ```

3. **Wait for completion** - You should see:
   ```
   ✓ Flask app will now auto-start on system boot!
   ```

### Step 2: Verify Service

```powershell
# Check service status
sc query FlaskMediaScraper

# Test the website
Start-Process "http://localhost/scraper"

# View live logs
Get-Content "C:\logs\services\FlaskMediaScraper\stdout.log" -Tail 20 -Wait
```

### Step 3: Test Reboot

1. Reboot your computer
2. Wait 1-2 minutes after login
3. Open browser to `http://localhost/scraper`
4. It should load automatically!

---

## Service Management

### View Status
```powershell
sc query FlaskMediaScraper
Get-Service FlaskMediaScraper | Format-List *
```

### Stop Service
```powershell
sc stop FlaskMediaScraper
```

### Start Service
```powershell
sc start FlaskMediaScraper
```

### Restart Service
```powershell
sc stop FlaskMediaScraper
timeout /t 5
sc start FlaskMediaScraper
```

### View Logs
```powershell
# View latest output
Get-Content "C:\logs\services\FlaskMediaScraper\stdout.log" -Tail 50

# View errors
Get-Content "C:\logs\services\FlaskMediaScraper\stderr.log" -Tail 50

# Watch logs in real-time
Get-Content "C:\logs\services\FlaskMediaScraper\stdout.log" -Tail 20 -Wait
```

---

## Uninstall Service

If you need to remove the auto-start service:

```powershell
# Run as Administrator
C:\tools\nssm-2.24\win64\nssm.exe stop FlaskMediaScraper
C:\tools\nssm-2.24\win64\nssm.exe remove FlaskMediaScraper confirm
```

---

## Troubleshooting

### Service won't start
1. Check logs: `Get-Content C:\logs\services\FlaskMediaScraper\stderr.log`
2. Verify Python path: `Test-Path C:\Python311\python.exe`
3. Test manually: `cd C:\inetpub\wwwroot\scraper; python app.py`

### Website not loading after boot
1. Wait 2-3 minutes (service needs startup time)
2. Check service status: `sc query FlaskMediaScraper`
3. Check IIS: Open IIS Manager, verify "Default Web Site" is running
4. Check port 5050: `netstat -ano | findstr :5050`

### Port already in use
```powershell
# Find what's using port 5050
netstat -ano | findstr :5050

# Kill the process (replace PID with actual number)
taskkill /PID <PID> /F
```

### Need to change port
Edit `.env` file and change `PORT=5050` to another port, then restart service.

---

## Configuration

Service configuration stored in Windows Registry:
```
HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Services\FlaskMediaScraper
```

Modify with NSSM GUI:
```powershell
C:\tools\nssm-2.24\win64\nssm.exe edit FlaskMediaScraper
```

---

## Files Created

- **Service**: FlaskMediaScraper (Windows Service)
- **Logs**: `C:\logs\services\FlaskMediaScraper\`
  - `stdout.log` - Application output
  - `stderr.log` - Errors and warnings
- **NSSM**: `C:\tools\nssm-2.24\`

---

## Recovery Settings

The service is configured to automatically restart if it crashes:
- **1st failure**: Restart after 10 seconds
- **2nd failure**: Restart after 10 seconds
- **Subsequent failures**: Restart after 10 seconds
- **Throttle**: 5 seconds minimum between restarts

---

## What Happens on Boot

1. **Windows starts** → Loads core services
2. **FlaskMediaScraper service starts** → Runs `python app.py`
3. **Flask binds to port 5050** → Listens for connections
4. **IIS reverse proxy** → Routes `/scraper` to port 5050
5. **You open browser** → `http://localhost/scraper` works!

**Total boot-to-ready time**: 1-2 minutes

---

## Support

If issues persist:
1. Check Windows Event Viewer → Windows Logs → System
2. Filter by Source: "Service Control Manager"
3. Look for FlaskMediaScraper errors
4. Check IIS logs: `C:\inetpub\logs\LogFiles\`
