# PowerShell Stop Script for Media Scraper
Write-Host "================================================" -ForegroundColor Red
Write-Host "    🛑 Media Scraper Server Stopper (PowerShell)" -ForegroundColor Red
Write-Host "================================================" -ForegroundColor Red
Write-Host ""

# Change to script directory
Set-Location $PSScriptRoot

Write-Host "🔍 Finding and stopping Python processes..." -ForegroundColor Yellow
$pythonProcesses = Get-Process -Name "python*" -ErrorAction SilentlyContinue
if ($pythonProcesses) {
    Write-Host "🛑 Stopping Python processes..." -ForegroundColor Yellow
    $pythonProcesses | Stop-Process -Force -ErrorAction SilentlyContinue
    Write-Host "✅ Python processes stopped" -ForegroundColor Green
} else {
    Write-Host "ℹ️ No Python processes running" -ForegroundColor Cyan
}

Write-Host "🔍 Checking for processes using port 5000..." -ForegroundColor Yellow
$portProcesses = netstat -ano | Select-String ":5000"
if ($portProcesses) {
    Write-Host "🛑 Found processes using port 5000, attempting to stop..." -ForegroundColor Yellow
    foreach ($line in $portProcesses) {
        $processId = ($line -split '\s+')[-1]
        if ($processId -match '^\d+$') {
            try {
                Stop-Process -Id $processId -Force -ErrorAction Stop
                Write-Host "✅ Stopped process ID: $processId" -ForegroundColor Green
            }
            catch {
                Write-Host "⚠️ Could not stop process ID: $processId" -ForegroundColor Yellow
            }
        }
    }
} else {
    Write-Host "ℹ️ No processes found using port 5000" -ForegroundColor Cyan
}

Write-Host "🧹 Cleaning up cache files..." -ForegroundColor Cyan
if (Test-Path "__pycache__") {
    Remove-Item -Recurse -Force "__pycache__" -ErrorAction SilentlyContinue
    Write-Host "✅ Cleaned Python cache files" -ForegroundColor Green
}

Write-Host "⏳ Waiting for processes to fully terminate..." -ForegroundColor Yellow
Start-Sleep -Seconds 3

Write-Host ""
Write-Host "✅ All server processes stopped" -ForegroundColor Green
Write-Host "📍 You can now safely start the server again" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Red
Read-Host "Press Enter to continue..." 