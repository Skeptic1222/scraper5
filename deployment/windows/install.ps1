# Enhanced Media Scraper - Windows Enterprise Deployment Script
# For IIS + SQL Server Express deployment
# Run as Administrator

param(
    [string]$AppPath = "C:\inetpub\wwwroot\scraper",
    [string]$DatabaseName = "enhanced_media_scraper",
    [string]$PythonVersion = "3.12",
    [switch]$SkipDatabase,
    [switch]$SkipIIS,
    [switch]$Force
)

Write-Host "Enhanced Media Scraper - Windows Enterprise Deployment" -ForegroundColor Green
Write-Host "======================================================" -ForegroundColor Green

# Check if running as Administrator
if (-NOT ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Write-Error "This script must be run as Administrator"
    exit 1
}

# Function to check if command exists
function Test-Command($cmdname) {
    return [bool](Get-Command -Name $cmdname -ErrorAction SilentlyContinue)
}

# Step 1: Install Prerequisites
Write-Host "Step 1: Installing Prerequisites..." -ForegroundColor Yellow

# Check Python installation (detect existing Python first)
$pythonExe = $null
$pythonPaths = @(
    "C:\Program Files\Python$($PythonVersion.Replace('.', ''))\python.exe",
    "C:\Python$($PythonVersion.Replace('.', ''))\python.exe",
    (Get-Command python -ErrorAction SilentlyContinue)?.Source,
    (Get-Command python3 -ErrorAction SilentlyContinue)?.Source
)

foreach ($path in $pythonPaths) {
    if ($path -and (Test-Path $path)) {
        $version = & $path --version 2>$null
        if ($version -match "Python $PythonVersion") {
            $pythonExe = $path
            $pythonPath = Split-Path $path
            Write-Host "Found Python $PythonVersion at: $pythonExe" -ForegroundColor Green
            break
        }
    }
}

if (-not $pythonExe) {
    Write-Host "Installing Python $PythonVersion..." -ForegroundColor Blue
    # Use more reliable URL construction
    $majorMinor = $PythonVersion
    $pythonUrl = "https://www.python.org/ftp/python/$majorMinor.0/python-$majorMinor.0-amd64.exe"
    $pythonInstaller = "$env:TEMP\python-installer.exe"
    
    try {
        Invoke-WebRequest -Uri $pythonUrl -OutFile $pythonInstaller -UseBasicParsing
        Start-Process -FilePath $pythonInstaller -ArgumentList "/quiet", "InstallAllUsers=1", "PrependPath=1", "Include_test=0", "TargetDir=C:\Program Files\Python$($PythonVersion.Replace('.', ''))" -Wait
        Remove-Item $pythonInstaller -Force
        
        # Update paths after installation
        $pythonExe = "C:\Program Files\Python$($PythonVersion.Replace('.', ''))\python.exe"
        $pythonPath = "C:\Program Files\Python$($PythonVersion.Replace('.', ''))"
    } catch {
        Write-Error "Failed to install Python: $($_.Exception.Message)"
        exit 1
    }
}

# Install wfastcgi for IIS integration
Write-Host "Installing wfastcgi for IIS integration..." -ForegroundColor Blue
& $pythonExe -m pip install wfastcgi

# Check for ODBC Driver 18 for SQL Server (required for database connectivity)
Write-Host "Checking for ODBC Driver 18 for SQL Server..." -ForegroundColor Blue
$odbcDriver = Get-OdbcDriver -Name "ODBC Driver 18 for SQL Server" -ErrorAction SilentlyContinue
if (-not $odbcDriver) {
    Write-Warning "ODBC Driver 18 for SQL Server not found. Database connections will fail."
    Write-Host "Download from: https://learn.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server" -ForegroundColor Yellow
    Write-Host "Or install SQL Server Express which includes the driver." -ForegroundColor Yellow
    if (-not $Force) {
        $continue = Read-Host "Continue anyway? (y/N)"
        if ($continue -ne "y" -and $continue -ne "Y") {
            exit 1
        }
    }
}

