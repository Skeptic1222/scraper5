-- Create SQL login for aidev
IF NOT EXISTS (SELECT * FROM sys.server_principals WHERE name = 'aidev')
BEGIN
    CREATE LOGIN aidev WITH PASSWORD = 'qwerty', CHECK_POLICY = OFF;
END

-- Grant admin permissions
ALTER SERVER ROLE sysadmin ADD MEMBER aidev;

-- Use scraperdb
USE scraperdb;

-- Create user in database
IF NOT EXISTS (SELECT * FROM sys.database_principals WHERE name = 'aidev')
BEGIN
    CREATE USER aidev FOR LOGIN aidev;
    ALTER ROLE db_owner ADD MEMBER aidev;
END

PRINT 'User aidev configured successfully';