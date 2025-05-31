# 🚀 Enhanced Media Scraper

**A powerful, multi-source media scraping application with advanced UI and real-time progress tracking.**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-2.0+-green.svg)](https://flask.palletsprojects.com/)
[![Status](https://img.shields.io/badge/Status-Production%20Ready-brightgreen.svg)]()

## ✨ Features

### 🎯 **Multi-Source Scraping**
- **78+ integrated sources** including Reddit, Instagram, Twitter, TikTok, YouTube
- **Adult content support** with safe search toggle
- **Comprehensive search** across images, videos, and GIFs
- **Real-time progress tracking** with detailed statistics

### 🎨 **Advanced Web Interface**
- **Responsive grid layout** with 5-per-row asset display
- **Video thumbnail generation** from first frame using canvas
- **Media viewer** with fullscreen support and keyboard navigation
- **Filter system** (All/Images/Videos) with real-time updates
- **Hover previews** for videos with smooth transitions

### ⌨️ **Keyboard Navigation**
- **Arrow keys** for media navigation (← → for prev/next)
- **Fullscreen control** (↑ for maximize, ↓ for minimize/close)
- **Media controls** (Space for play/pause, F for fullscreen, ESC to close)
- **Three fullscreen modes** (normal → maximize → stretch → close)

### 🔧 **Technical Features**
- **Flask backend** with RESTful API endpoints
- **Background job processing** with real-time status updates
- **Automatic file organization** by source and content type
- **Error handling** with graceful fallbacks
- **Production-ready** with comprehensive documentation

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/enhanced-media-scraper.git
   cd enhanced-media-scraper
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Start the application:**
   ```bash
   python app.py
   ```

4. **Open your browser:**
   Navigate to `http://localhost:5000`

### Alternative Startup Methods
```bash
# Production mode
python startup_scripts/run_production.py

# Windows batch file
startup_scripts/start.bat

# PowerShell script
startup_scripts/start.ps1
```

## 📦 Dependencies

- **Flask** (2.0+) - Web framework
- **yt-dlp** (2025.5.22) - Video downloader
- **gallery-dl** (1.29.7) - Social media content downloader
- **requests** - HTTP library
- **beautifulsoup4** - HTML parsing
- **Pillow** - Image processing

## 🎮 Usage Guide

### Basic Operation
1. **Start the server** using any of the startup methods
2. **Open the web interface** at `http://localhost:5000`
3. **Enter search terms** in the search box
4. **Select sources** (enable adult content if needed)
5. **Click "Start Download"** and monitor progress
6. **View results** in the asset grid below

### Keyboard Shortcuts
| Key | Action |
|-----|--------|
| `←` `→` | Navigate between media |
| `↑` | Cycle fullscreen modes |
| `↓` | Minimize or close viewer |
| `Space` | Play/pause videos |
| `F` | Toggle fullscreen |
| `ESC` | Close media viewer |

### Advanced Features
- **Safe Search Toggle:** Enable/disable adult content filtering
- **Source Selection:** Choose specific platforms to search
- **Real-time Progress:** Monitor downloads with live statistics
- **Asset Management:** Filter, view, and organize downloaded content

## 📁 Project Structure

```
enhanced-media-scraper/
├── app.py                          # Main Flask application
├── real_content_downloader.py      # Download engine
├── requirements.txt                # Python dependencies
├── README.md                       # This file
├── PROJECT_MAINTENANCE_GUIDE.md    # Comprehensive maintenance guide
├── SETUP_COMPLETE.md              # Detailed setup instructions
├── templates/
│   └── index.html                 # Web interface
├── downloads/                     # Downloaded content (auto-created)
└── startup_scripts/               # Server startup utilities
    ├── start.bat                  # Windows batch startup
    ├── start.ps1                  # PowerShell startup
    ├── run_production.py          # Production mode
    └── restart.bat                # Quick restart
```

## 🛡️ Safety & Legal

### Important Notes
- **Respect Terms of Service** of all platforms
- **Use responsibly** and within legal boundaries
- **Rate limiting** is implemented to prevent abuse
- **Adult content** filtering available for appropriate use

### Privacy
- **No data collection** - all content stays local
- **No external tracking** or analytics
- **Secure local storage** of downloaded content

## 🔧 Configuration

### Environment Setup
The application works out-of-the-box with default settings. For advanced configuration:

1. **Modify source settings** in `real_content_downloader.py`
2. **Adjust UI preferences** in `templates/index.html`
3. **Configure startup options** in `startup_scripts/`

### Troubleshooting
- **Flask won't start:** Check Python syntax with `python -m py_compile app.py`
- **UI not loading:** Verify all dependencies are installed
- **Downloads failing:** Check internet connection and source availability

## 📚 Documentation

- **[PROJECT_MAINTENANCE_GUIDE.md](PROJECT_MAINTENANCE_GUIDE.md)** - Comprehensive maintenance and recovery guide
- **[SETUP_COMPLETE.md](SETUP_COMPLETE.md)** - Detailed setup and feature documentation
- **[COMPREHENSIVE_SCRAPING_GUIDE.md](COMPREHENSIVE_SCRAPING_GUIDE.md)** - Advanced scraping techniques
- **[SAFESEARCH_BYPASS_GUIDE.md](SAFESEARCH_BYPASS_GUIDE.md)** - Safe search configuration

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines
- Follow the protection strategies in `PROJECT_MAINTENANCE_GUIDE.md`
- Test all changes thoroughly before submitting
- Maintain backward compatibility with existing features
- Document new functionality comprehensively

## 📈 Status

**Current Version:** 3.0 Production Ready  
**Status:** ✅ Fully Operational  
**Last Updated:** May 30, 2025  

### Success Metrics
- ✅ Flask server starts without errors
- ✅ UI loads and displays assets properly  
- ✅ Video thumbnails generate from first frame
- ✅ Media viewer with keyboard navigation
- ✅ Download system with 78+ sources
- ✅ Real-time progress tracking
- ✅ All API endpoints respond with HTTP 200

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Disclaimer

This tool is for educational and personal use only. Users are responsible for complying with all applicable laws and terms of service of the platforms they interact with. The developers are not responsible for any misuse of this software.

---

**Made with ❤️ for the open source community** 