# Configure FastCGI using standard wfastcgi-enable tool
$wfastcgiEnable = Join-Path (Split-Path $pythonExe) "Scripts\wfastcgi-enable.exe"
if (Test-Path $wfastcgiEnable) {
    Write-Host "Enabling FastCGI for Python..." -ForegroundColor Blue
    & $wfastcgiEnable
    
    # Configure environment variables for the application (without secrets)
    $appCmd = "C:\Windows\System32\inetsrv\appcmd.exe"
    if (Test-Path $appCmd) {
        # Find the FastCGI application registered by wfastcgi-enable
        $pythonDir = Split-Path $pythonExe
        $wfastcgiScript = Join-Path $pythonDir "Scripts\wfastcgi.py"
        
        Write-Host "Configuring FastCGI environment variables..." -ForegroundColor Blue
        & $appCmd set config /section:system.webServer/fastCgi /[fullPath='$pythonExe',arguments='$wfastcgiScript'].environmentVariables.+"[name='PYTHONPATH',value='$AppPath']"
        & $appCmd set config /section:system.webServer/fastCgi /[fullPath='$pythonExe',arguments='$wfastcgiScript'].environmentVariables.+"[name='WSGI_HANDLER',value='index.application']"
        & $appCmd set config /section:system.webServer/fastCgi /[fullPath='$pythonExe',arguments='$wfastcgiScript'].environmentVariables.+"[name='FLASK_ENV',value='production']"
        & $appCmd set config /section:system.webServer/fastCgi /[fullPath='$pythonExe',arguments='$wfastcgiScript'].environmentVariables.+"[name='APP_BASE',value='/']"
        
        Write-Host "FastCGI application configured. Set DATABASE_URL and SECRET_KEY manually via IIS Manager." -ForegroundColor Yellow
    }
} else {
    Write-Warning "wfastcgi-enable.exe not found. You may need to install wfastcgi package."
}

# Step 2: Configure IIS
if (-not $SkipIIS) {
    Write-Host "Step 2: Configuring IIS..." -ForegroundColor Yellow
    
    # Enable IIS features
    $features = @(
        "IIS-WebServerRole",
        "IIS-WebServer",
        "IIS-CommonHttpFeatures",
        "IIS-HttpErrors",
        "IIS-HttpLogging",
        "IIS-RequestFiltering",
        "IIS-StaticContent",
        "IIS-DefaultDocument",
        "IIS-CGI",
        "IIS-ISAPIExtensions",
        "IIS-ISAPIFilter",
        "IIS-HttpCompressionStatic",
        "IIS-HttpCompressionDynamic",
        "IIS-HttpRedirect",
        "IIS-IISCertificateMappingAuthentication",
        "IIS-URLAuthorization",
        "IIS-RequestFiltering",
        "IIS-CustomLogging",
        "IIS-BasicAuthentication",
        "IIS-WindowsAuthentication"
    )
    
    foreach ($feature in $features) {
        Write-Host "Enabling $feature..." -ForegroundColor Blue
        Enable-WindowsOptionalFeature -Online -FeatureName $feature -All -NoRestart
    }
    
    # Import WebAdministration module
    Import-Module WebAdministration
    
    # Create application directory
    if (-not (Test-Path $AppPath)) {
        New-Item -ItemType Directory -Path $AppPath -Force
    }
    
    # Set secure permissions on application directory (least privilege)
    $acl = Get-Acl $AppPath
    # Remove inherited permissions and set specific ones
    $acl.SetAccessRuleProtection($true, $false)
    
    # Grant minimal required permissions
    $accessRule = New-Object System.Security.AccessControl.FileSystemAccessRule("IIS_IUSRS", "ReadAndExecute", "ContainerInherit,ObjectInherit", "None", "Allow")
    $acl.SetAccessRule($accessRule)
    
    # Create and set write permissions for uploads and downloads directories
    $uploadPath = Join-Path $AppPath "uploads"
    $downloadPath = Join-Path $AppPath "downloads"
    $logsPath = Join-Path $AppPath "logs"
    
    New-Item -ItemType Directory -Path $uploadPath -Force -ErrorAction SilentlyContinue
    New-Item -ItemType Directory -Path $downloadPath -Force -ErrorAction SilentlyContinue
    New-Item -ItemType Directory -Path $logsPath -Force -ErrorAction SilentlyContinue
    
    # Grant write permissions to specific directories that need it
    foreach ($dir in @($uploadPath, $downloadPath, $logsPath)) {
        if (Test-Path $dir) {
            $dirAcl = Get-Acl $dir
            $writeRule = New-Object System.Security.AccessControl.FileSystemAccessRule("IIS_IUSRS", "Modify", "ContainerInherit,ObjectInherit", "None", "Allow")
            $dirAcl.SetAccessRule($writeRule)
            Set-Acl -Path $dir -AclObject $dirAcl
        }
    }
    $accessRule = New-Object System.Security.AccessControl.FileSystemAccessRule("IUSR", "Read", "ContainerInherit,ObjectInherit", "None", "Allow")
    $acl.SetAccessRule($accessRule)
    
    # Grant write access only to logs and temp directories
    $logsPath = Join-Path $AppPath "logs"
    if (-not (Test-Path $logsPath)) { New-Item -ItemType Directory -Path $logsPath -Force }
    $logsAcl = Get-Acl $logsPath
    $logsAccessRule = New-Object System.Security.AccessControl.FileSystemAccessRule("IIS_IUSRS", "Modify", "ContainerInherit,ObjectInherit", "None", "Allow")
    $logsAcl.SetAccessRule($logsAccessRule)
    Set-Acl -Path $logsPath -AclObject $logsAcl
    
    Set-Acl -Path $AppPath -AclObject $acl
    
    # Create Application Pool
    $poolName = "EnhancedMediaScraperPool"
    if (Get-IISAppPool -Name $poolName -ErrorAction SilentlyContinue) {
        Remove-WebAppPool -Name $poolName
    }
    New-WebAppPool -Name $poolName
    Set-ItemProperty -Path "IIS:\AppPools\$poolName" -Name processModel.identityType -Value ApplicationPoolIdentity
    Set-ItemProperty -Path "IIS:\AppPools\$poolName" -Name recycling.periodicRestart.time -Value "00:00:00"
    Set-ItemProperty -Path "IIS:\AppPools\$poolName" -Name processModel.maxProcesses -Value 1
    
    # Create IIS Site
    $siteName = "EnhancedMediaScraper"
    if (Get-Website -Name $siteName -ErrorAction SilentlyContinue) {
        Remove-Website -Name $siteName
    }
    New-Website -Name $siteName -Port 80 -PhysicalPath $AppPath -ApplicationPool $poolName
}

