#Requires -RunAsAdministrator
<#
.SYNOPSIS
    Setup auto-start for Flask Media Scraper using Windows Service
.DESCRIPTION
    Installs NSSM and creates a Windows Service that auto-starts on boot
#>

Write-Host "=== Flask Media Scraper Auto-Start Setup ===" -ForegroundColor Cyan
Write-Host ""

# Configuration
$ServiceName = "FlaskMediaScraper"
$AppDir = "C:\inetpub\wwwroot\scraper"
$PythonExe = "C:\Python311\python.exe"
$AppScript = "app.py"
$LogDir = "C:\logs\services\FlaskMediaScraper"
$NssmPath = "C:\tools\nssm-2.24\win64\nssm.exe"

# Step 1: Verify NSSM installation
Write-Host "[1/6] Checking NSSM installation..." -ForegroundColor Yellow
if (-not (Test-Path $NssmPath)) {
    Write-Host "  NSSM not found. Installing..." -ForegroundColor Yellow

    $NssmZip = "C:\tools\nssm.zip"
    $NssmExtract = "C:\tools"

    if (-not (Test-Path $NssmZip)) {
        Write-Host "  ERROR: NSSM zip not found at $NssmZip" -ForegroundColor Red
        Write-Host "  Please download from https://nssm.cc/release/nssm-2.24.zip" -ForegroundColor Red
        exit 1
    }

    # Extract
    Write-Host "  Extracting NSSM..." -ForegroundColor Yellow
    Expand-Archive -Path $NssmZip -DestinationPath $NssmExtract -Force

    if (-not (Test-Path $NssmPath)) {
        Write-Host "  ERROR: NSSM extraction failed" -ForegroundColor Red
        exit 1
    }
}

Write-Host "  ✓ NSSM found at: $NssmPath" -ForegroundColor Green

# Step 2: Stop existing Python processes
Write-Host "`n[2/6] Stopping existing Flask processes..." -ForegroundColor Yellow
$pythonProcs = Get-Process -Name python -ErrorAction SilentlyContinue
if ($pythonProcs) {
    $pythonProcs | Stop-Process -Force
    Write-Host "  ✓ Stopped $($pythonProcs.Count) Python process(es)" -ForegroundColor Green
} else {
    Write-Host "  No Python processes running" -ForegroundColor Gray
}

# Step 3: Remove existing service if present
Write-Host "`n[3/6] Checking for existing service..." -ForegroundColor Yellow
$existingService = Get-Service -Name $ServiceName -ErrorAction SilentlyContinue
if ($existingService) {
    Write-Host "  Removing existing service..." -ForegroundColor Yellow
    & $NssmPath stop $ServiceName
    Start-Sleep -Seconds 2
    & $NssmPath remove $ServiceName confirm
    Start-Sleep -Seconds 2
    Write-Host "  ✓ Existing service removed" -ForegroundColor Green
}

# Step 4: Create log directory
Write-Host "`n[4/6] Creating log directory..." -ForegroundColor Yellow
New-Item -ItemType Directory -Path $LogDir -Force | Out-Null
Write-Host "  ✓ Log directory: $LogDir" -ForegroundColor Green

# Step 5: Install and configure service
Write-Host "`n[5/6] Installing Windows Service..." -ForegroundColor Yellow

& $NssmPath install $ServiceName $PythonExe $AppScript
& $NssmPath set $ServiceName AppDirectory $AppDir
& $NssmPath set $ServiceName DisplayName "Flask Media Scraper Service"
& $NssmPath set $ServiceName Description "Enhanced Media Scraper v3.0 - Auto-starts on boot with crash recovery"
& $NssmPath set $ServiceName Start SERVICE_AUTO_START

# Logging with rotation
& $NssmPath set $ServiceName AppStdout "$LogDir\stdout.log"
& $NssmPath set $ServiceName AppStderr "$LogDir\stderr.log"
& $NssmPath set $ServiceName AppRotateFiles 1
& $NssmPath set $ServiceName AppRotateOnline 1
& $NssmPath set $ServiceName AppRotateBytes 10485760  # 10MB

# Environment
& $NssmPath set $ServiceName AppEnvironmentExtra "FLASK_ENV=production"

# Recovery settings
& $NssmPath set $ServiceName AppExit Default Restart
& $NssmPath set $ServiceName AppThrottle 5000       # Wait 5s before restart
& $NssmPath set $ServiceName AppRestartDelay 10000   # 10s delay after failure

# No console window
& $NssmPath set $ServiceName AppNoConsole 1

Write-Host "  ✓ Service installed and configured" -ForegroundColor Green

# Step 6: Start service and verify
Write-Host "`n[6/6] Starting service..." -ForegroundColor Yellow
& $NssmPath start $ServiceName
Start-Sleep -Seconds 5

# Verify service status
$service = Get-Service -Name $ServiceName -ErrorAction SilentlyContinue
if ($service -and $service.Status -eq "Running") {
    Write-Host "  ✓ Service is RUNNING" -ForegroundColor Green
} else {
    Write-Host "  ✗ Service failed to start" -ForegroundColor Red
    Write-Host "  Check logs at: $LogDir" -ForegroundColor Yellow
    exit 1
}

# Test HTTP endpoint
Write-Host "`n[Testing] HTTP endpoint..." -ForegroundColor Yellow
Start-Sleep -Seconds 3
try {
    $response = Invoke-WebRequest -Uri "http://localhost/scraper" -UseBasicParsing -TimeoutSec 10 -ErrorAction Stop
    Write-Host "  ✓ HTTP Response: $($response.StatusCode)" -ForegroundColor Green
} catch {
    Write-Host "  ✗ HTTP test failed: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "  Service may still be starting up - check logs" -ForegroundColor Yellow
}

# Summary
Write-Host "`n=== Setup Complete ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "Service Name    : $ServiceName" -ForegroundColor White
Write-Host "Status          : $($service.Status)" -ForegroundColor Green
Write-Host "Startup Type    : Automatic" -ForegroundColor White
Write-Host "Logs            : $LogDir" -ForegroundColor White
Write-Host ""
Write-Host "Useful Commands:" -ForegroundColor Yellow
Write-Host "  View status   : sc query $ServiceName" -ForegroundColor Gray
Write-Host "  Stop service  : sc stop $ServiceName" -ForegroundColor Gray
Write-Host "  Start service : sc start $ServiceName" -ForegroundColor Gray
Write-Host "  View logs     : Get-Content '$LogDir\stdout.log' -Tail 50" -ForegroundColor Gray
Write-Host "  Remove service: nssm remove $ServiceName confirm" -ForegroundColor Gray
Write-Host ""
Write-Host "✓ Flask app will now auto-start on system boot!" -ForegroundColor Green
