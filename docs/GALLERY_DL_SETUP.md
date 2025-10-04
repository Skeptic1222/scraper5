# Gallery-DL Configuration Guide
**Status**: Tool installed, configuration created, API keys needed
**Config Location**: `C:\inetpub\wwwroot\scraper\config\gallery-dl\config.json`

---

## ✅ Current Status

- [x] gallery-dl installed (version 1.30.9)
- [x] Configuration file created
- [ ] API credentials configured
- [ ] Sources tested and verified

---

## 🔑 Required API Credentials

To unlock the full potential of gallery-dl, you need to register for API keys from each service:

### Priority 1: High-Impact Sources (Register First)

#### 1. Reddit
**Why**: Major visual content source, high success potential
**Registration**: https://www.reddit.com/prefs/apps
**Steps**:
1. Go to https://www.reddit.com/prefs/apps
2. Click "create another app..."
3. Choose "script" type
4. Name: "Enhanced Media Scraper"
5. Description: "Personal media aggregator"
6. Redirect URI: http://localhost
7. Click "create app"
8. Copy `client_id` (under app name) and `client_secret`

**Add to config**:
```json
"reddit": {
  "enabled": true,
  "client-id": "YOUR_CLIENT_ID_HERE",
  "client-secret": "YOUR_CLIENT_SECRET_HERE",
  "user-agent": "EnhancedMediaScraper/3.0"
}
```

**Expected Impact**: 5% → 60-80% success rate

---

#### 2. Imgur
**Why**: Popular image hosting, easy API
**Registration**: https://api.imgur.com/oauth2/addclient
**Steps**:
1. Go to https://api.imgur.com/oauth2/addclient
2. Application name: "Enhanced Media Scraper"
3. Authorization type: "OAuth 2 authorization without a callback URL"
4. Email: your email
5. Description: "Personal media scraper"
6. Submit
7. Copy `Client ID`

**Add to config**:
```json
"imgur": {
  "enabled": true,
  "client-id": "YOUR_CLIENT_ID_HERE"
}
```

**Expected Impact**: 0% → 40-60% success rate

---

#### 3. Twitter/X (Optional - account required)
**Why**: Trending content source
**No API needed**: Uses login credentials
**Steps**:
1. Create a dedicated Twitter account for scraping (recommended)
2. Or use your existing account (may trigger rate limits)

**Add to config**:
```json
"twitter": {
  "enabled": true,
  "username": "your_twitter_username",
  "password": "your_twitter_password"
}
```

**Expected Impact**: 0% → 30-50% success rate

---

### Priority 2: Medium-Impact Sources

#### 4. Flickr
**Why**: High-quality photography source
**Registration**: https://www.flickr.com/services/apps/create/
**Steps**:
1. Go to https://www.flickr.com/services/apps/create/
2. Choose "Apply for a Non-Commercial Key"
3. App name: "Enhanced Media Scraper"
4. Description: "Personal media aggregator"
5. Submit
6. Copy `Key` and `Secret`

**Add to config**:
```json
"flickr": {
  "enabled": true,
  "api-key": "YOUR_API_KEY_HERE",
  "api-secret": "YOUR_API_SECRET_HERE"
}
```

---

#### 5. DeviantArt
**Why**: Art and illustration source
**Registration**: https://www.deviantart.com/developers/
**Steps**:
1. Go to https://www.deviantart.com/developers/
2. Click "Register Your Application"
3. Application name: "Enhanced Media Scraper"
4. Description: "Personal media scraper"
5. OAuth2 Redirect URI Whitelist: http://localhost
6. Submit
7. Copy `client_id` and `client_secret`

**Add to config**:
```json
"deviantart": {
  "enabled": true,
  "client-id": "YOUR_CLIENT_ID_HERE",
  "client-secret": "YOUR_CLIENT_SECRET_HERE"
}
```

---

#### 6. Instagram (Optional - account required)
**Why**: Major social media source
**No API needed**: Uses login credentials
**Note**: May require 2FA handling

**Add to config**:
```json
"instagram": {
  "enabled": true,
  "username": "your_instagram_username",
  "password": "your_instagram_password"
}
```

---

### Priority 3: Specialized Sources

#### 7. Pixiv (Anime/Art)
**No API needed**: Uses login credentials
**Steps**:
1. Create Pixiv account (free)
2. Add credentials to config

**Add to config**:
```json
"pixiv": {
  "enabled": true,
  "username": "your_pixiv_username",
  "password": "your_pixiv_password"
}
```

---

#### 8. Danbooru / E621 (Anime/Booru)
**Registration**:
- Danbooru: https://danbooru.donmai.us/profile
- E621: https://e621.net/users/home

**Steps**:
1. Create account
2. Go to profile settings
3. Generate API key

**Add to config**:
```json
"danbooru": {
  "enabled": true,
  "username": "your_username",
  "api-key": "your_api_key"
},
"e621": {
  "enabled": true,
  "username": "your_username",
  "api-key": "your_api_key"
}
```

---

## 🚀 Quick Start (No API Keys Required)

Some sources work without API keys:

### Working Out-of-the-Box:
- **Pinterest**: No auth needed
- **ArtStation**: No auth needed
- **Gelbooru**: No auth needed
- **Rule34**: No auth needed

