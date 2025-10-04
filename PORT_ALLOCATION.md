# Multi-Project Port Allocation Strategy

**Environment:** C:\inetpub\wwwroot with IIS
**Date:** October 2, 2025

---

## 🎯 Port Allocation Map

### Active Projects & Ports

| Project | Physical Path | IIS Path | Backend Port | Status |
|---------|--------------|----------|--------------|--------|
| **Scraper** | `C:\inetpub\wwwroot\scraper` | `/scraper` | **8080** | ✅ Active |
| **MediaVault** | `C:\inetpub\wwwroot\mediavault` | `/mediavault` | **3001** | ✅ Configured |
| **Scheduler** | `C:\inetpub\wwwroot\scheduler` | `/scheduler` | **5000** | ✅ Active (PID 28660) |

### Root Site Protection

| Site | Physical Path | Port | Access | Status |
|------|--------------|------|--------|--------|
| **Default Web Site** | `%SystemDrive%\inetpub\wwwroot` | **80** | http://localhost | ✅ Protected |

---

## 🔒 Current Port Usage (Verified)

```
Port 5000  → Scheduler (Node.js/Express) - PID 28660
Port 8080  → Scraper (Flask) - PID 4
Port 3001  → MediaVault (configured, not running)
Port 3000  → MediaVault frontend (listening on ::1)
Port 80    → IIS Default Site (localhost root)
```

---

## ✅ Port Conflict Resolution

### Scraper Project (THIS PROJECT)
- **Backend Port:** 8080 (Flask)
- **IIS URL:** http://localhost/scraper
- **web.config:** `localhost:8080`
- **Status:** ✅ NO CONFLICTS

### Scheduler Project
- **Backend Port:** 5000 (Node.js)
- **IIS URL:** http://localhost/scheduler
- **web.config:** `localhost:5000`
- **Status:** ✅ NO CONFLICTS

### MediaVault Project
- **Backend Port:** 3001 (configured)
- **Frontend Port:** 3000 (React/development)
- **IIS URL:** http://localhost/mediavault
- **web.config:** `localhost:3001`
- **Status:** ✅ NO CONFLICTS

---

## 🚨 Critical Rules

