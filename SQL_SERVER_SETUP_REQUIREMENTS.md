# SQL Server Express Setup Requirements

## Current Status
- **Issue**: SQL Server Express cannot be accessed from WSL environment
- **Temporary Solution**: Using SQLite database
- **Target**: SQL Server Express with database "Scraped"

## Requirements for SQL Server Express

### 1. Windows-Side Setup Required
SQL Server Express must be configured to accept connections from WSL:

#### Enable TCP/IP Protocol
1. Open SQL Server Configuration Manager
2. Navigate to: SQL Server Network Configuration → Protocols for SQLEXPRESS
3. Enable TCP/IP protocol
4. Right-click TCP/IP → Properties → IP Addresses tab
5. Set TCP Port to 1433 for all IP addresses
6. Restart SQL Server Express service

#### Configure Windows Firewall
```powershell
# Run in Administrator PowerShell
New-NetFirewallRule -DisplayName "SQL Server" -Direction Inbound -Protocol TCP -LocalPort 1433 -Action Allow
New-NetFirewallRule -DisplayName "SQL Browser" -Direction Inbound -Protocol UDP -LocalPort 1434 -Action Allow
```

#### Enable SQL Server Authentication
1. Open SQL Server Management Studio (SSMS)
2. Right-click server → Properties → Security
3. Select "SQL Server and Windows Authentication mode"
4. Restart SQL Server service

### 2. Database Setup
Run the provided script in SSMS as administrator:
```sql
-- Execute setup_sql_server.sql
-- This creates:
-- - Database: Scraped
-- - Login: dbuser (password: Qwerty1234!)
-- - Grants db_owner permissions
```

### 3. WSL Configuration
#### Install ODBC Driver
```bash
# In WSL Ubuntu
curl https://packages.microsoft.com/keys/microsoft.asc | sudo apt-key add -
curl https://packages.microsoft.com/config/ubuntu/$(lsb_release -rs)/prod.list | sudo tee /etc/apt/sources.list.d/mssql-release.list
sudo apt-get update
sudo ACCEPT_EULA=Y apt-get install -y msodbcsql17
sudo apt-get install -y unixodbc-dev
```

#### Test Connection
```bash
# Test with sqlcmd
sqlcmd -S 192.168.1.xxx,1433 -U dbuser -P 'Qwerty1234!' -Q "SELECT @@VERSION"
```

### 4. Update Application Configuration
Once SQL Server is accessible, update `.env`:
```env
DATABASE_URL=mssql+pyodbc://dbuser:Qwerty1234!@<WINDOWS_IP>:1433/Scraped?driver=ODBC+Driver+17+for+SQL+Server
```

Replace `<WINDOWS_IP>` with:
- Your Windows host IP (run `ipconfig` in Windows)
- Or use `host.docker.internal` if available
- Or `$(hostname).local`

### 5. Initialize Database
```bash
python3 init_db.py
```

## Current Workaround
The application is currently using SQLite (`scraper.db`) which provides full functionality but without the enterprise features of SQL Server Express.

## Migration Path
When SQL Server becomes accessible:
1. Update DATABASE_URL in .env
2. Run database initialization script
3. Migrate existing SQLite data if needed
4. Restart the application

## Benefits of SQL Server Express
- Better performance for concurrent users
- Advanced querying capabilities
- Better backup/restore options
- Windows authentication integration
- Enterprise-grade reliability

## Troubleshooting Commands
```bash
# Check if SQL Server port is accessible
nc -zv <WINDOWS_IP> 1433

# Test ODBC driver
odbcinst -q -d

# Python connection test
python3 test_sqlserver.py
```