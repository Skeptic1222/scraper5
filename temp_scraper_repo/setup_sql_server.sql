-- Enhanced Media Scraper SQL Server Setup Script
-- Run this script in SQL Server Management Studio (SSMS) as administrator

-- Switch to master database
USE master;
GO

-- Create login if it doesn't exist
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
    -- Ensure password is correct
    ALTER LOGIN [dbuser] WITH PASSWORD = 'Qwerty1234!';
    PRINT 'Login [dbuser] password updated';
END
GO

-- Enable the login
ALTER LOGIN [dbuser] ENABLE;
GO

-- Create database if it doesn't exist
IF NOT EXISTS (SELECT * FROM sys.databases WHERE name = 'Scraped')
BEGIN
    CREATE DATABASE [Scraped];
    PRINT 'Database [Scraped] created successfully';
END
ELSE
BEGIN
    PRINT 'Database [Scraped] already exists';
END
GO

-- Switch to Scraped database
USE [Scraped];
GO

-- Create user for the login
IF NOT EXISTS (SELECT * FROM sys.database_principals WHERE name = 'dbuser')
BEGIN
    CREATE USER [dbuser] FOR LOGIN [dbuser];
    PRINT 'User [dbuser] created in database [Scraped]';
END
GO

-- Grant permissions
ALTER ROLE db_owner ADD MEMBER [dbuser];
PRINT 'User [dbuser] added to db_owner role';
GO

-- Verify the setup
PRINT '';
PRINT '=== Verification ===';
PRINT 'Database: ' + DB_NAME();
PRINT 'Current User: ' + USER_NAME();
PRINT '';
PRINT 'Setup completed successfully!';
PRINT 'Connection string for the application:';
PRINT 'mssql+pyodbc://dbuser:Qwerty1234!@localhost\SQLEXPRESS/Scraped?driver=ODBC+Driver+17+for+SQL+Server';
GO