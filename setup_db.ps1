# SQL Server Database Setup Script
$server = "localhost\SQLEXPRESS"
$database = "Scraped"

Write-Host "Setting up SQL Server database..." -ForegroundColor Cyan

# Create the database
$query = @"
IF NOT EXISTS (SELECT * FROM sys.databases WHERE name = 'Scraped')
BEGIN
    CREATE DATABASE [Scraped]
    PRINT 'Database [Scraped] created successfully'
END
ELSE
BEGIN
    PRINT 'Database [Scraped] already exists'
END
"@

try {
    sqlcmd -S $server -E -Q $query
    Write-Host "Database creation check complete" -ForegroundColor Green
} catch {
    Write-Host "Error creating database: $_" -ForegroundColor Red
}

# Create login and user
$loginQuery = @"
USE master;
IF NOT EXISTS (SELECT * FROM sys.server_principals WHERE name = 'dbuser')
BEGIN
    CREATE LOGIN [dbuser] WITH PASSWORD = 'Qwerty1234!', 
    DEFAULT_DATABASE = [master],
    CHECK_EXPIRATION = OFF,
    CHECK_POLICY = OFF;
    PRINT 'Login [dbuser] created successfully';
END
ELSE
BEGIN
    ALTER LOGIN [dbuser] WITH PASSWORD = 'Qwerty1234!';
    PRINT 'Login [dbuser] password updated';
END
ALTER LOGIN [dbuser] ENABLE;
"@

try {
    sqlcmd -S $server -E -Q $loginQuery
    Write-Host "Login setup complete" -ForegroundColor Green
} catch {
    Write-Host "Error setting up login: $_" -ForegroundColor Red
}

# Grant permissions
$permQuery = @"
USE [Scraped];
IF NOT EXISTS (SELECT * FROM sys.database_principals WHERE name = 'dbuser')
BEGIN
    CREATE USER [dbuser] FOR LOGIN [dbuser];
END
ALTER ROLE db_owner ADD MEMBER [dbuser];
PRINT 'Permissions granted to dbuser';
"@

try {
    sqlcmd -S $server -E -Q $permQuery
    Write-Host "Permissions setup complete" -ForegroundColor Green
} catch {
    Write-Host "Error setting up permissions: $_" -ForegroundColor Red
}

Write-Host "`nDatabase setup complete!" -ForegroundColor Green
Write-Host "Connection string: mssql+pyodbc://dbuser:Qwerty1234!@localhost\SQLEXPRESS/Scraped?driver=ODBC+Driver+17+for+SQL+Server" -ForegroundColor Yellow