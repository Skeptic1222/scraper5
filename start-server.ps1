# Enhanced Media Scraper - Start Server PowerShell Script
Write-Host "===================================" -ForegroundColor Cyan
Write-Host "Enhanced Media Scraper Server Start" -ForegroundColor Cyan
Write-Host "===================================" -ForegroundColor Cyan

# Set working directory
Set-Location -Path "C:\inetpub\wwwroot\scraper"

# Check if Python is installed
$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) {
    Write-Host "Python is not installed! Please install Python 3.8 or higher." -ForegroundColor Red
    exit 1
}

# Check if virtual environment exists
if (-not (Test-Path "venv")) {
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    python -m venv venv
}

# Activate virtual environment
& .\venv\Scripts\Activate.ps1

# Check if port 8080 is in use
$port8080 = Get-NetTCPConnection -LocalPort 8080 -ErrorAction SilentlyContinue
if ($port8080) {
    Write-Host "Port 8080 is already in use. Stopping existing process..." -ForegroundColor Yellow
    $port8080 | ForEach-Object {
        Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue
    }
    Start-Sleep -Seconds 2
}

# Create logs directory if it doesn't exist
if (-not (Test-Path "logs")) {
    New-Item -ItemType Directory -Path "logs" | Out-Null
}

# Start Flask application
Write-Host "Starting Flask application on port 8080..." -ForegroundColor Green
Write-Host "Access the application at: http://localhost/scraper" -ForegroundColor Cyan
Write-Host "Server logs: logs\server.log" -ForegroundColor Gray

# Start in background
Start-Process -FilePath "python" -ArgumentList "app.py" -WorkingDirectory "C:\inetpub\wwwroot\scraper" -WindowStyle Hidden -PassThru

Start-Sleep -Seconds 3

# Verify it started
$port8080 = Get-NetTCPConnection -LocalPort 8080 -ErrorAction SilentlyContinue
if ($port8080) {
    Write-Host "✅ Flask application started successfully on port 8080!" -ForegroundColor Green
} else {
    Write-Host "❌ Failed to start Flask application" -ForegroundColor Red
    exit 1
}