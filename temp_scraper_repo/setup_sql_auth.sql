-- Enable Mixed Mode Authentication
EXEC xp_instance_regwrite N'HKEY_LOCAL_MACHINE', 
    N'Software\Microsoft\MSSQLServer\MSSQLServer', 
    N'LoginMode', REG_DWORD, 2;

-- Create SQL login
IF NOT EXISTS (SELECT * FROM sys.server_principals WHERE name = 'scraper_user')
BEGIN
    CREATE LOGIN scraper_user WITH PASSWORD = 'Scraper@2024!', CHECK_POLICY = OFF;
END

-- Grant server permissions
ALTER SERVER ROLE sysadmin ADD MEMBER scraper_user;

-- Use scraperdb
USE scraperdb;

-- Create user in database
IF NOT EXISTS (SELECT * FROM sys.database_principals WHERE name = 'scraper_user')
BEGIN
    CREATE USER scraper_user FOR LOGIN scraper_user;
    ALTER ROLE db_owner ADD MEMBER scraper_user;
END

PRINT 'SQL Authentication setup complete. Restart SQL Server service for mixed mode to take effect.';