# Enhanced Media Scraper - Site Architecture and Recent Fixes

## Overview
The Enhanced Media Scraper is a Flask-based web application that allows users to search and download media content from various sources. It uses Google OAuth for authentication and provides a modern web interface for content discovery.

## Architecture Components

### 1. Authentication System
**Technology**: Google Identity Services (Client-Side OAuth)
- **Template**: `templates/splash_gis.html` - Login page with Google Sign-In button
- **Backend**: `auth.py` - Handles OAuth callbacks and user management
- **Flow**:
  1. User clicks "Sign in with Google" button
  2. Google Identity Services shows authentication popup
  3. User authenticates with Google
  4. Google returns ID token to client
  5. Client sends token to `/auth/google/verify` endpoint
  6. Server verifies token and creates/updates user in database
  7. User session is created and user is redirected to main app

### 2. Database System
**Current**: SQLite (temporary) - Located at `instance/scraper.db`
**Planned**: SQL Server Express (configuration ready but auth issues)

**Models** (`models.py`):
- `User`: Authentication and user profile
  - Fields: id, google_id, email, name, picture, credits, subscription_plan, etc.
  - NO fields for: daily_limit, monthly_limit, is_admin (uses roles instead)
- `Role`: User roles (admin, user)
- `Asset`: Downloaded media files
- `ScrapeJob`: Download job tracking
- `AppSetting`: Application configuration

### 3. Frontend Architecture
**Framework**: Vanilla JavaScript with modular design
**Key Files**:
- `static/js/modules/app.js` - Main application controller
- `static/js/modules/asset-manager.js` - Media library management
- `static/js/modules/search.js` - Search functionality
- `static/js/modules/ai-assistant.js` - AI chat interface
- `static/js/modules/media-viewer.js` - Media preview/display

### 4. Backend Services
- **Content Sources**: 80+ media sources organized by category
- **Download Engine**: `optimized_downloader.py` - Handles actual downloads
- **Asset Manager**: `db_asset_manager.py` - In-memory asset storage
- **Job Manager**: `db_job_manager.py` - Download job queue

### 5. API Endpoints
- `/api/sources` - Get available content sources
- `/api/search` - Search for content
- `/api/download` - Initiate downloads
- `/api/assets` - Manage downloaded assets
- `/api/stats` - User statistics
- `/auth/*` - Authentication endpoints

## Recent Fixes Applied (2025-09-09)

### 1. Google OAuth Authentication Fix
**Problem**: OAuth login was completely broken after code cleanup
**Root Causes**:
- Wrong template being used (splash.html instead of splash_gis.html)
- User creation attempting to use non-existent model fields
- Missing Google authentication Python packages

**Solutions Applied**:
```python
# app.py line 461 - Changed to use correct template
return render_template('splash_gis.html', google_client_id=os.environ.get('GOOGLE_CLIENT_ID'), google_configured=google_configured)

# auth.py lines 605-617 - Fixed user creation
user = User(
    email=email,
    name=name or email.split('@')[0],
    google_id=google_id,
    picture=picture,
    created_at=datetime.utcnow(),
    credits=999999 if is_admin else 50,
    subscription_plan='premium' if is_admin else 'trial',
    subscription_status='active'
)

# Installed missing packages
pip install google-auth google-auth-oauthlib google-auth-httplib2
```

### 2. Asset API Parameter Mismatch
**Problem**: Asset API throwing "unexpected keyword argument 'file_type'" errors
**Solution**: Updated `db_asset_manager.py` to accept all parameters:
```python
def get_assets(user_id=None, file_type=None, limit=100, offset=0):
    # Now properly handles filtering and pagination
```

### 3. Template Reference Errors
**Problem**: Navbar trying to access non-existent route 'admin.get_stats'
**Solution**: Changed to use existing route 'admin_test'

### 4. Database Initialization Issues
**Problems**:
- SQLite database path issues
- AppSetting model field mismatches
- Environment variable conflicts

**Solutions**:
- Created `start.py` with proper absolute path handling
- Fixed AppSetting initialization with correct field structure
- Cleaned up .env file duplicates

## Configuration Files

