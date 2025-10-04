# IIS Reverse Proxy Configuration Fix for Enhanced Media Scraper
# Run as Administrator

Write-Host "Enhanced Media Scraper - IIS Configuration Fix" -ForegroundColor Green
Write-Host "=============================================" -ForegroundColor Green

# Check if running as Administrator
if (-NOT ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator"))
{
    Write-Host "This script must be run as Administrator!" -ForegroundColor Red
    Write-Host "Please right-click and select 'Run as Administrator'" -ForegroundColor Yellow
    pause
    exit 1
}

# Check if IIS is installed
$iis = Get-WindowsFeature -Name Web-Server
if ($iis.InstallState -ne "Installed") {
    Write-Host "IIS is not installed!" -ForegroundColor Red
    exit 1
}

Write-Host "`n1. Checking required IIS modules..." -ForegroundColor Yellow

# Check URL Rewrite Module
$urlRewrite = Get-WebConfigurationProperty -PSPath "MACHINE/WEBROOT/APPHOST" -Filter "system.webServer/globalModules/add" -Name "name" | Where-Object {$_ -like "*RewriteModule*"}
if (-not $urlRewrite) {
    Write-Host "   - URL Rewrite Module: NOT INSTALLED" -ForegroundColor Red
    Write-Host "     Please download and install from: https://www.iis.net/downloads/microsoft/url-rewrite" -ForegroundColor Yellow
} else {
    Write-Host "   - URL Rewrite Module: OK" -ForegroundColor Green
}

# Check Application Request Routing (ARR)
$arr = Get-WebConfigurationProperty -PSPath "MACHINE/WEBROOT/APPHOST" -Filter "system.webServer/proxy" -Name "enabled" -ErrorAction SilentlyContinue
if (-not $arr -or $arr.Value -ne $true) {
    Write-Host "   - Application Request Routing: NOT ENABLED" -ForegroundColor Red
    Write-Host "     Enabling ARR proxy..." -ForegroundColor Yellow

    # Try to enable ARR
    try {
        Set-WebConfigurationProperty -PSPath "MACHINE/WEBROOT/APPHOST" -Filter "system.webServer/proxy" -Name "enabled" -Value $true
        Write-Host "     ARR proxy enabled successfully!" -ForegroundColor Green
    } catch {
        Write-Host "     Failed to enable ARR. Please install ARR from: https://www.iis.net/downloads/microsoft/application-request-routing" -ForegroundColor Red
    }
} else {
    Write-Host "   - Application Request Routing: OK" -ForegroundColor Green
}

Write-Host "`n2. Checking Flask backend..." -ForegroundColor Yellow

# Check if Flask is running on port 3050
$flask = Test-NetConnection -ComputerName localhost -Port 3050 -InformationLevel Quiet
if ($flask) {
    Write-Host "   - Flask server (port 3050): RUNNING" -ForegroundColor Green
} else {
    Write-Host "   - Flask server (port 3050): NOT RUNNING" -ForegroundColor Red
    Write-Host "     Please start Flask using start-flask-service.bat" -ForegroundColor Yellow
}

Write-Host "`n3. Configuring IIS Site..." -ForegroundColor Yellow

# Import IIS module
Import-Module WebAdministration

# Check if the scraper application exists
$app = Get-WebApplication -Site "Default Web Site" -Name "scraper" -ErrorAction SilentlyContinue

if (-not $app) {
    Write-Host "   - Creating /scraper application..." -ForegroundColor Yellow
    New-WebApplication -Site "Default Web Site" -Name "scraper" -PhysicalPath "C:\inetpub\wwwroot\scraper" -ApplicationPool "DefaultAppPool"
    Write-Host "   - Application created!" -ForegroundColor Green
} else {
    Write-Host "   - Application exists: OK" -ForegroundColor Green
}

Write-Host "`n4. Testing configuration..." -ForegroundColor Yellow

# Test direct Flask connection
$directTest = Invoke-WebRequest -Uri "http://localhost:3050/" -UseBasicParsing -TimeoutSec 5 -ErrorAction SilentlyContinue
if ($directTest.StatusCode -eq 200) {
    Write-Host "   - Direct Flask connection: OK" -ForegroundColor Green
} else {
    Write-Host "   - Direct Flask connection: FAILED" -ForegroundColor Red
}

# Test IIS proxy
$proxyTest = Invoke-WebRequest -Uri "http://localhost/scraper" -UseBasicParsing -TimeoutSec 5 -ErrorAction SilentlyContinue
if ($proxyTest.StatusCode -eq 200) {
    Write-Host "   - IIS proxy connection: OK" -ForegroundColor Green
} else {
    Write-Host "   - IIS proxy connection: FAILED" -ForegroundColor Red

    # Try to restart IIS
    Write-Host "`n   Restarting IIS..." -ForegroundColor Yellow
    iisreset /noforce

    Start-Sleep -Seconds 3

    # Test again
    $proxyTest2 = Invoke-WebRequest -Uri "http://localhost/scraper" -UseBasicParsing -TimeoutSec 5 -ErrorAction SilentlyContinue
    if ($proxyTest2.StatusCode -eq 200) {
        Write-Host "   - IIS proxy connection after restart: OK" -ForegroundColor Green
    } else {
        Write-Host "   - IIS proxy connection after restart: STILL FAILED" -ForegroundColor Red
        Write-Host "`n   Please check the Windows Event Viewer for IIS errors" -ForegroundColor Yellow
    }
}

Write-Host "`n=============================================" -ForegroundColor Green
Write-Host "Configuration check complete!" -ForegroundColor Green
Write-Host ""
Write-Host "If issues persist:" -ForegroundColor Yellow
Write-Host "1. Ensure Flask is running (use start-flask-service.bat)" -ForegroundColor White
Write-Host "2. Check Windows Firewall allows port 3050" -ForegroundColor White
Write-Host "3. Verify URL Rewrite and ARR modules are installed" -ForegroundColor White
Write-Host "4. Check Event Viewer > Windows Logs > Application for errors" -ForegroundColor White
Write-Host ""

pause