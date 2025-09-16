# SQL Server Express 2022 Setup for WSL Access

## The Issue
SQL Server Express running on Windows is not accessible from WSL by default due to:
1. Windows Firewall blocking the connection
2. SQL Server not configured for remote connections
3. Network isolation between WSL and Windows host

## Solution Steps

### Step 1: Enable SQL Server for Remote Connections (Run in Windows)

1. **Open SQL Server Configuration Manager**
   - Windows Key + R → `SQLServerManager16.msc` (for SQL Server 2022)

2. **Enable TCP/IP Protocol**
   - Navigate to: SQL Server Network Configuration → Protocols for SQLEXPRESS
   - Right-click "TCP/IP" → Enable
   - Double-click "TCP/IP" → IP Addresses tab
   - Scroll to "IPAll" section
   - Set TCP Port: 1433
   - Clear TCP Dynamic Ports field

3. **Restart SQL Server**
   - SQL Server Services → SQL Server (SQLEXPRESS) → Restart

### Step 2: Configure Windows Firewall (Run as Administrator)

```powershell
# Open PowerShell as Administrator and run:
New-NetFirewallRule -DisplayName "SQL Server" -Direction Inbound -Protocol TCP -LocalPort 1433 -Action Allow
New-NetFirewallRule -DisplayName "SQL Browser" -Direction Inbound -Protocol UDP -LocalPort 1434 -Action Allow
```

### Step 3: Enable SQL Server Authentication

1. **Open SQL Server Management Studio (SSMS)**
2. **Connect to localhost\SQLEXPRESS**
3. **Right-click server → Properties → Security**
4. **Select "SQL Server and Windows Authentication mode"**
5. **Click OK and restart SQL Server**

### Step 4: Verify dbuser Login

```sql
-- Run in SSMS
USE master;
GO

-- Check if dbuser exists
SELECT name FROM sys.sql_logins WHERE name = 'dbuser';

-- If not exists, create it
CREATE LOGIN dbuser WITH PASSWORD = 'Qwerty1234!';
GO

-- Grant permissions
ALTER SERVER ROLE sysadmin ADD MEMBER dbuser;
GO

-- Ensure user can connect
ALTER LOGIN dbuser ENABLE;
GO
```

### Step 5: Test from WSL

After completing the above steps, the connection should work with:
```
DATABASE_URL=mssql+pyodbc://dbuser:Qwerty1234!@172.26.96.1\\SQLEXPRESS/Scraped?driver=ODBC+Driver+17+for+SQL+Server
```

## Alternative: Use Application in Windows

If SQL Server connectivity from WSL continues to be an issue, consider:
1. Running the Flask app directly in Windows (not WSL)
2. Using Windows Terminal with Python installed on Windows
3. Or continuing with the mock database mode for development