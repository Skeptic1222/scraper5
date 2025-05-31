# PowerShell Start Script for Media Scraper
Write-Host "================================================" -ForegroundColor Green
Write-Host "    🚀 Media Scraper Server Starter (PowerShell)" -ForegroundColor Green  
Write-Host "================================================" -ForegroundColor Green
Write-Host ""

# Change to script directory
Set-Location $PSScriptRoot

Write-Host "🛑 Stopping any existing Python processes..." -ForegroundColor Yellow
# Stop existing Python processes
Get-Process -Name "python*" -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2

Write-Host "🧹 Cleaning up cache files..." -ForegroundColor Cyan
# Remove Python cache
if (Test-Path "__pycache__") {
    Remove-Item -Recurse -Force "__pycache__" -ErrorAction SilentlyContinue
}

Write-Host "🔍 Checking dependencies..." -ForegroundColor Cyan
# Check if dependencies are installed
$check = python -c "import flask, yt_dlp; print('OK')" 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Missing dependencies detected" -ForegroundColor Red
    Write-Host "💡 Installing requirements..." -ForegroundColor Yellow
    pip install -r requirements.txt
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Failed to install dependencies" -ForegroundColor Red
        Write-Host "💡 Try running: pip install flask yt-dlp waitress requests beautifulsoup4" -ForegroundColor Yellow
        Read-Host "Press Enter to continue..."
        exit 1
    }
} else {
    Write-Host "✅ All dependencies OK" -ForegroundColor Green
}

Write-Host "🚀 Starting Media Scraper Production Server..." -ForegroundColor Green
Write-Host "📍 Server will be available at: http://localhost:5000" -ForegroundColor Cyan
Write-Host "🛑 Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host "================================================" -ForegroundColor Green
Write-Host ""

# Start the server
try {
    python run_production.py
}
catch {
    Write-Host "❌ Error starting server: $_" -ForegroundColor Red
}

Write-Host ""
Write-Host "🛑 Server stopped" -ForegroundColor Yellow
Read-Host "Press Enter to continue..." 