# Step 3: Configure SQL Server Express
if (-not $SkipDatabase) {
    Write-Host "Step 3: Configuring SQL Server Express..." -ForegroundColor Yellow
    
    # Check if SQL Server Express is installed
    $sqlService = Get-Service -Name "MSSQL`$SQLEXPRESS" -ErrorAction SilentlyContinue
    if (-not $sqlService) {
        Write-Host "SQL Server Express not found. Please install SQL Server Express first." -ForegroundColor Red
        Write-Host "Download from: https://www.microsoft.com/en-us/sql-server/sql-server-downloads" -ForegroundColor Yellow
        return
    }
    
    # Start SQL Server Express service
    if ($sqlService.Status -ne "Running") {
        Start-Service -Name "MSSQL`$SQLEXPRESS"
    }
    
    # Create database
    $createDbScript = @"
USE master;
IF NOT EXISTS (SELECT name FROM sys.databases WHERE name = '$DatabaseName')
BEGIN
    CREATE DATABASE [$DatabaseName];
END
"@
    
    $sqlcmdPath = "${env:ProgramFiles}\Microsoft SQL Server\Client SDK\ODBC\170\Tools\Binn\sqlcmd.exe"
    if (-not (Test-Path $sqlcmdPath)) {
        $sqlcmdPath = "${env:ProgramFiles(x86)}\Microsoft SQL Server\Client SDK\ODBC\170\Tools\Binn\sqlcmd.exe"
    }
    
    if (Test-Path $sqlcmdPath) {
        Write-Host "Creating database '$DatabaseName'..." -ForegroundColor Blue
        & $sqlcmdPath -S ".\SQLEXPRESS" -E -Q $createDbScript
    } else {
        Write-Host "sqlcmd not found. Please install SQL Server Command Line Utilities." -ForegroundColor Red
    }
}

# Step 4: Deploy Application
Write-Host "Step 4: Deploying Application..." -ForegroundColor Yellow