**Test immediately**:
```bash
cd C:\inetpub\wwwroot\scraper
gallery-dl --config config/gallery-dl/config.json "https://www.pinterest.com/search/pins/?q=landscape"
```

---

## 🧪 Testing Gallery-DL

### Test Individual Sources:

```bash
# Test Reddit (after adding API keys)
gallery-dl --config config/gallery-dl/config.json "https://www.reddit.com/r/wallpapers/top/?t=week"

# Test Imgur (after adding API key)
gallery-dl --config config/gallery-dl/config.json "https://imgur.com/gallery/example"

# Test Pinterest (no API needed)
gallery-dl --config config/gallery-dl/config.json "https://www.pinterest.com/search/pins/?q=nature"

# Test ArtStation (no API needed)
gallery-dl --config config/gallery-dl/config.json "https://www.artstation.com/artwork/example"
```

### Monitor Logs:
```bash
# Watch gallery-dl logs in real-time
tail -f logs/gallery-dl.log

# Check for unsupported URLs
cat logs/gallery-dl-unsupported.txt
```

---

## 🔧 Integration with Scraper

Gallery-dl is already integrated into the multi-method framework:

**File**: `scrapers/scraping_methods.py`
**Method**: `GalleryDlMethod` (priority 15)

**Supported Sources** (auto-detected):
- imgur, flickr, instagram, twitter, reddit
- deviantart, artstation, pixiv
- danbooru, gelbooru, tumblr, pinterest

**How it works**:
1. Multi-method framework extracts URLs for a source
2. If source matches gallery-dl supported sites, `GalleryDlMethod` is tried
3. gallery-dl downloads images using configured credentials
4. Files are saved to `downloads/{source}/` directory

---

## 📊 Expected Performance Gains

| Source | Current | With API Keys | Improvement |
|--------|---------|---------------|-------------|
| Reddit | 5% | 60-80% | +1200% |
| Imgur | 0% | 40-60% | NEW |
| Flickr | 0% | 50-70% | NEW |
| DeviantArt | 0% | 40-60% | NEW |
| Instagram | 0% | 30-50% | NEW |
| Twitter | 0% | 30-50% | NEW |
| Pinterest | 0% | 30-40% | NEW |
| Pixiv | 0% | 60-80% | NEW |

**Total Impact**: +7 major sources unlocked, +200-400 files per job

---

## 🔒 Security Best Practices

1. **Never commit API keys to git**
   - Add `config/gallery-dl/config.json` to `.gitignore`
   - Keep a template without credentials

2. **Use dedicated accounts**
   - Create separate accounts for scraping
   - Don't use your personal social media accounts
   - Reduces risk if rate-limited or banned

3. **Rate limiting**
   - gallery-dl has built-in rate limiting (`"rate": "1M"`)
   - Don't modify unless necessary
   - Respect API terms of service

4. **2FA handling**
   - Some services (Instagram) may require 2FA
   - Use app-specific passwords when available
   - May need to login manually first to save session

---

## 🔄 Updating Configuration

After adding API keys to `config/gallery-dl/config.json`:

1. **No server restart needed** - gallery-dl reads config on each run
2. **Test the source** - Use command-line test (see above)
3. **Verify in logs** - Check `logs/gallery-dl.log` for success
4. **Run scraper job** - Source should now work in web interface

---

## 📝 Configuration Template

For reference, here's the template with all available options:

```json
{
  "extractor": {
    "base-directory": "C:/inetpub/wwwroot/scraper/downloads",

    "reddit": {
      "enabled": true,
      "client-id": "REPLACE_ME",
      "client-secret": "REPLACE_ME",
      "user-agent": "EnhancedMediaScraper/3.0"
    },

    "imgur": {
      "enabled": true,
      "client-id": "REPLACE_ME"
    },

    "flickr": {
      "enabled": true,
      "api-key": "REPLACE_ME",
      "api-secret": "REPLACE_ME"
    },

    "deviantart": {
      "enabled": true,
      "client-id": "REPLACE_ME",
      "client-secret": "REPLACE_ME"
    },

    "twitter": {
      "enabled": true,
      "username": "REPLACE_ME",
      "password": "REPLACE_ME"
    },

    "instagram": {
      "enabled": true,
      "username": "REPLACE_ME",
      "password": "REPLACE_ME"
    },

    "pixiv": {
      "enabled": true,
      "username": "REPLACE_ME",
      "password": "REPLACE_ME"
    }
  }
}
```

---

## 📚 Additional Resources

- **gallery-dl Documentation**: https://github.com/mikf/gallery-dl
- **Supported Sites**: https://github.com/mikf/gallery-dl/blob/master/docs/supportedsites.md
- **Configuration Guide**: https://github.com/mikf/gallery-dl/blob/master/docs/configuration.rst

---

## ✅ Next Steps

1. **Register for Reddit API** (highest impact - 5 minutes)
2. **Register for Imgur API** (medium impact - 5 minutes)
3. **Test sources** with command-line
4. **Run scraper job** and monitor improvement
5. **Gradually add more API keys** as needed

**Estimated Time**: 20-30 minutes for top 3 sources
**Expected Result**: +200-300 files per job, major Reddit/Imgur improvement
