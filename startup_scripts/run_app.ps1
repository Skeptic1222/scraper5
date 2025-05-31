# Media Scraper Production Server Launcher
# Auto-start script for Windows Task Scheduler

Set-Location "C:\inetpub\wwwroot\scraper"

# Use system Python directly to avoid venv issues
& "C:\Program Files\Python313\python.exe" run_production.py 