# Enhanced Media Scraper v3.0

## Overview

Enhanced Media Scraper is an enterprise-grade web scraping application that aggregates content from 118+ sources including search engines, social media platforms, video sites, and image galleries. The application provides a Flask-based web interface with authentication bypass for testing, database-driven asset management, and real-time progress tracking for bulk downloads.

## Recent Updates (Sept 18, 2025)

### Windows Enterprise Deployment Implementation
- **IIS FastCGI Integration**: Production-ready deployment using proper WSGI handlers with wfastcgi
- **SQL Server Express**: Native support with Windows Authentication and encrypted connections
- **Path Management**: Windows-compatible path utilities for enterprise deployment
- **Security Configuration**: Secure environment variables, least-privilege permissions, CSP headers
- **Deployment Scripts**: Automated PowerShell installation with secure configuration

### Critical Database Integration Fix (Completed)
- **Fixed Asset Storage**: Replaced in-memory storage with PostgreSQL database persistence
- **Database Manager**: Created proper `db_asset_manager.py` with SQLAlchemy integration
- **API Integration**: Fixed module imports and field name mismatches in assets blueprint
- **Data Persistence**: Assets now properly saved to PostgreSQL and persist across restarts
- **Verified Working**: 17+ assets confirmed in database, API returning data correctly

### Known Issues (Handover Documentation)

#### CRITICAL: Dashboard Navigation Issue
**Status**: UNRESOLVED - Requires architectural approach change
**Symptom**: Dashboard section appears blank when clicking "Dashboard" in sidebar, despite JavaScript console showing successful initialization
**Root Cause**: CSS hides all `.content-section` by default with `display: none !important`. Navigation system fails to apply `.active` class to `#dashboard-section` when clicked
**Technical Details**:
- Dashboard JavaScript (`simple-dashboard.js`) loads and executes successfully
- Console logs show "Container found, creating dashboard..." and "Dashboard HTML created successfully"
- APIs respond correctly (/api/assets returns 17 assets, /api/jobs responds)
- Issue is in SPA section-switching mechanism in `nav.js` not activating dashboard section
**Attempted Solutions** (All Failed):
- CSS !important overrides and cascade fixes
- Navigation attribute matching corrections (data-section="dashboard-section")
- Nuclear overlay testing (confirmed JS works, UI rendering issue)
- Multiple dashboard implementations (complex real-time vs simple cards)
**Recommended Solution**: Eliminate SPA gating for dashboard - create dedicated `/dashboard` route with server-side template rendering where dashboard content is visible by default

## Previous Updates (Sept 16, 2025)

### Complete UI Redesign from Ground Up
- **Rebuilt Layout Architecture**: Created clean, professional layout with fixed sidebar navigation and content area
- **Fixed Navigation System**: Implemented proper sidebar with Dashboard, Search & Download, Asset Library, and Settings sections
- **Hash-based Routing**: Added JavaScript navigation with URL hash support for deep linking and browser back/forward
- **Mobile Responsive**: Fully responsive design with collapsible sidebar and overlay for mobile devices
- **Clean CSS Structure**: Removed 30+ conflicting CSS files and created organized layout system

### Technical Implementation
- Created `base/layout.css` with comprehensive layout system and CSS variables
- Rebuilt `base.html` template with semantic HTML and accessibility features
- Implemented `nav.js` module for section switching and state management
- Maintained all existing functionality with 118+ content sources
- All API endpoints working correctly (/api/sources, /api/assets)

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Backend Architecture
- **Framework**: Flask 2.3.2 with SQLAlchemy ORM for database operations
- **Authentication**: Google OAuth 2.0 integration with Flask-Login for session management
- **Database**: PostgreSQL (production) with SQLite fallback for development
- **API Design**: RESTful endpoints with Blueprint-based modular organization
- **Deployment**: IIS reverse proxy configuration with proper URL routing

### Frontend Architecture
- **Template Engine**: Jinja2 with responsive HTML/CSS templates
- **JavaScript**: Vanilla JS with modular component architecture
- **UI Components**: Custom sidebar navigation, real-time progress indicators, and asset management interfaces
- **Responsive Design**: Mobile-friendly layouts with CSS Grid and Flexbox

### Data Storage Solutions
- **Primary Database**: PostgreSQL for production with comprehensive indexing
- **Asset Storage**: Database-backed media blob storage with file metadata
- **Caching**: In-memory job tracking and download caching for performance
- **Session Management**: Secure cookie-based sessions with configurable lifetime

### Content Sources Integration
- **78+ Sources**: Organized into categories (search engines, social media, video platforms, art platforms, adult content)
- **Parallel Processing**: Multi-threaded downloads with configurable worker pools
- **Rate Limiting**: Built-in throttling to respect source API limits
- **Content Filtering**: Safe search options and NSFW content controls

