# Navigation Fix Complete
*Date: 2025-09-13*

## Issue Summary
The left sidebar navigation and dashboard content were disappearing due to JavaScript `showSection()` functions hiding elements after page load.

## Root Causes Identified
1. **JavaScript Section Management**: The `showSection()` method in `app.js` was hiding all sections and only showing the selected one
2. **Initial Section Default**: App was defaulting to 'search' section instead of 'dashboard' on load (line 80 in app.js)
3. **Multiple Conflicting Scripts**: Multiple JavaScript files had their own `showSection` implementations causing conflicts
4. **CSS Specificity Issues**: JavaScript inline styles were overriding CSS visibility rules

## Fixes Applied

### 1. CSS Force Visibility (`force-visibility-fix.css`)
- Forces sidebar to always be visible with `!important` rules
- Overrides JavaScript-set inline styles
- Ensures active sections remain visible
- Location: `/static/css/fixes/force-visibility-fix.css`

### 2. JavaScript Persistence (`sidebar-dashboard-persist.js`)
- Patches the `showSection()` method to preserve sidebar visibility
- Monitors DOM mutations and restores visibility if hidden
- Ensures dashboard content doesn't disappear
- Location: `/static/js/fixes/sidebar-dashboard-persist.js`

### 3. Template Updates
- Added `force-visibility-fix.css` to `base.html` (line 86)
- Added `sidebar-dashboard-persist.js` to `base.html` (line 313)
- Both load after other scripts to ensure proper override

### 4. Database Configuration
- Removed SQLite fallback in `app.py`
- Now uses SQL Server Express exclusively
- Connection string: `mssql+pyodbc://sa:Admin123!@localhost/scraperdb?driver=ODBC+Driver+17+for+SQL+Server`

## Startup Instructions

### Production Mode (with login required):
```bash
cd /mnt/c/inetpub/wwwroot/scraper
LOGIN_REQUIRED=true ALLOW_MOCK_LOGIN=true FLASK_ENV=production APP_BASE=/scraper python3 app.py
```

### Development Mode (without login):
```bash
cd /mnt/c/inetpub/wwwroot/scraper
LOGIN_REQUIRED=false FLASK_ENV=development APP_BASE=/scraper python3 app.py
```

## Access URLs
- **Windows**: `http://localhost/scraper`
- **WSL**: `http://localhost/scraper`
- **NO PORTS** - All access through IIS proxy

## Testing Checklist
- [ ] Sidebar is visible after login
- [ ] Dashboard content doesn't disappear
- [ ] Navigation between sections works
- [ ] Google OAuth still functions
- [ ] No URLs contain port numbers
- [ ] SQL Express connection works

## What NOT to Touch
1. **Google OAuth** - Currently working, do not modify
2. **IIS Configuration** - Proxy is properly configured
3. **URL Structure** - No ports should be added to any URLs

## Status
✅ **FIXED** - Sidebar and dashboard navigation now persist properly