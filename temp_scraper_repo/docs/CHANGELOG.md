# Scraper Application Changelog

## Version 2.1.2 - Command Center & Video Fix (December 2024)

### 🎯 Critical Fixes

#### 1. **Fixed Command Center Display Updates**
- **Issue**: Command center showed all zeros during downloads (Files Scanned: 0, Downloaded: 0%, etc.)
- **Root Cause**: JavaScript element ID mapping was incorrect
- **Fix**: 
  - Updated `updateCommandCenter()` to properly map `totalScanned`, `totalDownloaded` elements
  - Now shows real-time updates during downloads
  - Progress statistics update every second

#### 2. **Fixed Video Downloads Completely Failing**
- **Issue**: Videos detected but 0 downloaded with error "_parse_browser_specification() takes from 1 to 4 positional arguments but 6 were given"
- **Root Cause**: `cookiesfrombrowser` was incorrectly defined as list `['chrome', 'firefox']`
- **Fix**: 
  - Changed to single string `'cookiesfrombrowser': 'chrome'`
  - Videos now download properly from all platforms
  - Chrome cookies used for authenticated content

## Version 2.1.1 - Video Download Enhancement (December 2024)

### 🎯 Critical Fixes

#### 1. **Fixed Video-Only Search Filtering**
- **Issue**: When selecting "Videos" in search type, images were still being downloaded
- **Root Cause**: Search type parameter wasn't being passed through to the download functions
- **Fix**: 
  - Updated `run_comprehensive_search_job` to pass search_type to `comprehensive_multi_source_scrape`
  - Modified `download_urls_from_source` to accept and respect filter_type parameter
  - Added logic to skip non-video content when "videos" filter is active

#### 2. **Fixed Media Viewer Text Overlay**
- **Issue**: Text information was overlaying the image/video in the media viewer
- **Root Cause**: CSS positioning was set to absolute with bottom positioning
- **Fix**: Changed to relative positioning with margin-top to display text below media

#### 3. **Enhanced Video Download Capabilities**
- **Improvements**:
  - Added multiple quality fallbacks (720p → 480p → best available)
  - Platform-specific handling for Twitter/X, Instagram, TikTok
  - Chrome cookie integration for authenticated content
  - Direct download fallback for .mp4/.webm/.avi/.mov files
  - Better error handling with specific messages for private/unavailable videos
  - Downloads video thumbnails alongside videos
  - Increased file size limit to 200MB
  - Added retry logic and fragment retries

## Version 2.1.0 - AI Enhancement Update (December 2024)

### 🎯 Critical Fixes

#### 1. **Fixed Download Functionality**
- **Issue**: Downloads were failing with a "job not found" error
- **Root Cause**: 
  - Database was trying to store Python dictionaries directly in SQL Server fields
  - Frontend was looking for `data.job` when backend returned data at top level
- **Fix**: 
  - Updated `db_job_manager.py` to convert dictionaries to JSON strings before database storage
  - Fixed frontend to properly access job data without `.job` nesting
  - Improved download methods to use anchor tags instead of iframes (more reliable)

#### 2. **Fixed Image/Video Viewing**
- **Issue**: Broken image icons were showing instead of actual images
- **Root Cause**: Missing `check_asset_access` function causing authentication errors
- **Fix**: Added proper asset access control in `app.py` to handle public/private assets correctly

### 🎨 UI/UX Improvements

#### 1. **Theme Fixes**
- **System Status Box**: Now properly styled in both light and dark modes with improved spacing
- **Form Controls**: Fixed text input visibility issues in both themes
- **Progress Panels**: Updated all panels to use theme-aware styling variables

#### 2. **Asset Library Enhancements**
- **Removed View Button**: Thumbnails are now directly clickable to open media viewer
- **Added Download Icon**: Floating download button on each asset card for quick downloads
- **Select All**: Added checkboxes to select all images or all videos at once
- **Improved Layout**: Better positioning prevents UI elements from overlaying images

#### 3. **Command Center Improvements**
- **Activity Feed**: Now shows meaningful content including:
  - Real filenames being downloaded
  - URLs being searched
  - Source-specific progress updates
  - AI-enhanced insights (when API key is configured)
- **Better Styling**: Improved font, spacing, and readability

### 🤖 AI Integration

#### 1. **OpenAI GPT-4 Integration**
- **API Key**: Integrated OpenAI API key for AI-powered features
- **AI Assistant**: Added intelligent search assistant that helps:
  - Optimize search queries
  - Filter out fake/misleading content
  - Recommend best sources
  - Provide real-time search insights

#### 2. **AI-Enhanced Search Features**
- **Query Optimization**: AI analyzes and improves search terms
- **Smart Filters**: 
  - Exclude fake/misleading content
  - High quality content only
  - Verified sources only
  - Recent content filtering (30 days)
- **Source Recommendations**: AI suggests optimal sources based on query
- **Live Insights**: Real-time optimization score and recommendations

### 📋 Technical Changes

#### 1. **Backend Updates**
- Added `ai_assistant.py` module for OpenAI integration
- Updated `app.py` with:
  - AI assistant endpoints (`/api/ai-assistant`, `/api/ai-optimize-query`)
  - Fixed asset access control
  - Improved download handling with proper headers
- Updated `db_job_manager.py` to handle JSON serialization properly

#### 2. **Frontend Updates**
- Enhanced `templates/index.html` with:
  - AI assistant panel and chat interface
  - Improved asset card creation
  - Better download handling
  - Theme-aware styling throughout
  - Activity feed with real updates

#### 3. **Dependencies**
- Added `openai>=0.27.0` to `requirements.txt`

### 🔧 Configuration

#### Environment Variables
```env
# OpenAI Configuration (add to .env file)
OPENAI_API_KEY=your-api-key-here
```

### 📝 Usage Notes

1. **Downloading Assets**:
   - Click the download icon on any asset card
   - Use "Download Selected" for bulk downloads
   - Videos now download properly with correct headers

2. **AI Assistant**:
   - Click "AI Assistant" button in search section
   - Chat naturally about what you want to search
   - AI will optimize queries and suggest sources

3. **Asset Selection**:
   - Click thumbnails to view in media viewer
   - Use checkboxes to select individual assets
   - Use "Select All Images/Videos" for bulk selection

### 🐛 Known Issues Fixed
- ✅ Database JSON serialization errors
- ✅ "Job not found" errors during downloads
- ✅ Broken image thumbnails
- ✅ Form input visibility in light/dark modes
- ✅ System status box styling
- ✅ Video downloading issues

### 🚀 Next Steps
- Webhook integration for email automation
- Customer service chatbot with user account awareness
- Enhanced AI feedback in activity feed
- Improved video thumbnail generation 