# SQL Express 2022 Setup Guide for Enhanced Media Scraper

## Prerequisites
- Windows with SQL Server Express 2022 installed
- Administrator access
- Python 3.11+ installed

## Quick Setup (Recommended)

### Step 1: Run Setup Script as Administrator
1. Right-click on `SETUP_SQLEXPRESS.bat`
2. Select "Run as administrator"
3. Follow the prompts

This script will:
- Enable SQL Server Authentication
- Create the `dbuser` login with password `Qwerty1234!`
- Create the `Scraped` database
- Set up proper permissions

### Step 2: Initialize Database Schema
```cmd
python init_db.py
```

### Step 3: Run the Application
```cmd
RUN_WITH_SQLEXPRESS.bat
```

## Manual Setup (If Scripts Fail)

### Step 1: Enable SQL Server Authentication
1. Open SQL Server Management Studio (SSMS)
2. Connect to `localhost\SQLEXPRESS` using Windows Authentication
3. Right-click the server → Properties → Security
4. Select "SQL Server and Windows Authentication mode"
5. Click OK
6. Restart SQL Server Express service

### Step 2: Create Login and Database
Run this SQL in SSMS:
```sql
-- Create login
IF NOT EXISTS (SELECT * FROM sys.server_principals WHERE name = 'dbuser')
BEGIN
    CREATE LOGIN [dbuser] WITH PASSWORD = 'Qwerty1234!',
    DEFAULT_DATABASE = [master],
    CHECK_EXPIRATION = OFF,
    CHECK_POLICY = OFF;
END

-- Enable login
ALTER LOGIN [dbuser] ENABLE;

-- Create database
IF NOT EXISTS (SELECT * FROM sys.databases WHERE name = 'Scraped')
    CREATE DATABASE [Scraped];

-- Set permissions
USE [Scraped];
CREATE USER [dbuser] FOR LOGIN [dbuser];
ALTER ROLE [db_owner] ADD MEMBER [dbuser];
```

### Step 3: Test Connection
```cmd
sqlcmd -S localhost\SQLEXPRESS -U dbuser -P Qwerty1234! -d Scraped -Q "SELECT DB_NAME()"
```

## Troubleshooting

### Error: "Login failed for user 'dbuser'"
1. Ensure SQL Server Authentication is enabled (not just Windows)
2. Restart SQL Server Express service after enabling
3. Check the password is exactly: `Qwerty1234!`

### Error: "Cannot open database 'Scraped'"
1. Database doesn't exist - run setup script
2. Check user permissions in SSMS

### Error: "SQL Server does not exist or access denied"
1. Check SQL Server Express service is running
2. Verify instance name is `SQLEXPRESS`
3. Check Windows Firewall settings

### Error: "timeout expired"
1. SQL Server may be starting up - wait 30 seconds
2. Check SQL Server Configuration Manager
3. Enable TCP/IP protocol if needed

## Connection String
The application uses this connection string:
```
mssql+pyodbc://dbuser:Qwerty1234!@localhost\SQLEXPRESS/Scraped?driver=ODBC+Driver+17+for+SQL+Server
```

## Files Created
- `SETUP_SQLEXPRESS.bat` - Main setup script (run as admin)
- `Setup-SQLExpress.ps1` - PowerShell setup script
- `RUN_WITH_SQLEXPRESS.bat` - Start application with SQL Express
- `test_sqlexpress.py` - Test database connectivity
- `init_sqlexpress.bat` - Initialize database schema

## Next Steps
After setup, the application will use SQL Express 2022 for all data storage:
- User accounts and authentication
- Downloaded media metadata
- Job tracking and progress
- Subscription information

Access the application at: **http://localhost/scraper**
