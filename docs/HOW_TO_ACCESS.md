# 🌐 **How to Access Your Media Scraper at localhost/scraper**

## 🚀 **Quick Start Guide**

### **Step 1: Start the Server**
Choose any of these methods:

**Method A - Python Script (Recommended):**
```bash
python start_server.py
```

**Method B - Direct Flask:**
```bash
python app.py
```

**Method C - Windows Batch:**
```bash
start_server.bat
```

### **Step 2: Open Your Browser**
Visit any of these URLs:

- **🏠 Main Page**: http://localhost/scraper
- **🔧 Scraper Interface**: http://localhost/scraper  
- **📁 Downloads**: http://localhost/scraper/api/downloads

---

## 🎯 **What You'll See**

### **Beautiful Web Interface**
- 📸 **Image Downloader**: Enter search terms, get images
- 📱 **Social Media Scraper**: Instagram, TikTok, YouTube support
- 📂 **Download Manager**: See all your downloaded files
- 📊 **Real-time Progress**: Live status updates

### **Features Available**
- ✅ Search and download images
- ✅ Scrape social media profiles  
- ✅ Monitor download progress
- ✅ Browse and download files
- ✅ Mobile-friendly interface
- ✅ REST API endpoints

---

## 🖥️ **Server Status**

Check if the server is running:
```bash
# Check IIS site status via browser or use API
curl http://localhost/scraper/api/downloads
```

---

## 📱 **Using the Interface**

### **Download Images:**
1. Enter a search term (e.g., "nature", "cats", "technology")
2. Choose how many images (1-100)
3. Click "Download Images"
4. Watch the progress bar
5. See files appear in Downloads section

### **Scrape Social Media:**
1. Select platform (Instagram/TikTok/Other)
2. Paste the profile or video URL
3. Click "Scrape Content"
4. Monitor the status
5. Download completed files

---

## 🔧 **Troubleshooting**

### **Can't Access http://localhost/scraper?**
```bash
# Make sure server is running
python app.py

# Check Windows Firewall
# Try different port if 5000 is busy
```

### **Server Not Starting?**
```bash
# Install dependencies
pip install -r requirements.txt

# Check Python version
python --version

# Restart with verbose output
python start_server.py
```

### **No Downloads Showing?**
- Click "Refresh" button
- Check if `downloads/` folder exists
- Restart the server

---

## 📊 **Current Setup**

✅ **Location**: `C:\inetpub\wwwroot\scraper`  
✅ **URL**: http://localhost/scraper  
✅ **Interface**: Modern, responsive web UI  
✅ **Backend**: Flask + Python 3.13  
✅ **Features**: Image download + Social media scraping  

---

## 🎯 **Ready to Use!**

Your media scraper is now a **professional web application**!

1. **Start**: `python start_server.py`
2. **Visit**: http://localhost/scraper
3. **Download**: Enter search terms and start downloading!

**🌟 Enjoy your localhost/scraper web interface! 🌟**

---

## 📞 **Quick Help**

- **Start Server**: `python start_server.py`
- **Web Interface**: http://localhost/scraper
- **Stop Server**: Press `Ctrl+C` in terminal
- **Restart**: Close terminal and run start command again

**Your scraper is now accessible at localhost just like you requested!** 🎉 
