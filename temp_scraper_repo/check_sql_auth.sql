-- Check SQL Server authentication mode
SELECT 
    CASE SERVERPROPERTY('IsIntegratedSecurityOnly')   
        WHEN 1 THEN 'Windows Authentication only'  
        WHEN 0 THEN 'SQL Server and Windows Authentication'  
    END AS AuthenticationMode;

-- Check if dbuser exists
SELECT name, type_desc, is_disabled
FROM sys.sql_logins
WHERE name = 'dbuser';

-- Check user permissions
SELECT 
    p.permission_name,
    p.state_desc
FROM sys.server_permissions p
JOIN sys.sql_logins l ON p.grantee_principal_id = l.principal_id
WHERE l.name = 'dbuser';