@echo off
echo ================================================
echo     🛑 Media Scraper Server Stopper
echo ================================================
echo.

REM Change to the scraper directory
cd /d "%~dp0"

echo 🔍 Finding Python processes...
tasklist /fi "imagename eq python.exe" /fo table 2>nul | find "python.exe" >nul
if not errorlevel 1 (
    echo 🛑 Stopping Python processes...
    taskkill /f /im python.exe /t 2>nul
    if not errorlevel 1 (
        echo ✅ Python processes stopped
    ) else (
        echo ⚠️ No Python processes found to stop
    )
) else (
    echo ℹ️ No python.exe processes running
)

echo 🔍 Finding background Python processes...
tasklist /fi "imagename eq pythonw.exe" /fo table 2>nul | find "pythonw.exe" >nul
if not errorlevel 1 (
    echo 🛑 Stopping background Python processes...
    taskkill /f /im pythonw.exe /t 2>nul
    if not errorlevel 1 (
        echo ✅ Background Python processes stopped
    ) else (
        echo ⚠️ No background Python processes found to stop
    )
) else (
    echo ℹ️ No pythonw.exe processes running
)

echo 🔍 Checking for processes using port 5000...
netstat -ano | findstr :5000 >nul
if not errorlevel 1 (
    echo 🛑 Found processes using port 5000, attempting to stop...
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr :5000') do (
        echo Killing process ID: %%a
        taskkill /f /pid %%a 2>nul
    )
) else (
    echo ℹ️ No processes found using port 5000
)

echo 🧹 Cleaning up cache files...
REM Remove Python cache files from current directory
if exist __pycache__ (
    rmdir /s /q __pycache__ 2>nul
    echo ✅ Cleaned Python cache files
)

REM Wait a moment for all processes to fully terminate
echo ⏳ Waiting for processes to fully terminate...
timeout /t 3 /nobreak >nul

echo.
echo ✅ All server processes stopped
echo 📍 You can now safely start the server again
echo ================================================
pause 