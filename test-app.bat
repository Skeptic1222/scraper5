@echo off
echo ================================================
echo Enhanced Media Scraper - Application Test
echo Project Port Range: 3000-3099 (Using Port 3050)
echo ================================================
echo.

REM Test Python installation
echo [1/5] Testing Python installation...
python --version >nul 2>&1
if %ERRORLEVEL% equ 0 (
    echo √ Python is installed
    python --version
) else (
    echo × Python is not installed
    exit /b 1
)
echo.

REM Test virtual environment
echo [2/5] Testing virtual environment...
if exist "venv\Scripts\python.exe" (
    echo √ Virtual environment exists
) else (
    echo × Virtual environment not found
    echo   Run: python -m venv venv
)
echo.

REM Test port availability
echo [3/5] Testing port 3050 availability...
netstat -ano | findstr :3050 >nul
if %ERRORLEVEL% equ 0 (
    echo × Port 3050 is in use
    echo   Run stop-server.bat to free the port
) else (
    echo √ Port 3050 is available
)
echo.

REM Test .env configuration
echo [4/5] Testing environment configuration...
if exist ".env" (
    echo √ .env file exists
    findstr "FLASK_RUN_PORT=3050" .env >nul
    if %ERRORLEVEL% equ 0 (
        echo √ Port 3050 configured in .env
    ) else (
        echo × Port 3050 not configured in .env
    )
    findstr "GOOGLE_CLIENT_ID=" .env >nul
    if %ERRORLEVEL% equ 0 (
        echo √ Google OAuth configured
    ) else (
        echo × Google OAuth not configured
    )
) else (
    echo × .env file not found
    echo   Run build-server.bat to create it
)
echo.

REM Test web.config
echo [5/5] Testing IIS configuration...
if exist "web.config" (
    echo √ web.config exists
    findstr "localhost:3050" web.config >nul
    if %ERRORLEVEL% equ 0 (
        echo √ IIS proxy configured for port 3050
    ) else (
        echo × IIS proxy not configured for port 3050
    )
) else (
    echo × web.config not found
)
echo.

echo ================================================
echo Test Complete!
echo.
echo To start the application:
echo   1. Run: build-server.bat (first time only)
echo   2. Run: start-server.bat
echo   3. Access: http://localhost/scraper
echo.
echo To stop the application:
echo   Run: stop-server.bat
echo ================================================

pause