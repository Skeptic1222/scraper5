@echo off
title Media Scraper - Restarting
echo ============================================
echo   Enhanced Media Scraper - Restarting
echo ============================================
echo.

REM First, stop the application if it's running
echo Step 1: Stopping the application...
echo ============================================

REM Try to find the process by window title
tasklist /FI "WINDOWTITLE eq Media Scraper Server*" 2>nul | findstr /i "python.exe cmd.exe" >nul
if not errorlevel 1 (
    echo Found Media Scraper process, stopping...
    taskkill /FI "WINDOWTITLE eq Media Scraper Server*" /F >nul 2>&1
    timeout /t 2 /nobreak >nul
    goto :start_app
)

REM Check if port 5000 is in use
netstat -an | findstr :5000 >nul
if not errorlevel 1 (
    echo Finding process using port 5000...
    
    REM Find the PID of the process using port 5000
    for /f "tokens=5" %%a in ('netstat -aon ^| findstr :5000 ^| findstr LISTENING') do (
        set PID=%%a
        goto :kill_process
    )
    
    :kill_process
    echo Stopping process with PID: %PID%
    taskkill /PID %PID% /F >nul 2>&1
    timeout /t 2 /nobreak >nul
) else (
    echo No application currently running on port 5000
)

:start_app
echo.
echo Step 2: Starting the application...
echo ============================================

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

REM Run the application
start "Media Scraper Server" /B cmd /c "python app.py"

REM Wait for the server to start
echo Waiting for server to start...
timeout /t 5 /nobreak >nul

REM Check if the server started successfully
netstat -an | findstr :5000 >nul
if errorlevel 1 (
    echo WARNING: Server may not have started properly
    echo Please check the application window for errors
) else (
    echo ============================================
    echo Application restarted successfully!
    echo ============================================
    echo.
    echo Opening browser...
    start http://localhost:5000
)

echo.
echo The application is running in a separate window.
echo Use stop.bat to stop the application.
pause 