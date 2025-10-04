@echo off
echo ===================================
echo Enhanced Media Scraper Server Start
echo ===================================

REM Check if Python is installed
where python >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo Python is not installed! Please install Python 3.8 or higher.
    exit /b 1
)

REM Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Install dependencies if requirements.txt changed
echo Checking dependencies...
if exist requirements.txt (
    python -m pip install -r requirements.txt --quiet
)
if exist requirements-windows.txt (
    python -m pip install -r requirements-windows.txt --quiet
)

REM Set port for Scraper project (Flask dedicated port - no IIS conflict)
set FLASK_RUN_PORT=5050
set PORT=5050

REM Check if port 5050 is in use
netstat -ano | findstr :5050 >nul
if %ERRORLEVEL% equ 0 (
    echo Port 5050 is already in use. Stopping existing process...
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr :5050') do (
        taskkill /PID %%a /F
    )
    timeout /t 2 /nobreak >nul
)

REM Create logs directory if it doesn't exist
if not exist "logs" mkdir logs

REM Start Flask application
echo Starting Enhanced Media Scraper on port 5050 (Flask dedicated port - no IIS conflict)...
echo Server logs will be written to logs\server.log
python app.py > logs\server.log 2>&1

REM Keep the window open on error
if %ERRORLEVEL% neq 0 (
    echo Error starting server! Check logs\server.log for details.
    pause
    exit /b 1
)