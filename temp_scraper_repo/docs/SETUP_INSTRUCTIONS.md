# Enhanced Media Scraper - Setup Instructions

## Prerequisites
- Windows Server/Windows 10/11 with SQL Server Express 2022 installed
- Python 3.13 installed
- Administrator access

## Step 1: Configure SQL Server

1. **Enable SQL Server Authentication**
   - Open SQL Server Management Studio (SSMS)
   - Connect to `localhost\SQLEXPRESS` using Windows Authentication
   - Right-click on the server instance → Properties
   - Go to Security tab
   - Select "SQL Server and Windows Authentication mode"
   - Click OK and restart SQL Server

2. **Create Database Login**
   Run this in SSMS:
   ```sql
   -- Create login if it doesn't exist
   IF NOT EXISTS (SELECT * FROM sys.server_principals WHERE name = 'dbuser')
   BEGIN
       CREATE LOGIN [dbuser] WITH PASSWORD = 'Qwerty1234!';
   END
   
   -- Enable the login
   ALTER LOGIN [dbuser] ENABLE;
   ```

3. **Create Database**
   ```sql
   -- Create database
   IF NOT EXISTS (SELECT * FROM sys.databases WHERE name = 'Scraped')
   BEGIN
       CREATE DATABASE Scraped;
   END
   
   -- Grant permissions
   USE Scraped;
   CREATE USER [dbuser] FOR LOGIN [dbuser];
   ALTER ROLE db_owner ADD MEMBER [dbuser];
   ```

## Step 2: Configure Windows Firewall

1. Open Windows Defender Firewall with Advanced Security
2. Create new Inbound Rule:
   - Rule Type: Port
   - Protocol: TCP
   - Port: 1433
   - Action: Allow the connection
   - Profile: All
   - Name: SQL Server

## Step 3: Install Application Dependencies

Open Command Prompt as Administrator and navigate to the application directory:

```cmd
cd C:\inetpub\wwwroot\scraper

# Install Python dependencies
pip install -r requirements.txt
```

## Step 4: Initialize Database

```cmd
# Create database tables
python init_db.py
```

## Step 5: Start the Application

```cmd
# Start the Flask application
python app.py
```

The application will be available at: http://localhost/scraper

## Troubleshooting

### SQL Server Connection Issues

1. **Check SQL Server is running:**
   ```cmd
   sc query MSSQL$SQLEXPRESS
   ```

2. **Test connection with sqlcmd:**
   ```cmd
   sqlcmd -S localhost\SQLEXPRESS -U dbuser -P Qwerty1234! -Q "SELECT @@VERSION"
   ```

3. **Enable TCP/IP protocol:**
   - Open SQL Server Configuration Manager
   - SQL Server Network Configuration → Protocols for SQLEXPRESS
   - Enable TCP/IP
   - Restart SQL Server

### Python Module Issues

If you get module import errors:
```cmd
pip install --upgrade -r requirements.txt
```

### Permission Issues

Make sure the application directory has proper permissions:
```cmd
icacls C:\inetpub\wwwroot\scraper /grant "IIS_IUSRS:(OI)(CI)F"
```

## Default Credentials

- **Admin Email:** sop1973@gmail.com (configured in .env)
- **Database:** dbuser / Qwerty1234!
- **Windows Admin:** AIDEV / Qwerty1234!

## Next Steps

1. Access the application at http://localhost/scraper
2. Sign in with Google OAuth
3. The admin user (sop1973@gmail.com) will automatically get admin privileges
4. Start using the scraper!
