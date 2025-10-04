@echo off
echo ===================================
echo Enhanced Media Scraper Server Build
echo ===================================

REM Check if Python is installed
where python >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo Python is not installed! Please install Python 3.8 or higher.
    exit /b 1
)

REM Create and activate virtual environment
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Install all dependencies
echo Installing dependencies...
python -m pip install --upgrade pip

REM Install core dependencies
echo Installing core Python packages...
python -m pip install -r requirements.txt

REM Install Windows-specific dependencies if file exists
if exist "requirements-windows.txt" (
    echo Installing Windows-specific packages...
    python -m pip install -r requirements-windows.txt
)

REM Install ODBC driver for SQL Server if needed
python -m pip install pyodbc

REM Run database setup
echo Setting up database...
python init_db_simple.py

REM Create required directories
if not exist "logs" mkdir logs
if not exist "instance" mkdir instance
if not exist "uploads" mkdir uploads

REM Generate .env file if it doesn't exist
if not exist ".env" (
    echo Generating .env file...
    echo FLASK_ENV=production> .env
    echo DEBUG=false>> .env
    echo SECRET_KEY=%RANDOM%%RANDOM%%RANDOM%%RANDOM%>> .env
    echo FLASK_RUN_PORT=3050>> .env
    echo PORT=3050>> .env
    echo DATABASE_URL=mssql+pyodbc://dbuser:Qwerty1234!@localhost\SQLEXPRESS/Scraped?driver=ODBC+Driver+17+for+SQL+Server>> .env
    echo ADMIN_EMAIL=sop1973@gmail.com>> .env
    echo GOOGLE_CLIENT_ID=YOUR_GOOGLE_CLIENT_ID_HERE>> .env
    echo GOOGLE_CLIENT_SECRET=YOUR_GOOGLE_CLIENT_SECRET_HERE>> .env
    echo GOOGLE_REDIRECT_URL=/scraper/auth/google/callback>> .env
)

REM Clean up compiled Python files
echo Cleaning up compiled files...
del /s /q *.pyc 2>nul
del /s /q __pycache__\*.* 2>nul

echo Build completed successfully!
echo.
echo Project: Enhanced Media Scraper
echo Port Range: 3000-3099 (Using port 3050)
echo.
echo You can now run start-server.bat to start the application.

REM Keep the window open on error
if %ERRORLEVEL% neq 0 (
    echo Build failed! Please check the error messages above.
    pause
    exit /b 1
)

timeout /t 5 /nobreak >nul