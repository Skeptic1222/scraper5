@echo off
echo ================================================
echo     🚀 Media Scraper Server Starter
echo ================================================
echo.

REM Change to the scraper directory (ensure we're in the right place)
cd /d "%~dp0"

echo 🛑 Stopping any existing Python processes...
REM Kill any existing Python processes related to this project
taskkill /f /im python.exe 2>nul
taskkill /f /im pythonw.exe 2>nul
REM Wait a moment for processes to fully terminate
timeout /t 2 /nobreak >nul

echo 🧹 Cleaning up cache files...
REM Remove Python cache files
if exist __pycache__ (
    rmdir /s /q __pycache__ 2>nul
)

echo 🔍 Checking dependencies...
python -c "import flask, yt_dlp; print('✅ All dependencies OK')" 2>nul
if errorlevel 1 (
    echo ❌ Missing dependencies detected
    echo 💡 Installing requirements...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ❌ Failed to install dependencies
        echo 💡 Try running: pip install flask yt-dlp waitress requests beautifulsoup4
        echo 📋 Or check if virtual environment is activated
        pause
        exit /b 1
    )
)

echo 🚀 Starting Media Scraper Production Server...
echo 📍 Server will be available at: http://localhost:5000
echo 🛑 Press Ctrl+C to stop the server
echo ================================================
echo.

REM Start the production server
python run_production.py

echo.
echo 🛑 Server stopped
pause 