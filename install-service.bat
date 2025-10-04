@echo off
REM ============================================================
REM Flask Media Scraper - Windows Service Installation
REM Run this file as Administrator!
REM ============================================================

echo.
echo ====================================================
echo Flask Media Scraper - Service Installation
echo ====================================================
echo.

REM Check for admin privileges
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo ERROR: This script requires Administrator privileges!
    echo Please right-click and select "Run as administrator"
    echo.
    pause
    exit /b 1
)

echo [1/7] Checking NSSM installation...
if not exist "C:\tools\nssm-2.24\win64\nssm.exe" (
    echo   Extracting NSSM...
    powershell -Command "Expand-Archive -Path 'C:\tools\nssm.zip' -DestinationPath 'C:\tools' -Force"
)
if not exist "C:\tools\nssm-2.24\win64\nssm.exe" (
    echo   ERROR: NSSM not found!
    pause
    exit /b 1
)
echo   OK - NSSM found

echo.
echo [2/7] Stopping existing Python processes...
taskkill /F /IM python.exe >nul 2>&1
timeout /t 2 /nobreak >nul
echo   OK - Processes stopped

echo.
echo [3/7] Removing existing service (if any)...
sc query FlaskMediaScraper >nul 2>&1
if %errorLevel% equ 0 (
    C:\tools\nssm-2.24\win64\nssm.exe stop FlaskMediaScraper
    timeout /t 3 /nobreak >nul
    C:\tools\nssm-2.24\win64\nssm.exe remove FlaskMediaScraper confirm
    timeout /t 2 /nobreak >nul
    echo   OK - Removed existing service
) else (
    echo   OK - No existing service
)

echo.
echo [4/7] Creating log directory...
if not exist "C:\logs\services\FlaskMediaScraper" mkdir "C:\logs\services\FlaskMediaScraper"
echo   OK - Created C:\logs\services\FlaskMediaScraper

echo.
echo [5/7] Installing Windows Service...
C:\tools\nssm-2.24\win64\nssm.exe install FlaskMediaScraper "C:\Python311\python.exe" app.py
C:\tools\nssm-2.24\win64\nssm.exe set FlaskMediaScraper AppDirectory "C:\inetpub\wwwroot\scraper"
C:\tools\nssm-2.24\win64\nssm.exe set FlaskMediaScraper DisplayName "Flask Media Scraper Service"
C:\tools\nssm-2.24\win64\nssm.exe set FlaskMediaScraper Description "Enhanced Media Scraper v3.0 - Auto-starts on boot"
C:\tools\nssm-2.24\win64\nssm.exe set FlaskMediaScraper Start SERVICE_AUTO_START
C:\tools\nssm-2.24\win64\nssm.exe set FlaskMediaScraper AppStdout "C:\logs\services\FlaskMediaScraper\stdout.log"
C:\tools\nssm-2.24\win64\nssm.exe set FlaskMediaScraper AppStderr "C:\logs\services\FlaskMediaScraper\stderr.log"
C:\tools\nssm-2.24\win64\nssm.exe set FlaskMediaScraper AppRotateFiles 1
C:\tools\nssm-2.24\win64\nssm.exe set FlaskMediaScraper AppRotateBytes 10485760
C:\tools\nssm-2.24\win64\nssm.exe set FlaskMediaScraper AppExit Default Restart
C:\tools\nssm-2.24\win64\nssm.exe set FlaskMediaScraper AppThrottle 5000
C:\tools\nssm-2.24\win64\nssm.exe set FlaskMediaScraper AppRestartDelay 10000
C:\tools\nssm-2.24\win64\nssm.exe set FlaskMediaScraper AppNoConsole 1
echo   OK - Service configured

echo.
echo [6/7] Starting service...
C:\tools\nssm-2.24\win64\nssm.exe start FlaskMediaScraper
timeout /t 5 /nobreak >nul
echo   OK - Service started

echo.
echo [7/7] Verifying service status...
sc query FlaskMediaScraper | findstr "STATE"
echo.

echo ====================================================
echo Installation Complete!
echo ====================================================
echo.
echo Service Name: FlaskMediaScraper
echo Startup Type: Automatic
echo Logs: C:\logs\services\FlaskMediaScraper
echo.
echo The Flask app will now auto-start on system boot!
echo.
echo Useful Commands:
echo   View status:  sc query FlaskMediaScraper
echo   Stop service: sc stop FlaskMediaScraper
echo   Start service: sc start FlaskMediaScraper
echo   View logs: notepad C:\logs\services\FlaskMediaScraper\stdout.log
echo.
pause
