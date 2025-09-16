# Enhanced Media Scraper v3.0

## Overview

Enhanced Media Scraper is an enterprise-grade web scraping application that aggregates content from 118+ sources including search engines, social media platforms, video sites, and image galleries. The application provides a Flask-based web interface with authentication bypass for testing, database-driven asset management, and real-time progress tracking for bulk downloads.

## Recent Updates (Sept 16, 2025)

### Major UI Improvements
- **Resolved UI Stability**: Fixed critical JavaScript conflicts causing UI elements to flash and vanish by removing 30+ conflicting scripts
- **Enhanced Search Interface**: Created modular JavaScript components for search functionality with proper source selection
- **Modern UI Design**: Implemented gradient-based modern styling with card layouts and improved visual hierarchy
- **Asset Library Manager**: Built comprehensive asset display and management system with thumbnail preview support
- **Search Handler**: Developed robust search submission system with progress tracking and result display
- **Source Categories**: Organized 118+ sources into intuitive categories with icons and visual groupings

### Technical Fixes
- Removed problematic JavaScript files from static/js/fixes/ that were causing UI conflicts
- Simplified base template to include only essential scripts (Bootstrap + core functionality)
- Added enhanced CSS styling for modern, responsive design
- Created modular JavaScript architecture for better maintainability

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
- **PostgreSQL**: Primary production database with full ACID compliance
- **SQLite**: Development fallback with simplified setup
- **SQL Server Express**: Optional enterprise database support

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