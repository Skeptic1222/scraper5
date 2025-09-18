# Enhanced Media Scraper Service Management Script
# PowerShell script for managing the Windows service

param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("install", "uninstall", "start", "stop", "restart", "status")]
    [string]$Action
)

$ServiceName = "EnhancedMediaScraper"
$ServiceDisplayName = "Enhanced Media Scraper Service"
$ScriptPath = Split-Path -Parent $MyInvocation.MyCommand.Definition
$ServiceScript = Join-Path $ScriptPath "enhanced_media_scraper_service.py"
$PythonExe = "python"

function Write-Status {
    param([string]$Message, [string]$Level = "INFO")
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    switch ($Level) {
        "SUCCESS" { Write-Host "[$timestamp] ✅ $Message" -ForegroundColor Green }
        "ERROR"   { Write-Host "[$timestamp] ❌ $Message" -ForegroundColor Red }
        "WARN"    { Write-Host "[$timestamp] ⚠️  $Message" -ForegroundColor Yellow }
        default   { Write-Host "[$timestamp] ℹ️  $Message" -ForegroundColor Cyan }
    }
}

function Test-Prerequisites {
    Write-Status "Checking prerequisites..."
    
    # Check if running as administrator
    $currentUser = [Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()
    if (-not $currentUser.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
        Write-Status "This script must be run as Administrator" "ERROR"
        exit 1
    }
    
    # Check Python installation
    try {
        $pythonVersion = & $PythonExe --version 2>$null
        Write-Status "Python found: $pythonVersion"
    } catch {
        Write-Status "Python not found in PATH" "ERROR"
        exit 1
    }
    
    # Check pywin32 installation
    try {
        & $PythonExe -c "import win32service" 2>$null
        Write-Status "pywin32 module found"
    } catch {
        Write-Status "pywin32 module not found. Install with: pip install pywin32" "ERROR"
        exit 1
    }
    
    # Check service script exists
    if (-not (Test-Path $ServiceScript)) {
        Write-Status "Service script not found: $ServiceScript" "ERROR"
        exit 1
    }
    
    Write-Status "Prerequisites check passed" "SUCCESS"
}

function Install-Service {
    Write-Status "Installing $ServiceDisplayName..."
    try {
        & $PythonExe $ServiceScript install
        Write-Status "Service installed successfully" "SUCCESS"
        
        # Configure service for automatic startup
        Set-Service -Name $ServiceName -StartupType Automatic
        Write-Status "Service configured for automatic startup" "SUCCESS"
        
    } catch {
        Write-Status "Service installation failed: $($_.Exception.Message)" "ERROR"
        exit 1
    }
}

function Uninstall-Service {
    Write-Status "Uninstalling $ServiceDisplayName..."
    try {
        # Stop service if running
        $service = Get-Service -Name $ServiceName -ErrorAction SilentlyContinue
        if ($service -and $service.Status -eq "Running") {
            Write-Status "Stopping service before uninstall..."
            Stop-Service -Name $ServiceName -Force
            Start-Sleep 3
        }
        
        & $PythonExe $ServiceScript remove
        Write-Status "Service uninstalled successfully" "SUCCESS"
        
    } catch {
        Write-Status "Service uninstall failed: $($_.Exception.Message)" "ERROR"
        exit 1
    }
}

function Start-ServiceAction {
    Write-Status "Starting $ServiceDisplayName..."
    try {
        Start-Service -Name $ServiceName
        Start-Sleep 2
        $service = Get-Service -Name $ServiceName
        if ($service.Status -eq "Running") {
            Write-Status "Service started successfully" "SUCCESS"
        } else {
            Write-Status "Service failed to start properly" "ERROR"
        }
    } catch {
        Write-Status "Service start failed: $($_.Exception.Message)" "ERROR"
        exit 1
    }
}

function Stop-ServiceAction {
    Write-Status "Stopping $ServiceDisplayName..."
    try {
        Stop-Service -Name $ServiceName -Force
        Start-Sleep 2
        $service = Get-Service -Name $ServiceName
        if ($service.Status -eq "Stopped") {
            Write-Status "Service stopped successfully" "SUCCESS"
        } else {
            Write-Status "Service failed to stop properly" "WARN"
        }
    } catch {
        Write-Status "Service stop failed: $($_.Exception.Message)" "ERROR"
        exit 1
    }
}

function Restart-ServiceAction {
    Write-Status "Restarting $ServiceDisplayName..."
    Stop-ServiceAction
    Start-Sleep 3
    Start-ServiceAction
}

function Get-ServiceStatus {
    Write-Status "Checking $ServiceDisplayName status..."
    try {
        $service = Get-Service -Name $ServiceName -ErrorAction SilentlyContinue
        if ($service) {
            Write-Status "Service Status: $($service.Status)"
            Write-Status "Startup Type: $($service.StartType)"
            
            # Get process information if running
            if ($service.Status -eq "Running") {
                $processId = (Get-WmiObject -Class Win32_Service | Where-Object {$_.Name -eq $ServiceName}).ProcessId
                if ($processId) {
                    $process = Get-Process -Id $processId -ErrorAction SilentlyContinue
                    if ($process) {
                        Write-Status "Process ID: $processId"
                        Write-Status "Memory Usage: $([math]::Round($process.WorkingSet / 1MB, 2)) MB"
                        Write-Status "Start Time: $($process.StartTime)"
                    }
                }
            }
        } else {
            Write-Status "Service not found" "WARN"
        }
    } catch {
        Write-Status "Status check failed: $($_.Exception.Message)" "ERROR"
    }
}

# Main execution
Write-Status "Enhanced Media Scraper Service Manager"
Write-Status "Action: $Action"

# Test prerequisites for all actions except status
if ($Action -ne "status") {
    Test-Prerequisites
}

switch ($Action) {
    "install" {
        Install-Service
        Write-Status "To start the service, run: .\service_manager.ps1 start"
    }
    "uninstall" {
        Uninstall-Service
    }
    "start" {
        Start-ServiceAction
    }
    "stop" {
        Stop-ServiceAction
    }
    "restart" {
        Restart-ServiceAction
    }
    "status" {
        Get-ServiceStatus
    }
}

Write-Status "Operation completed"