# Copy application files
if (Test-Path "app.py") {
    Write-Host "Copying application files..." -ForegroundColor Blue
    Copy-Item -Path "." -Destination $AppPath -Recurse -Force -Exclude @("deployment", ".git", "__pycache__", "*.pyc", ".env")
    
    # Copy enterprise web.config
    if (Test-Path "web.config.enterprise") {
        Copy-Item -Path "web.config.enterprise" -Destination "$AppPath\web.config" -Force
    }
    
    # Create required directories
    $dirs = @("logs", "uploads", "downloads", "static\error")
    foreach ($dir in $dirs) {
        $fullPath = Join-Path $AppPath $dir
        if (-not (Test-Path $fullPath)) {
            New-Item -ItemType Directory -Path $fullPath -Force
        }
    }
    
    # Create error pages
    $error404 = @"
<!DOCTYPE html>
<html>
<head><title>Page Not Found</title></head>
<body><h1>404 - Page Not Found</h1><p>The requested page could not be found.</p></body>
</html>
"@
    
    $error500 = @"
<!DOCTYPE html>
<html>
<head><title>Server Error</title></head>
<body><h1>500 - Server Error</h1><p>An internal server error occurred.</p></body>
</html>
"@
    
    $error404 | Out-File -FilePath "$AppPath\static\error\404.html" -Encoding UTF8
    $error500 | Out-File -FilePath "$AppPath\static\error\500.html" -Encoding UTF8
}

# Step 5: Install Python Dependencies
Write-Host "Step 5: Installing Python Dependencies..." -ForegroundColor Yellow

if (Test-Path "$AppPath\requirements.txt") {
    Set-Location $AppPath
    
    # Handle Windows-specific dependency installation issues
    Write-Host "Installing critical packages individually (Windows compatibility)..." -ForegroundColor Blue
    
    $criticalPackages = @("flask", "sqlalchemy", "pyodbc", "flask-sqlalchemy", "flask-login")
    foreach ($package in $criticalPackages) {
        Write-Host "Installing $package..." -ForegroundColor Blue
        & $pythonExe -m pip install $package --force-reinstall
        Start-Sleep -Seconds 2
    }
    
    # Install remaining packages
    Write-Host "Installing remaining packages..." -ForegroundColor Blue
    & $pythonExe -m pip install -r requirements.txt --force-reinstall
}

# Step 6: Create Environment Configuration
Write-Host "Step 6: Creating Environment Configuration..." -ForegroundColor Yellow

$envContent = @"
# Enhanced Media Scraper - Production Configuration
FLASK_ENV=production
FLASK_DEBUG=False

# Database Configuration (SQL Server Express) - SECURE
# Set DATABASE_URL via IIS Configuration Editor for production security
# DATABASE_URL=mssql+pyodbc://./\SQLEXPRESS/$DatabaseName?driver=ODBC Driver 18 for SQL Server&trusted_connection=yes&Encrypt=yes&TrustServerCertificate=no

# Application Settings
SECRET_KEY=$(New-Guid).ToString().Replace('-', '')
APP_BASE=/scraper
SESSION_COOKIE_SECURE=true
SESSION_COOKIE_HTTPONLY=true

# Logging
LOG_LEVEL=INFO
LOG_FILE=C:\inetpub\logs\scraper\app.log

# Google OAuth (Configure these)
GOOGLE_CLIENT_ID=your-google-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-google-client-secret

# OpenAI API (Configure this)
OPENAI_API_KEY=your-openai-api-key

# Admin Configuration
ADMIN_EMAIL=admin@yourcompany.com
"@

$envContent | Out-File -FilePath "$AppPath\.env" -Encoding UTF8

# Step 7: Initialize Database
Write-Host "Step 7: Initializing Database..." -ForegroundColor Yellow

if (Test-Path "$AppPath\init_db.py") {
    Set-Location $AppPath
    & $pythonExe init_db.py
}

# Windows Service files exist for development/testing but are NOT used in production
# Production deployment uses IIS FastCGI only - no Windows Service required

# Step 9: Test Installation
Write-Host "Step 9: Testing Installation..." -ForegroundColor Yellow

try {
    Set-Location $AppPath
    $testResult = & "$pythonPath\python.exe" -c "import app; print('Application imports successfully')"
    Write-Host $testResult -ForegroundColor Green
} catch {
    Write-Host "Application test failed: $_" -ForegroundColor Red
}

# Final Instructions
Write-Host ""
Write-Host "Deployment Complete!" -ForegroundColor Green
Write-Host "==================" -ForegroundColor Green
Write-Host "1. Configure Google OAuth credentials in $AppPath\.env"
Write-Host "2. Configure OpenAI API key in $AppPath\.env"
Write-Host "3. Test the application by visiting http://localhost"
Write-Host "4. Check logs in C:\inetpub\logs\scraper\"
Write-Host ""
Write-Host "Troubleshooting:"
Write-Host "- Check IIS Application Pool is running"
Write-Host "- Check SQL Server Express service is running"
Write-Host "- Check file permissions on $AppPath"
Write-Host "- Check logs for errors"
Write-Host ""