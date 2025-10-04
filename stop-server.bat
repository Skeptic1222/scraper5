@echo off
echo ===================================
echo Enhanced Media Scraper Server Stop
echo ===================================

REM Find and kill Python processes using port 5050 (Scraper project)
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :5050') do (
    echo Stopping Enhanced Media Scraper process with PID %%a...
    taskkill /PID %%a /F
)

REM Find and kill any remaining Flask processes
taskkill /FI "WINDOWTITLE eq Enhanced Media Scraper" /F 2>nul
taskkill /FI "IMAGENAME eq python.exe" /FI "WINDOWTITLE eq Flask*" /F 2>nul

echo Server stopped successfully!
timeout /t 2 /nobreak >nul