### ⚠️ NEVER USE THESE PORTS:
- **Port 80** - Reserved for IIS Default Web Site (http://localhost)
- **Port 443** - Reserved for HTTPS (if configured)
- **Port 5000** - TAKEN by Scheduler
- **Port 8080** - TAKEN by Scraper

### ✅ Available Ports for Future Projects:
- **5050-5099** - Flask/Python applications
- **3000-3099** - React/Node.js frontends
- **8081-8089** - Additional web services

---

## 🔧 IIS Site Structure

### Active IIS Sites
```
1. Default Web Site
   - Path: %SystemDrive%\inetpub\wwwroot
   - Binding: *:80:
   - Status: Protected (DO NOT MODIFY)

2. shiftwise.org
   - Path: C:\inetpub\wwwroot\scheduler
   - Purpose: Scheduler project

3. OAuth-Scheduler
   - Path: C:\inetpub\wwwroot\scheduler
   - Purpose: OAuth variant of Scheduler

4. SecureGalleryPro
   - Path: C:\inetpub\wwwroot\SecureGalleryPro
   - Purpose: Separate gallery application
```

---

## 📋 Project-Specific Configuration

### Scraper (Current Project)
**Location:** `C:\inetpub\wwwroot\scraper`

**Files Updated:**
- ✅ `web.config` → Port 8080
- ✅ `start-server.bat` → Port 8080
- ✅ `stop-server.bat` → Port 8080
- ✅ `.env` → FLASK_RUN_PORT=8080

**Access:**
- Public URL: http://localhost/scraper
- Direct Flask: http://localhost:8080 (testing only)

### Scheduler
**Location:** `C:\inetpub\wwwroot\scheduler`

**Configuration:**
- Backend: Node.js on port 5000
- web.config proxies to localhost:5000
- Access: http://localhost/scheduler

### MediaVault
**Location:** `C:\inetpub\wwwroot\mediavault`

**Configuration:**
- Backend: Port 3001 (configured)
- Frontend: Port 3000 (development)
- web.config proxies to localhost:3001
- Access: http://localhost/mediavault

---

## 🛡️ Localhost Protection

### Default Site (http://localhost)
- **Physical Path:** `C:\inetpub\wwwroot`
- **Port:** 80 (HTTP)
- **Status:** ✅ Protected
- **Purpose:** Root IIS site, should NOT be modified by sub-applications

### Sub-Application Isolation
Each project runs in its own isolated context:
- Scraper → `/scraper` path
- MediaVault → `/mediavault` path
- Scheduler → `/scheduler` path

**IMPORTANT:** Projects do NOT affect http://localhost root!

---

## 🔍 Port Conflict Detection

### How to Check for Conflicts
```batch
REM Check all listening ports
netstat -ano | findstr "LISTENING"

REM Check specific port (e.g., 8080)
netstat -ano | findstr ":8080"

REM Check what process is using a port
tasklist /FI "PID eq [PID_NUMBER]"
```

### Port Conflict Prevention
1. **Always check** `netstat` before assigning a port
2. **Document** port assignments in this file
3. **Update** web.config to match backend port
4. **Test** both direct and IIS proxy access
5. **Never** hardcode ports in application URLs (use APP_BASE path)

---

## 📊 Port Allocation Best Practices

### Port Ranges by Technology
```
Flask/Python:     5050-5099, 8080-8099
Node.js/Express:  3000-3099, 5000-5099
React/Frontend:   3000-3099
ASP.NET:          8000-8099
Database:         1433 (SQL Server), 5432 (PostgreSQL)
```

### Recommended Port Assignment Strategy
1. **Check existing ports** (netstat)
2. **Assign from appropriate range**
3. **Update web.config immediately**
4. **Update .env or config files**
5. **Document in this file**
6. **Test IIS proxy routing**

---

## 🚀 Quick Reference Commands

### Start/Stop Scraper (Port 8080)
```batch
cd C:\inetpub\wwwroot\scraper
start-server.bat
stop-server.bat
```

### Check Port Status
```batch
netstat -ano | findstr ":8080"
netstat -ano | findstr ":5000"
netstat -ano | findstr ":3001"
```

### Verify IIS Proxy
```batch
curl http://localhost/scraper
curl http://localhost/scheduler
curl http://localhost/mediavault
```

---

## ⚠️ Troubleshooting

### Issue: Port Already in Use
1. Check what's using the port: `netstat -ano | findstr ":[PORT]"`
2. Identify process: `tasklist /FI "PID eq [PID]"`
3. Stop conflicting service or choose different port

### Issue: IIS 502/503 Error
1. Verify backend is running on correct port
2. Check web.config points to correct port
3. Test direct backend access: `curl http://localhost:[PORT]`
4. Restart IIS: `iisreset`

### Issue: http://localhost Not Working
1. Check Default Web Site is running in IIS
2. Verify port 80 is not blocked
3. Ensure no sub-app is interfering with root

---

## 📝 Change Log

### October 2, 2025
- ✅ Scraper port changed from 3050 → 8080
- ✅ All batch files updated
- ✅ web.config updated
- ✅ .env configuration updated
- ✅ Verified no conflicts with Scheduler (port 5000)
- ✅ Verified no conflicts with MediaVault (port 3001)
- ✅ Protected http://localhost root site

---

## 🎯 Summary

### Current State: ✅ ALL PROJECTS ISOLATED
- **No port conflicts** between projects
- **Scraper on 8080** - Unique, no conflicts
- **Scheduler on 5000** - Running, no conflicts
- **MediaVault on 3001** - Configured, no conflicts
- **http://localhost** - Protected, untouched

### Access URLs (No Port Numbers Visible!)
- http://localhost (root site - protected)
- http://localhost/scraper (Scraper app)
- http://localhost/scheduler (Scheduler app)
- http://localhost/mediavault (MediaVault app)

---

*This document ensures all Claude Code sessions are aware of port allocations across multiple projects.*
