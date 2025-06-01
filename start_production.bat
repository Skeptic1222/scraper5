@echo off
title Media Scraper - Production Mode
echo ============================================
echo   Enhanced Media Scraper - Production Mode
echo ============================================
echo.

REM Create logs directory if it doesn't exist
if not exist "logs" (
    echo Creating logs directory...
    mkdir logs
)

REM Set timestamp for log files
for /f "tokens=2 delims==" %%a in ('wmic OS Get localdatetime /value') do set "dt=%%a"
set "TIMESTAMP=%dt:~0,4%-%dt:~4,2%-%dt:~6,2%_%dt:~8,2%-%dt:~10,2%-%dt:~12,2%"
set "LOG_FILE=logs\scraper_%TIMESTAMP%.log"

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

REM Set production environment variables
set FLASK_ENV=production
set FLASK_DEBUG=0

REM Load additional environment variables from .env if exists
if exist ".env" (
    echo Loading environment variables from .env file...
    for /f "delims=" %%a in (.env) do (
        set "%%a"
    )
)

REM Check if the app is already running
netstat -an | findstr :5000 >nul
if not errorlevel 1 (
    echo WARNING: Port 5000 is already in use!
    echo The application might already be running.
    echo.
    choice /C YN /M "Do you want to stop it and start fresh?"
    if errorlevel 2 exit /b 0
    
    REM Stop existing process
    echo Stopping existing process...
    call stop.bat
    timeout /t 3 /nobreak >nul
)

REM Start the Flask application with logging
echo Starting Flask application in production mode...
echo Log file: %LOG_FILE%
echo.
echo Server will be available at: http://localhost:5000
echo ============================================
echo.

REM Create a wrapper script to handle logging
echo import sys > run_production.py
echo import logging >> run_production.py
echo from datetime import datetime >> run_production.py
echo. >> run_production.py
echo # Configure logging >> run_production.py
echo logging.basicConfig( >> run_production.py
echo     level=logging.INFO, >> run_production.py
echo     format='%%(asctime)s - %%(name)s - %%(levelname)s - %%(message)s', >> run_production.py
echo     handlers=[ >> run_production.py
echo         logging.FileHandler('%LOG_FILE%'), >> run_production.py
echo         logging.StreamHandler(sys.stdout) >> run_production.py
echo     ] >> run_production.py
echo ) >> run_production.py
echo. >> run_production.py
echo # Import and run the app >> run_production.py
echo from app import app >> run_production.py
echo. >> run_production.py
echo if __name__ == '__main__': >> run_production.py
echo     app.run(host='0.0.0.0', port=5000, debug=False) >> run_production.py

REM Run the application with logging
start "Media Scraper Server" /B cmd /c "python run_production.py >> %LOG_FILE% 2>&1"

REM Wait for the server to start
echo Waiting for server to start...
timeout /t 5 /nobreak >nul

REM Check if the server started successfully
netstat -an | findstr :5000 >nul
if errorlevel 1 (
    echo ERROR: Server failed to start!
    echo Please check the log file: %LOG_FILE%
    pause
    exit /b 1
)

echo ============================================
echo Application started successfully!
echo ============================================
echo.
echo Server is running at: http://localhost:5000
echo Log file: %LOG_FILE%
echo.
echo Opening browser...
start http://localhost:5000

echo.
echo Press any key to view live logs (Ctrl+C to exit log view)...
pause >nul

REM Show live logs
echo.
echo === LIVE LOGS ===
type %LOG_FILE%
echo.
echo === Press Ctrl+C to stop viewing logs ===
powershell -command "Get-Content '%LOG_FILE%' -Wait" 