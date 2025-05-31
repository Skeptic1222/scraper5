# 🚀 Enhanced Media Scraper

**A comprehensive, multi-platform media scraping application with an advanced web interface, real-time progress tracking, and support for 78+ content sources including social media, image platforms, and adult content sites.**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-2.0+-green.svg)](https://flask.palletsprojects.com/)
[![Status](https://img.shields.io/badge/Status-Production%20Ready-brightgreen.svg)]()

## 🎯 What This Application Does

The Enhanced Media Scraper is a powerful, all-in-one solution for discovering, downloading, and managing media content from across the internet. It provides a sophisticated web interface that allows users to search and download images, videos, and GIFs from a vast array of sources with just a few clicks.

### 🔍 **Core Functionality**

**Unified Search Experience:** Instead of visiting dozens of different websites, users can search multiple platforms simultaneously from a single interface. Enter any search term, select your preferred sources, and let the application handle the rest.

**Intelligent Content Discovery:** The application doesn't just download - it intelligently discovers content using advanced search algorithms, follows links, extracts metadata, and organizes everything automatically.

**Real-Time Management:** Watch your downloads happen in real-time with live progress tracking, thumbnail generation, and immediate preview capabilities - no waiting to see what you've found.

## ✨ Features Overview

### 🌐 **Massive Source Coverage (78+ Platforms)**

**Social Media Platforms:**
- Reddit (including NSFW subreddits with advanced filtering)
- Instagram (posts, stories, profiles)
- Twitter/X (images, videos, user timelines)
- TikTok (videos, user content)
- Pinterest (boards, pins, user profiles)
- Tumblr (blogs, tags, media posts)

**Video Platforms:**
- YouTube (videos, channels, playlists)
- Vimeo (videos, user collections)
- Dailymotion (videos, user content)
- Adult video platforms (with safe search controls)

**Image Platforms:**
- Google Images (with advanced search options)
- Bing Images (including no-safe-search mode)
- Flickr (photos, albums, user galleries)
- DeviantArt (artwork, collections)
- Imgur (albums, galleries, individual images)

**Adult Content Platforms:**
- XVideos, Pornhub, XHamster (with age verification)
- Reddit NSFW communities
- Adult image boards and galleries
- Comprehensive adult content aggregation

**Specialized Sources:**
- E-commerce product images
- News media galleries
- Art and photography sites
- Community forums and boards

### 🎨 **Advanced Web Interface**

**Responsive Design:**
- Clean, modern interface that works on desktop and mobile
- 5-column grid layout optimizing screen real estate
- Hover effects and smooth transitions for professional feel
- Dark/light theme compatibility

**Real-Time Asset Management:**
- Live thumbnail generation for all media types
- Video thumbnails extracted from first frame using HTML5 canvas
- Instant filtering (All/Images/Videos/GIFs)
- Search within downloaded content
- Batch operations for managing large collections

**Media Viewer:**
- Full-screen media viewer with cinema-quality experience
- Support for all image formats (JPG, PNG, WebP, GIF, etc.)
- Video player with standard controls (play, pause, seek, volume)
- Multiple fullscreen modes (normal → maximize → stretch)
- Smooth transitions and loading animations

### ⌨️ **Professional Keyboard Navigation**

**Media Navigation:**
- `←` `→` Arrow keys for seamless browsing through media
- `↑` Cycle through fullscreen modes for optimal viewing
- `↓` Minimize or close viewer
- `Home`/`End` Jump to first/last media item

**Video Controls:**
- `Space` Play/pause toggle
- `F` Toggle fullscreen mode
- `M` Mute/unmute audio
- `ESC` Close media viewer
- `+`/`-` Zoom in/out for images

**Advanced Navigation:**
- `Ctrl+F` Search within current media collection
- `Delete` Remove selected media (with confirmation)
- `Ctrl+A` Select all media items
- Number keys (1-9) for quick filter switching

### 🔧 **Powerful Technical Architecture**

**Backend Engine:**
- Flask web server with RESTful API design
- Asynchronous download processing with queue management
- Smart retry logic for failed downloads
- Automatic duplicate detection and handling
- Bandwidth throttling to prevent rate limiting

**Download Intelligence:**
- Multi-threaded downloading with configurable concurrent connections
- Smart file naming with metadata preservation
- Automatic folder organization by source and date
- Progress tracking with ETA calculations
- Resume capability for interrupted downloads

**Content Processing:**
- Automatic image optimization and format conversion
- Video thumbnail extraction and preview generation
- Metadata extraction (EXIF, creation dates, source URLs)
- Content categorization and tagging
- Duplicate detection using perceptual hashing

## 🚀 Quick Start Guide

### Prerequisites
- **Python 3.8+** (3.9+ recommended for optimal performance)
- **pip package manager**
- **4GB+ RAM** (for processing large media collections)
- **High-speed internet connection** (for efficient downloading)

### Installation Steps

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Skeptic1222/Scraper.git
   cd Scraper
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Start the application:**
   ```bash
   python app.py
   ```

4. **Access the interface:**
   Open your browser and navigate to `http://localhost:5000`

### Alternative Startup Methods

**Production Mode (Recommended):**
```bash
python startup_scripts/run_production.py
```

**Windows Users:**
```bash
# Quick start
startup_scripts/start.bat

# PowerShell (with admin privileges)
startup_scripts/start.ps1

# Restart existing server
startup_scripts/restart.bat
```

## 📦 Technical Dependencies

**Core Framework:**
- **Flask 2.0+** - Web application framework and API server
- **yt-dlp 2025.5.22** - Advanced video downloader with platform support
- **gallery-dl 1.29.7** - Social media and gallery content extractor

**Media Processing:**
- **Pillow (PIL)** - Image processing and thumbnail generation
- **opencv-python** - Video processing and frame extraction
- **imageio** - Multi-format image reading and writing

**Web Scraping:**
- **requests** - HTTP client for web requests
- **beautifulsoup4** - HTML parsing and content extraction
- **selenium** - Browser automation for complex sites
- **cloudscraper** - Anti-bot protection bypass

**Data Management:**
- **sqlite3** - Local database for metadata and history
- **json** - Configuration and settings management
- **pickle** - Session state persistence

## 🎮 Complete Usage Guide

### Basic Operation Workflow

1. **Server Startup**
   - Launch using any startup method above
   - Wait for "Server running on http://localhost:5000" message
   - Navigate to the web interface

2. **Content Discovery**
   - Enter descriptive search terms (e.g., "nature photography", "cooking videos")
   - Toggle safe search based on desired content type
   - Select specific sources or use "All Sources" for maximum coverage

3. **Download Management**
   - Click "Start Download" to begin content discovery
   - Monitor real-time progress with live statistics
   - Watch thumbnails appear as content is processed

4. **Content Exploration**
   - Use the filter system to focus on specific media types
   - Navigate through content using keyboard shortcuts
   - Utilize fullscreen viewer for optimal media experience

### Advanced Features & Tips

**Search Optimization:**
- Use specific keywords for better results ("sunset beach" vs "pretty pictures")
- Combine terms with boolean logic where supported
- Try different variations of search terms for comprehensive results

**Source Management:**
- Start with safe search enabled to familiarize yourself with the interface
- Gradually enable specific adult sources if desired
- Monitor download speeds and adjust concurrent connections as needed

**Content Organization:**
- Downloads are automatically organized by source and date
- Use the search function to find specific content quickly
- Regular cleanup of downloads folder recommended for storage management

## 📁 Detailed Project Structure

```
enhanced-media-scraper/
├── 📄 app.py                          # Main Flask application server
├── 🔧 real_content_downloader.py      # Core download engine with 78+ sources
├── 📋 requirements.txt                # Python package dependencies
├── 📖 README.md                       # This comprehensive guide
├── 🛠️ PROJECT_MAINTENANCE_GUIDE.md    # System maintenance and troubleshooting
├── ⚙️ SETUP_COMPLETE.md              # Detailed installation guide
├── 🌐 templates/
│   └── index.html                     # Responsive web interface
├── 📁 downloads/                      # Downloaded media (auto-organized)
│   ├── reddit_nsfw/                   # Reddit NSFW content
│   ├── bing_images/                   # Bing image searches
│   ├── xvideos/                       # Adult video content
│   └── [source_name]/                 # Auto-created source folders
├── 🚀 startup_scripts/               # Server management utilities
│   ├── start.bat                      # Windows quick start
│   ├── start.ps1                      # PowerShell startup
│   ├── run_production.py              # Production server mode
│   ├── restart.bat                    # Server restart utility
│   └── stop.bat                       # Graceful server shutdown
└── 📚 [Additional Documentation]/     # Comprehensive guides and references
```

## 🔒 Privacy, Security & Legal Compliance

### Data Privacy
- **100% Local Operation:** All content remains on your local machine
- **No Cloud Storage:** No data sent to external servers or services
- **No Tracking:** No analytics, user tracking, or data collection
- **Secure Downloads:** Direct source connections without intermediaries

### Security Features
- **Input Sanitization:** All user inputs are validated and sanitized
- **Safe File Handling:** Automatic malware scanning for downloaded content
- **Secure Connections:** HTTPS enforcement for all external connections
- **Rate Limiting:** Built-in protection against excessive requests

### Legal Compliance
- **Terms of Service Respect:** Built-in rate limiting to comply with platform ToS
- **Copyright Awareness:** Downloads for personal use and research only
- **Age Verification:** Adult content access requires explicit user confirmation
- **DMCA Compliance:** Tools for content removal upon valid requests

### Responsible Usage Guidelines
- **Personal Use Only:** Content should be used for personal, educational, or research purposes
- **Respect Creators:** Consider supporting content creators through official channels
- **Legal Jurisdiction:** Users must comply with their local laws and regulations
- **Platform Guidelines:** Respect the terms of service of all scraped platforms

## 🛠️ Configuration & Customization

### Basic Configuration
The application works immediately with default settings optimized for most users:

**Download Settings:**
- Concurrent connections: 3 (adjustable in `real_content_downloader.py`)
- Default quality: Highest available
- Timeout settings: 30 seconds per request
- Retry attempts: 3 per failed download

**Interface Customization:**
- Grid layout: 5 items per row (responsive)
- Thumbnail size: 200x200px (auto-scaled)
- Video preview: First frame extraction
- Theme: Auto-detection based on system preference

### Advanced Configuration

**Source Customization:**
Edit `real_content_downloader.py` to:
- Add new content sources
- Modify existing source parameters
- Adjust search algorithms
- Configure quality preferences

**UI Modifications:**
Modify `templates/index.html` to:
- Change grid layout and styling
- Add custom filters and sorting
- Implement additional keyboard shortcuts
- Customize the media viewer experience

**Performance Tuning:**
- Adjust thread counts for your system capabilities
- Modify memory usage limits for large downloads
- Configure storage paths and organization
- Set bandwidth limiting for shared connections

## 🐛 Troubleshooting & Support

### Common Issues & Solutions

**Application Won't Start:**
```bash
# Check Python syntax
python -m py_compile app.py

# Verify dependencies
pip install -r requirements.txt --upgrade

# Check port availability
netstat -an | findstr 5000
```

**Downloads Failing:**
- Verify internet connection stability
- Check if source websites are accessible
- Review rate limiting settings
- Confirm disk space availability

**UI Not Loading:**
- Clear browser cache and cookies
- Try accessing via `127.0.0.1:5000` instead of `localhost:5000`
- Check browser console for JavaScript errors
- Verify all static files are present

**Performance Issues:**
- Reduce concurrent download threads
- Clear downloads folder of old content
- Check available RAM and disk space
- Restart the application periodically

### Getting Help

1. **Check Documentation:** Review all included markdown files for detailed guidance
2. **Search Issues:** Look through existing GitHub issues for similar problems
3. **Create Issues:** Submit detailed bug reports with logs and system information
4. **Community Support:** Engage with other users for tips and solutions

## 📚 Comprehensive Documentation

This project includes extensive documentation for all aspects of operation:

- **[PROJECT_MAINTENANCE_GUIDE.md](PROJECT_MAINTENANCE_GUIDE.md)** - Complete system maintenance, backup, and recovery procedures
- **[SETUP_COMPLETE.md](SETUP_COMPLETE.md)** - Detailed installation guide with troubleshooting
- **[COMPREHENSIVE_SCRAPING_GUIDE.md](COMPREHENSIVE_SCRAPING_GUIDE.md)** - Advanced scraping techniques and source configuration
- **[SAFESEARCH_BYPASS_GUIDE.md](SAFESEARCH_BYPASS_GUIDE.md)** - Safe search configuration and adult content handling
- **[WEB_INTERFACE_GUIDE.md](WEB_INTERFACE_GUIDE.md)** - Complete web interface documentation and customization
- **[HOW_TO_ACCESS.md](HOW_TO_ACCESS.md)** - Network access and remote usage instructions

## 🤝 Contributing to the Project

We welcome contributions from developers of all skill levels:

### Development Workflow
1. **Fork** the repository to your GitHub account
2. **Clone** your fork locally
3. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
4. **Develop** your changes with comprehensive testing
5. **Commit** with descriptive messages (`git commit -m 'Add amazing feature'`)
6. **Push** to your branch (`git push origin feature/amazing-feature`)
7. **Submit** a Pull Request with detailed description

### Contribution Guidelines
- **Code Quality:** Follow Python PEP 8 style guidelines
- **Testing:** Test all changes thoroughly across different platforms
- **Documentation:** Update relevant documentation for new features
- **Compatibility:** Maintain backward compatibility with existing installations
- **Security:** Consider security implications of all changes

### Areas for Contribution
- **New Sources:** Add support for additional content platforms
- **UI Improvements:** Enhance the web interface design and functionality
- **Performance:** Optimize download speeds and memory usage
- **Features:** Implement user-requested functionality
- **Documentation:** Improve guides and add tutorials
- **Testing:** Develop automated testing suites

## 📈 Current Status & Roadmap

### Current Version: 3.0 Production Ready
**Status:** ✅ Fully Operational and Stable  
**Last Updated:** May 30, 2025  

### Verified Functionality
- ✅ Flask server starts reliably without errors
- ✅ Web UI loads with full responsive design
- ✅ Video thumbnail generation from first frame
- ✅ Complete media viewer with keyboard navigation
- ✅ Download system operational across 78+ sources
- ✅ Real-time progress tracking with live updates
- ✅ All API endpoints respond correctly (HTTP 200)
- ✅ Adult content filtering and safe search controls
- ✅ Cross-platform compatibility (Windows, macOS, Linux)

### Future Development Plans
- **Mobile App:** Native mobile applications for iOS and Android
- **Cloud Integration:** Optional cloud storage and sync capabilities
- **AI Features:** Automatic content categorization and recommendations
- **Batch Processing:** Enhanced bulk download and processing capabilities
- **Plugin System:** Extensible architecture for community-developed sources
- **API Access:** Public API for third-party integrations

## ⚖️ Legal Information

### License
This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for complete details.

### Important Disclaimers

**Educational and Personal Use Only:** This software is designed for educational purposes, personal research, and individual content curation. Commercial use or redistribution of downloaded content may violate copyright laws.

**User Responsibility:** Users are solely responsible for:
- Complying with all applicable local, national, and international laws
- Respecting the terms of service of all platforms accessed
- Ensuring downloaded content is used appropriately and legally
- Verifying age requirements for adult content access

**Developer Liability:** The developers and contributors of this software:
- Provide the tool "as-is" without warranties of any kind
- Are not responsible for user actions or content downloaded
- Do not endorse or encourage violation of any terms of service
- Reserve the right to modify or discontinue the software at any time

**Content Ownership:** All downloaded content remains the intellectual property of its original creators and platforms. This software merely facilitates access to publicly available content.

---

**🌟 Built with passion for the open source community**  
**💡 Empowering users with comprehensive media discovery tools**  
**🚀 Continuously evolving with cutting-edge features** 