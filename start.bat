@echo off
title Media Scraper - Starting
echo ============================================
echo   Enhanced Media Scraper - Starting
echo ============================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python and try again.
    pause
    exit /b 1
)

REM Check if app.py exists
if not exist "app.py" (
    echo ERROR: app.py not found in current directory
    echo Please run this script from the project root directory
    pause
    exit /b 1
)

REM Check if the app is already running
netstat -an | findstr :5000 >nul
if not errorlevel 1 (
    echo WARNING: Port 5000 is already in use!
    echo The application might already be running.
    echo.
    choice /C YN /M "Do you want to continue anyway?"
    if errorlevel 2 exit /b 0
)

REM Set environment variables if .env file exists
if exist ".env" (
    echo Loading environment variables from .env file...
    for /f "delims=" %%a in (.env) do (
        set "%%a"
    )
)

REM Start the Flask application in a new window
echo Starting Flask application...
echo.
echo Server will be available at: http://localhost:5000
echo.
echo Press Ctrl+C to stop the server
echo ============================================
echo.

REM Run the application
start "Media Scraper Server" /B cmd /c "python app.py"

echo.
echo Application started successfully!
echo Opening browser in 3 seconds...
timeout /t 3 /nobreak >nul

REM Open the application in the default browser
start http://localhost:5000

echo.
echo The application is running in a separate window.
echo Use stop.bat to stop the application.
pause 