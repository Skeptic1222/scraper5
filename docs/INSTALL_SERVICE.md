# Enhanced Media Scraper - Service Installation

## For Linux/WSL Systems

To install the Enhanced Media Scraper as a system service:

```bash
# Copy service file to systemd directory
sudo cp scraper.service /etc/systemd/system/

# Update the User in the service file to your username
sudo sed -i "s/User=user/User=$USER/g" /etc/systemd/system/scraper.service

# Reload systemd
sudo systemctl daemon-reload

# Enable the service to start on boot
sudo systemctl enable scraper.service

# Start the service
sudo systemctl start scraper.service

# Check service status
sudo systemctl status scraper.service
```

## For Windows Systems

Use the provided batch files:
- `FIX_AND_RUN.bat` - Complete setup and run
- `start_windows.bat` - Quick start
- `run_app.bat` - Simple run

To create a Windows service, use NSSM (Non-Sucking Service Manager):
1. Download NSSM from https://nssm.cc/
2. Run: `nssm install "Enhanced Media Scraper"`
3. Set path to: `C:\Python3XX\python.exe`
4. Set arguments: `C:\inetpub\wwwroot\scraper\app.py`
5. Set working directory: `C:\inetpub\wwwroot\scraper`

## Quick Start Commands

### Linux/WSL:
```bash
./start.sh
```

### Windows:
```cmd
FIX_AND_RUN.bat
```

### Python (Cross-platform):
```bash
python3 app_with_fallback.py
```

## Access the Application

Once running, access at: http://localhost/scraper
