@echo off
title Enhanced Media Scraper - Flask Service
echo ============================================
echo Enhanced Media Scraper - Flask Service
echo ============================================
echo.

:: Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    pause
    exit /b 1
)

:: Navigate to the application directory
cd /d C:\inetpub\wwwroot\scraper

:: Kill any existing Python processes on port 3050
echo Stopping any existing Flask instances...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :3050') do (
    echo Killing PID %%a
    taskkill /PID %%a /F >nul 2>&1
)

:: Wait a moment for the port to be released
timeout /t 2 /nobreak >nul

:: Set environment variables
set FLASK_APP=app.py
set FLASK_ENV=production
set FLASK_RUN_PORT=3050
set OAUTHLIB_INSECURE_TRANSPORT=1

echo.
echo Starting Flask application on port 3050...
echo Server will be available at:
echo   - Direct: http://localhost:3050
echo   - Via IIS: http://localhost/scraper
echo.
echo Press Ctrl+C to stop the server
echo ============================================
echo.

:: Start Flask
python app.py

echo.
echo Flask server has stopped.
pause