### Environment Variables (.env)
```bash
# Google OAuth (REQUIRED)
GOOGLE_CLIENT_ID=your_google_client_id_here
GOOGLE_CLIENT_SECRET=your_google_client_secret_here

# Database
DATABASE_URL=sqlite:///instance/scraper.db  # Current
# DATABASE_URL=mssql+pyodbc://... # Future SQL Server

# OAuth Callback
OAUTH_CALLBACK_URL=/scraper/auth/google/callback  # Use IIS proxy path (no ports)

# Application
SECRET_KEY=8f42a73054b1749f8e9d0e9b3c4a5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c
DEBUG=True
PORT=5050
HOST=0.0.0.0

# Admin
ADMIN_EMAIL=sop1973@gmail.com

# PayPal (Sandbox)
PAYPAL_CLIENT_ID=AYmGjmBj0UNF...
PAYPAL_SECRET=ENab7lt1bLY...
PAYPAL_MODE=sandbox
```

### IIS Configuration (web.config)
- Configured to proxy requests from `/scraper` to Flask app on port 5050
- Handles static files directly
- OAuth callback rewrite rules

## How to Start the Application

### Development Mode (Behind IIS)
```bash
# Start the server
python3 start.py

# Access via IIS proxy
http://localhost/scraper
```

### Production Mode (Behind IIS)
```bash
# Ensure IIS is configured with web.config
# Start Flask server
python3 start.py

# Access through IIS at
http://localhost/scraper
```

## Known Issues and TODO

### Current Issues
1. **Missing JavaScript File**: `/static/js/fix-checkbox-selection.js` returns 404
2. **Asset Statistics**: `DBAssetManager` missing `get_asset_statistics` method
3. **IIS Integration**: Not accessible from WSL environment
4. **SQL Server**: Authentication not working, using SQLite fallback

### Future Improvements
1. Implement proper SQL Server authentication
2. Add missing asset statistics functionality
3. Complete admin dashboard implementation
4. Add comprehensive error handling
5. Implement proper logging system
6. Add unit tests for critical functions

## Testing Checklist

### OAuth Authentication
- [x] User can see login page
- [x] Google Sign-In button appears
- [x] Google authentication popup works
- [x] User is created/updated in database
- [x] Session is created successfully
- [x] User is redirected to main app

### Main Application
- [x] Sources load correctly
- [x] Search interface displays
- [ ] Search functionality works
- [ ] Downloads work correctly
- [x] Asset library displays (with errors)
- [ ] Media viewer works

### Admin Features
- [x] Admin user detection works
- [ ] Admin dashboard accessible
- [ ] User management works
- [ ] Settings management works

## File Structure
```
/mnt/c/inetpub/wwwroot/scraper/
├── app.py                 # Main Flask application
├── auth.py                # Authentication handlers
├── models.py              # Database models
├── start.py               # Startup script with DB init
├── optimized_downloader.py # Download engine
├── db_asset_manager.py    # Asset management
├── db_job_manager.py      # Job queue management
├── instance/
│   └── scraper.db        # SQLite database
├── static/
│   ├── css/              # Stylesheets
│   └── js/
│       └── modules/      # JavaScript modules
├── templates/
│   ├── base.html         # Base template
│   ├── index.html        # Main app
│   ├── splash_gis.html   # Login page (ACTIVE)
│   └── components/       # Reusable components
└── docs/                 # Documentation
```

## Security Considerations
1. **OAuth**: Using Google Identity Services for secure authentication
2. **Sessions**: Flask-Login manages user sessions
3. **CSRF**: Protection enabled via WTF_CSRF_ENABLED
4. **Admin Access**: Role-based access control
5. **API Security**: All endpoints check authentication

## Deployment Notes
- Application designed to run behind IIS on Windows Server
- WSL2 development environment supported
- Database migration path: SQLite → SQL Server Express
- Static files served directly by IIS in production

## Contact and Support
- Admin Email: sop1973@gmail.com
- Debug Mode: Currently enabled for development
- Logs: Check `server.log` for runtime information

---
Last Updated: 2025-09-09
Fixed By: Claude AI Assistant
Version: 3.0