### Security and Authentication
- **OAuth Flow**: Google OAuth 2.0 with proper callback handling and state management
- **Role-Based Access Control**: Admin and user roles with permission-based feature access
- **Session Security**: HTTPOnly cookies with CSRF protection and secure headers
- **Input Validation**: Parameterized queries and request sanitization

### Performance Optimizations
- **Connection Pooling**: SQLAlchemy engine configuration with pool management
- **Request Timeouts**: Configurable timeout middleware for long-running operations
- **Memory Management**: Process monitoring and cleanup utilities
- **Database Optimization**: Strategic indexing and query optimization

## External Dependencies

### Authentication Services
- **Google OAuth 2.0**: Primary authentication provider with client credentials management
- **Flask-Login**: Session management and user state persistence

### Database Systems  
- **PostgreSQL**: Primary production database with full ACID compliance (current)
- **SQLite**: Development fallback with simplified setup
- **SQL Server Express**: Target migration database - requires pyodbc driver and connection string updates

### Python Libraries
- **Flask Ecosystem**: Flask-SQLAlchemy, Flask-WTF, Flask-Talisman for security
- **HTTP Clients**: Requests library with OAuth extensions for API communication
- **Media Processing**: Pillow for image manipulation and OpenCV for advanced processing
- **Web Scraping**: BeautifulSoup4 for HTML parsing and content extraction

### Development and Testing
- **Playwright**: Browser automation for UI testing and debugging
- **Code Quality**: Ruff for linting and Black for code formatting
- **Environment Management**: Python-dotenv for configuration management

### Deployment Infrastructure
- **IIS Integration**: Windows IIS reverse proxy configuration with URL rewriting
- **Process Management**: Windows Service integration for production deployment
- **Monitoring**: Custom logging with file rotation and error tracking

## Windows Enterprise Deployment

### Deployment Files Created
- **`deployment/windows/install.ps1`**: Automated PowerShell installation script with SQL Server Express setup
- **`deployment/windows/enhanced_media_scraper_service.py`**: Windows service wrapper for Flask application
- **`deployment/windows/service_manager.ps1`**: PowerShell service management script (install/start/stop/restart/status)
- **`deployment/windows/path_utils.py`**: Windows-compatible path management utilities
- **`deployment/windows/requirements_windows.txt`**: Windows-specific Python dependencies
- **`deployment/windows/README.md`**: Comprehensive Windows deployment documentation
- **`web.config.enterprise`**: IIS configuration with FastCGI, URL rewriting, security headers

### Key Features
- **IIS FastCGI**: Production-ready WSGI deployment with proper handler configuration
- **SQL Server Express**: Windows Authentication with encrypted connections (Encrypt=yes, TrustServerCertificate=no)
- **Enterprise Security**: Least-privilege file permissions, secure environment variable handling
- **Security Headers**: HSTS, CSP, X-Frame-Options for enterprise compliance
- **Path Management**: Windows-compatible file and directory handling
- **PowerShell Scripts**: Automated installation with secure configuration

## Migration Readiness

### SQL Server Express Migration
**Status**: Ready for migration
**Requirements**:
- Add `pyodbc` to requirements.txt
- Update DATABASE_URL format: `mssql+pyodbc://user:pass@localhost\\SQLEXPRESS/dbname?driver=ODBC Driver 18 for SQL Server`
- Validate SQLAlchemy models for MSSQL compatibility (autoincrement PKs, DateTime defaults)
- Add engine options: `pool_pre_ping=True`, `fast_executemany=True`

### Google OAuth Integration
**Status**: Architecture ready, needs configuration
**Current State**: `auth.py` implements OAuth flow with `init_auth(app)` function
**Required Configuration**:
- Set `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` environment variables
- Configure redirect URIs in Google Cloud Console
- Set `SESSION_COOKIE_SAMESITE=None` for production HTTPS
- Disable `MemoryUser` mock authentication in production

## Code Cleanup Required

### Files to Remove
- **Duplicate Apps**: `app_working.py`, `simple_app.py`, various start variants
- **Legacy Debugging**: `static/js/fixes/*`, `emergency-*.js`, multiple dashboard variants
- **Test Templates**: `index_simple.html`, `splash_*`, `test_*.html`
- **Artifacts**: `logs/*`, `debug_logs/*`, `downloads/*`, `*.zip`, `cookies.txt`, `instance/scraper.db`

### Security Concerns
- **Sensitive Data**: Remove cookies.txt, instance DB, and logs before GitHub upload
- **Debug Logging**: Currently at MAX level - must be reduced for production
- **Secrets**: Add .env.example, exclude actual secrets from repository