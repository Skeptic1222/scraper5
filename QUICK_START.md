# 🚀 Enhanced Media Scraper - Quick Start Guide

## 📍 How to Access the Application

### From Any Windows Browser
```
http://localhost/scraper
```
✅ This is the primary way to access the application

### Admin Login
```
Email: sop1973@gmail.com
Password: Use Google OAuth (click "Sign in with Google")
```

## 🔧 Common Tasks

### Start the Server (from WSL)
```bash
cd /mnt/c/inetpub/wwwroot/scraper
python3 start_server.py
```

### Stop All Server Instances
```bash
pkill -f "python.*start_server"
```

### Check if Server is Running
```bash
ps aux | grep python
```

### View Server Logs
```bash
# From the latest running server
tail -f /mnt/c/inetpub/wwwroot/scraper/logs/app.log
```

## 🗄️ Database Information

### Current Database
- **Type**: SQLite (temporary)
- **Location**: `/mnt/c/inetpub/wwwroot/scraper/instance/scraper.db`
- **Status**: ✅ Working

### Target Database (Not Yet Active)
- **Type**: SQL Server Express
- **Server**: localhost,1433
- **Database Name**: Scraped
- **Status**: ⚠️ Authentication issues, needs configuration

## 🐛 Troubleshooting

### "Sources Not Loading"
1. Click the red "Fix Sources NOW" button at bottom right
2. Or refresh the page (F5)
3. Or restart the server

### "Cannot Login"
1. Clear browser cookies
2. Try incognito/private mode
3. Ensure you're using http://localhost/scraper (not https)

### "Multiple Server Instances Running"
```bash
# Kill all Python processes
pkill -f python

# Start fresh
cd /mnt/c/inetpub/wwwroot/scraper
python3 start_server.py
```

### "Database Connection Failed"
Currently using SQLite which should always work. If issues:
```bash
# Check database file exists
ls -la instance/scraper.db

# Recreate if needed
python3 init_db.py
```

## 📂 Important Paths

### WSL Paths
- **Application**: `/mnt/c/inetpub/wwwroot/scraper/`
- **Database**: `/mnt/c/inetpub/wwwroot/scraper/instance/scraper.db`
- **Logs**: `/mnt/c/inetpub/wwwroot/scraper/logs/`

### Windows Paths
- **Application**: `C:\inetpub\wwwroot\scraper\`
- **Access URL**: `http://localhost/scraper`
- **IIS Manager**: Run `inetmgr` from Windows

## ⚡ Quick Commands

### Update Admin Credits
```bash
python3 update_admin_account.py
```

### Check API Status
```bash
curl http://localhost/scraper/api/sources
```

### View Running Processes
```bash
ps aux | grep python | grep -v grep
```

### Emergency Server Restart
```bash
pkill -f python && python3 start_server.py
```

## 🎯 Features Status

| Feature | Status | Notes |
|---------|--------|-------|
| Google Login | ✅ Working | Use sop1973@gmail.com |
| Source Display | ✅ Fixed | 78+ sources available |
| Search | ✅ Working | Basic functionality |
| Downloads | ⚠️ Partial | Some sources may fail |
| Asset Library | ✅ Working | View/manage downloads |
| Admin Panel | ✅ Fixed | Full access granted |

## 📝 Key Files to Know

- **Main App**: `app.py` (start via `python start.py` preferred)
- **Server Start**: `start.py`
- **Configuration**: `.env`
- **Database Models**: `models.py`
- **Authentication**: `auth.py`

## 🔗 Useful Links

- **Application**: http://localhost/scraper
- **Direct Flask**: internal backend port (for IIS only; avoid in code/UI)
- **IIS Manager**: `inetmgr` (Windows)
- **Documentation**: `/mnt/c/inetpub/wwwroot/scraper/docs/`

## 💡 Pro Tips

1. **Always use `app_refactored.py`**, not `app.py`
2. **SQLite is currently active**, not SQL Server Express
3. **The red "Fix Sources NOW" button** can resolve many UI issues
4. **Admin account** (sop1973@gmail.com) has unlimited credits
5. **IIS handles the `/scraper` prefix**, Flask doesn't need it

## 🆘 Need Help?

1. Check `/docs/CURRENT_STATUS_AND_ACCESS.md` for detailed info
2. Review `/docs/CODE_REVIEW_2025.md` for known issues
3. See `/docs/RECENT_FIXES_AND_IMPROVEMENTS.md` for what's been fixed

---

**Quick Access**: http://localhost/scraper  
**Admin Email**: sop1973@gmail.com  
**Server Port**: 5050 (proxied via IIS)  
**Database**: SQLite (for now)
