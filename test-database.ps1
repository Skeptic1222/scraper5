# Test SQL Server Express Connection for Enhanced Media Scraper
Write-Host "Testing SQL Server Express Connection..." -ForegroundColor Cyan
Write-Host "Project: Enhanced Media Scraper (Port 3050)" -ForegroundColor Yellow

# Test connection parameters
$server = "localhost\SQLEXPRESS"
$database = "Scraped"
$user = "dbuser"
$password = "Qwerty1234!"

# Test Windows Authentication first
Write-Host "`nTesting Windows Authentication..." -ForegroundColor Yellow
try {
    $connString = "Server=$server;Database=master;Integrated Security=true;"
    $conn = New-Object System.Data.SqlClient.SqlConnection($connString)
    $conn.Open()
    Write-Host "✓ Windows Authentication successful" -ForegroundColor Green
    $conn.Close()
} catch {
    Write-Host "✗ Windows Authentication failed: $_" -ForegroundColor Red
}

# Check if database exists
Write-Host "`nChecking if database 'Scraped' exists..." -ForegroundColor Yellow
try {
    $query = "SELECT name FROM sys.databases WHERE name = 'Scraped'"
    $cmd = sqlcmd -S $server -E -Q $query -h -1 2>&1
    if ($cmd -like "*Scraped*") {
        Write-Host "✓ Database 'Scraped' exists" -ForegroundColor Green
    } else {
        Write-Host "✗ Database 'Scraped' does not exist" -ForegroundColor Red
        Write-Host "  Run: sqlcmd -S $server -E -Q `"CREATE DATABASE Scraped`"" -ForegroundColor Yellow
    }
} catch {
    Write-Host "✗ Error checking database: $_" -ForegroundColor Red
}

# Test SQL Authentication
Write-Host "`nTesting SQL Authentication (dbuser)..." -ForegroundColor Yellow
try {
    $testQuery = "SELECT 1"
    $result = sqlcmd -S $server -U $user -P $password -d $database -Q $testQuery 2>&1
    if ($result -notlike "*Error*" -and $result -notlike "*failed*") {
        Write-Host "✓ SQL Authentication successful" -ForegroundColor Green
    } else {
        Write-Host "✗ SQL Authentication failed" -ForegroundColor Red
        Write-Host "  May need to create user: CREATE LOGIN dbuser WITH PASSWORD = 'Qwerty1234!'" -ForegroundColor Yellow
    }
} catch {
    Write-Host "✗ Error with SQL Authentication: $_" -ForegroundColor Red
}

Write-Host "`nDatabase connection string for .env file:" -ForegroundColor Cyan
Write-Host "DATABASE_URL=mssql+pyodbc://dbuser:Qwerty1234!@localhost\SQLEXPRESS/Scraped?driver=ODBC+Driver+17+for+SQL+Server" -ForegroundColor White