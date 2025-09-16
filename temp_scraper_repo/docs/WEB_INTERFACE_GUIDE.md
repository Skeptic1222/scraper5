# 🌐 Media Scraper - Web Interface Guide

## 🚀 **How to Start the Web Application**

### **Option 1: Quick Start (Recommended)**
```bash
python start_server.py
```
This will:
- ✅ Check all dependencies
- 🌐 Start the backend; access the UI at `http://localhost/scraper` (IIS proxy)
- 🔓 Automatically open your browser
- 📊 Show real-time status

### **Option 2: Direct Flask Start**
```bash
python app.py
```

### **Option 3: Windows Batch File**
Double-click: `start_server.bat`

---

## 🌐 **Access URLs**

Once started, visit any of these URLs in your browser:

- **Main Interface**: http://localhost/scraper
- **Scraper Page**: http://localhost/scraper
- **API Status**: http://localhost/scraper/api/downloads

---

## 🎨 **Web Interface Features**

### **📸 Image Downloader**
- **Search Query**: Enter any search term
- **Max Images**: Choose 1-100 images to download
- **Real-time Progress**: Live status updates
- **Instant Download**: Click "Download Images"

### **📱 Social Media Scraper**
- **Platform Selection**: Instagram, TikTok, or Other
- **URL Input**: Paste any profile or video URL
- **Background Processing**: Downloads happen in background
- **Status Tracking**: Real-time progress monitoring

### **📂 Downloads Manager**
- **Live File List**: See all downloaded content
- **Organized Folders**: Files sorted by search query
- **Direct Download**: Click any file to download
- **Auto Refresh**: Updates automatically after downloads

---

## 🔧 **API Endpoints**

The web interface provides a REST API:

### **Image Downloads**
```http
POST /api/download-images
Content-Type: application/json

{
  "query": "search term",
  "max_images": 10
}
```

### **Social Media Scraping**
```http
POST /api/scrape-social
Content-Type: application/json

{
  "platform": "instagram",
  "url": "https://instagram.com/username"
}
```

### **Job Status**
```http
GET /api/job-status/{job_id}
```

### **Downloads List**
```http
GET /api/downloads
```

---

## 📱 **Mobile Friendly**

The interface is fully responsive and works on:
- 📱 Mobile phones
- 📟 Tablets  
- 💻 Desktops
- 🖥️ Large screens

---

## 🛠️ **Troubleshooting**

### **Server Won't Start**
```bash
# Install dependencies
pip install -r requirements.txt

# Check Python version
python --version  # Should be 3.7+

# Start manually
python app.py
```

### **Port Already in Use**
If port 5000 is busy, edit `app.py` line 126:
```python
app.run(host='localhost', port=8080, debug=True)  # Change to port 8080
```

### **Can't Access from Other Devices**
Edit `app.py` line 126:
```python
app.run(host='0.0.0.0', port=5000, debug=True)  # Allow external access
```

### **Downloads Not Showing**
- Click the "Refresh" button in Downloads section
- Check the `downloads/` folder exists
- Restart the server

---

## 🔒 **Security Notes**

- **Local Only**: Server runs on localhost by default
- **No Authentication**: Currently no login required
- **File Access**: Downloaded files are publicly accessible
- **Development Mode**: Debug mode is enabled

For production use, consider:
- Adding authentication
- Using a production WSGI server
- Implementing file access controls
- Disabling debug mode

---

## 🎯 **Quick Test**

1. **Start Server**: `python start_server.py`
2. **Open Browser**: Go to http://localhost/scraper
3. **Test Image Download**: 
   - Enter "test" in search box
   - Click "Download Images"
   - Watch progress in real-time
4. **Check Downloads**: See files appear in Downloads section

---

## 🚪 **Stopping the Server**

- **Command Line**: Press `Ctrl+C`
- **Browser**: Close the terminal/command prompt
- **Background**: Use Task Manager to end Python process

---

## 📊 **Current Status**

✅ **Working Features:**
- Beautiful responsive web interface
- Real-time progress tracking
- Image downloading with custom queries
- Social media scraping (Instagram/TikTok)
- File management and downloads
- REST API endpoints

🎯 **Ready to Use:**
Your scraper is now available as a professional web application at `http://localhost/scraper`!

---

**🌟 Enjoy your new Media Scraper Web Interface! 🌟** 
