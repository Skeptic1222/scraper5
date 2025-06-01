@echo off
title Media Scraper - Stopping
echo ============================================
echo   Enhanced Media Scraper - Stopping
echo ============================================
echo.

REM Find Python processes running app.py
echo Searching for running Media Scraper processes...

REM First, try to find the process by window title
tasklist /FI "WINDOWTITLE eq Media Scraper Server*" 2>nul | findstr /i "python.exe cmd.exe" >nul
if not errorlevel 1 (
    echo Found Media Scraper process by window title
    taskkill /FI "WINDOWTITLE eq Media Scraper Server*" /F >nul 2>&1
    echo Process terminated successfully!
    goto :check_port
)

REM Check if port 5000 is in use
netstat -an | findstr :5000 >nul
if errorlevel 1 (
    echo No application found running on port 5000
    echo The Media Scraper may not be running.
    pause
    exit /b 0
)

REM Find the PID of the process using port 5000
echo Finding process using port 5000...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :5000 ^| findstr LISTENING') do (
    set PID=%%a
    goto :found_pid
)

echo Could not find process ID for port 5000
pause
exit /b 1

:found_pid
echo Found process with PID: %PID%

REM Get process name
for /f "tokens=1" %%a in ('tasklist /FI "PID eq %PID%" ^| findstr %PID%') do (
    set PROCESS_NAME=%%a
)
echo Process name: %PROCESS_NAME%

REM Confirm before killing
echo.
choice /C YN /M "Do you want to stop this process?"
if errorlevel 2 (
    echo Operation cancelled.
    pause
    exit /b 0
)

REM Kill the process
echo Stopping the application...
taskkill /PID %PID% /F >nul 2>&1
if errorlevel 1 (
    echo ERROR: Failed to stop the process
    echo You may need to run this script as Administrator
    pause
    exit /b 1
)

:check_port
REM Wait a moment for the port to be released
timeout /t 2 /nobreak >nul

REM Verify the port is free
netstat -an | findstr :5000 >nul
if not errorlevel 1 (
    echo WARNING: Port 5000 is still in use
    echo The application may not have stopped completely
) else (
    echo ============================================
    echo Application stopped successfully!
    echo ============================================
)

echo.
pause 