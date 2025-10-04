# URL Mode Toggle - Troubleshooting Guide

**Problem**: URL mode toggle buttons not appearing on Search & Download page

## Quick Diagnostic Steps

### Step 1: Check if Template is Loading
1. Go to Search & Download page
2. **Look for a YELLOW BOX with red border** at the top of the page
3. It says: "⚠️ TEMPLATE UPDATE TEST: If you see this yellow box..."

**If you see the yellow box:**
- ✅ Template is loading correctly
- Problem is likely browser cache or JavaScript
- Go to Step 2

**If you DON'T see the yellow box:**
- ❌ Flask server needs restart or using wrong template
- Go to Step 4

---

### Step 2: Check Browser Console
1. Press `F12` to open browser developer tools
2. Click the **Console** tab
3. Look for these messages:

**Good signs (template loading):**
```
🔧 INDEX.HTML LOADED - Template Update: 2025-01-XX
✅ URL mode toggle already exists
OR
✅ URL mode toggle injected successfully!
```

**Bad signs (cache issue):**
```
❌ URL MODE NOT AVAILABLE - Browser cache may need clearing
```

---

### Step 3: Clear Browser Cache (HARD REFRESH)

**Windows:**
- Chrome/Edge: `Ctrl + Shift + Delete` → Clear cached images and files → Clear data
- Firefox: `Ctrl + Shift + Delete` → Cached Web Content → Clear Now
- **OR** Hard refresh: `Ctrl + F5` or `Shift + F5`

**After clearing cache:**
1. Close ALL browser tabs with the app
2. Reopen browser
3. Navigate to `http://localhost/scraper`
4. Check Search & Download section

---

### Step 4: Restart Flask Server

**If Flask is running via command line:**
```bash
# Find the process
ps aux | grep "python.*app.py"

# Kill it
pkill -f "python.*app.py"

# Restart
cd /path/to/scraper
python3 app.py
```

**If Flask is running as Windows service:**
```powershell
# Stop service
Stop-Service EnhancedMediaScraperService

# Start service
Start-Service EnhancedMediaScraperService
```

**If using IIS:**
- Open IIS Manager
- Find "scraper" application pool
- Right-click → Recycle

---

### Step 5: Verify Template File

Check that `templates/index.html` contains:

**Around line 35-48 (Search Mode Toggle):**
```html
<!-- Search Mode Toggle -->
<div class="mb-3">
    <div class="btn-group w-100" role="group">
        <input type="radio" class="btn-check" name="search-mode" id="mode-keyword" value="keyword" checked>
        <label class="btn btn-outline-primary" for="mode-keyword">
            <i class="fas fa-search"></i> Keyword Search
        </label>

        <input type="radio" class="btn-check" name="search-mode" id="mode-url" value="url">
        <label class="btn btn-outline-primary" for="mode-url">
            <i class="fas fa-link"></i> Paste URL
        </label>
    </div>
</div>
```

**Around line 65-84 (URL Input Container):**
```html
<!-- URL Paste Input (hidden by default) -->
<div class="mb-3" id="url-paste-container" style="display: none;">
    <div class="input-group input-group-lg">
        <span class="input-group-text bg-primary text-white">
            <i class="fas fa-link"></i>
        </span>
        <input type="url"
               class="form-control"
               id="url-paste-input"
               placeholder="Paste URL (YouTube, Reddit, Imgur, Pornhub, etc.)">
        <button type="button" class="btn btn-success px-4" id="url-scrape-btn">
            <i class="fas fa-download"></i> Scrape URL
        </button>
    </div>
</div>
```

---

## What Should Appear

When working correctly, you'll see:

```
┌─────────────────────────────────────────┐
│  Search & Download                      │
├─────────────────────────────────────────┤
│                                         │
│  [Keyword Search] [Paste URL]  ← Buttons│
│                                         │
│  ┌──────────────────────────┐          │
│  │ Enter keywords...   [🚀 Search] │   │
│  └──────────────────────────┘          │
│                                         │
└─────────────────────────────────────────┘
```

When you click **[Paste URL]**:

```
┌─────────────────────────────────────────┐
│  Search & Download                      │
├─────────────────────────────────────────┤
│                                         │
│  [Keyword Search] [Paste URL]  ← Active │
│                                         │
│  ┌──────────────────────────────────┐  │
│  │🔗 Paste URL here... [Scrape URL] │  │
│  └──────────────────────────────────┘  │
│  ℹ️ Supports: YouTube, Pornhub...      │
│                                         │
│  (Source selection hidden)              │
│                                         │
└─────────────────────────────────────────┘
```

---

## Still Not Working?

**Check these files exist:**
- `static/js/modules/url-scraper.js` ✅
- `static/js/modules/search-handler.js` ✅
- `templates/index.html` ✅

**Verify script loading in browser console:**
```javascript
// Check if url-scraper loaded
console.log(typeof window.pollJobStatus); // Should be "function"

// Check if elements exist
console.log(document.getElementById('mode-url')); // Should be an element, not null
console.log(document.getElementById('url-scrape-btn')); // Should be an element, not null
```

---

## Manual Failsafe Test

Open browser console (F12) and paste:

```javascript
// Force inject URL mode toggle
const searchForm = document.getElementById('search-form');
const searchQuery = document.getElementById('search-query');
const keywordContainer = searchQuery.closest('.mb-3');

const toggleHTML = `
<div class="mb-3">
    <div class="btn-group w-100" role="group">
        <input type="radio" class="btn-check" name="search-mode" id="mode-keyword" value="keyword" checked>
        <label class="btn btn-outline-primary" for="mode-keyword">
            <i class="fas fa-search"></i> Keyword Search
        </label>
        <input type="radio" class="btn-check" name="search-mode" id="mode-url" value="url">
        <label class="btn btn-outline-primary" for="mode-url">
            <i class="fas fa-link"></i> Paste URL
        </label>
    </div>
</div>
<div class="mb-3" id="url-paste-container" style="display: none;">
    <div class="input-group input-group-lg">
        <span class="input-group-text bg-primary text-white">
            <i class="fas fa-link"></i>
        </span>
        <input type="url" class="form-control" id="url-paste-input" placeholder="Paste URL">
        <button type="button" class="btn btn-success px-4" id="url-scrape-btn">
            <i class="fas fa-download"></i> Scrape URL
        </button>
    </div>
</div>
`;

keywordContainer.insertAdjacentHTML('beforebegin', toggleHTML);
console.log('✅ URL mode manually injected!');
```

If this works, the issue is Flask server not serving the updated template.

---

## Contact Info

If still not working after all steps, provide:
1. Screenshot of Search & Download page
2. Browser console screenshot (F12 → Console)
3. Flask server logs
4. Browser used (Chrome, Firefox, Edge, etc.)
