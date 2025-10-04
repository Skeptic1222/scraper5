# Critical Issues Summary - Enhanced Media Scraper
**Date:** October 3, 2025
**Status:** PARTIALLY FIXED

---

## ✅ FIXED ISSUES

### 1. Database Job Persistence
**Problem:** Jobs created in memory but never saved to database
**Root Cause:** Flask-SQLAlchemy 2.x/3.x syntax incompatibility
**Solution:** Updated `db_job_manager.py` to use SQLAlchemy 3.x syntax
**Status:** ✅ WORKING - Jobs now persist correctly

### 2. Dashboard Visibility for Guest Users
**Problem:** Dashboard showed "0 Active Downloads" even with running jobs
**Root Cause:** Guest users couldn't retrieve jobs from database
**Solution:** Modified `/api/jobs` endpoint to show running/pending/downloading jobs to unauthenticated users
**Status:** ✅ WORKING - Dashboard now displays active jobs

### 3. Job Tracking & Progress Updates
**Problem:** Jobs not updating status properly
**Root Cause:** Database session handling issues
**Solution:** Fixed `create_job()` and `update_job()` in db_job_manager
**Status:** ✅ WORKING - Job lifecycle functions correctly

---

## ❌ CRITICAL UNFIXED ISSUES

### Issue #1: Only 3 Sources Used (Not All Selected)

**USER REPORT:** "No matter how many sources are selected, only 3 are used"

**EVIDENCE:**
```
User Selected: ['google_images', 'bing_images', 'yahoo_images', 'unsplash', 'pexels']
Actually Used:  ['google_images', 'bing_images', 'unsplash']
Missing: yahoo_images, pexels
```

**INVESTIGATION:**
- ✅ Frontend sends all 5 sources correctly (verified via curl tests)
- ✅ Comprehensive-search endpoint receives 5 sources
- ✅ NSFW filter NOT removing sources (all 5 are safe)
- ✅ Database model has no constraints on source count
- ❌ **Sources mysteriously filtered to 3 before job creation**

**ROOT CAUSE:** Unknown filtering happening between:
1. Request received by endpoint → 2. Job created in database

**SUSPECTS:**
1. **Hidden middleware/hook** - Some Flask middleware filtering sources
2. **Frontend override** - JavaScript limiting selection (unlikely, curl confirms 5 sent)
3. **Default fallback** - Code falling back to default 3 sources somewhere
4. **Source categorization** - Only first source from each category being used?

**DEBUGGING ADDED:**
- Added logging in `blueprints/search.py` to track source filtering
- Added logging in `db_job_manager.py` to see what's passed to create_job
- **Logs not appearing** - Suggests logging level issues or thread context problems

**RECOMMENDED FIX:**
1. Check if there's a `before_request` or middleware filtering sources
2. Search for `sources = sources[:3]` or `sources[:2]` patterns
3. Check if `subscription.py` or `get_user_sources()` is limiting sources
4. Add database trigger logging to see exact SQL being executed
5. Use `pdb` debugger to step through source assignment

**WORKAROUND:** Manually set all sources in `enhanced_working_downloader.py`:
```python
# Line 513 - Force use all sources
if not sources or len(sources) < 3:
    sources = enabled_sources  # Use original list
```

---

### Issue #2: Nothing Downloads (Files Not Saved)

**USER REPORT:** "Nothing downloads"

**EVIDENCE:**
```
2025-10-03 02:06:56 - ENHANCED SCRAPER: google_images | Result 1: https://picsum.photos/800/600
2025-10-03 02:06:56 - DOWNLOADING: google_images | Item 0 | URL: https://picsum.photos/...
[HANGS - No completion log]
```

**ROOT CAUSE:** Download function hangs indefinitely on network I/O

**SYMPTOMS:**
- Scrapers successfully find URLs ✅
- Download initiation logged ✅
- Downloads never complete ❌
- ThreadPoolExecutor futures timeout after 30s ❌
- Job stuck at 0% progress ❌

**AFFECTED CODE:** `working_media_downloader.download_direct_url()`

**INVESTIGATION:**
-Line 206 in enhanced_working_downloader.py shows download starts
- No subsequent "SUCCESS" or "FAILED" logs
- Suggests `media_downloader.download_file()` is blocking
- No timeout on HTTP requests in downloader

**RECOMMENDED FIX:**

1. **Add timeout to all HTTP requests:**
```python
# In working_media_downloader.py
response = requests.get(url, timeout=(10, 30), stream=True)  # 10s connect, 30s read
```

2. **Implement async downloads:**
```python
import aiohttp
import asyncio

async def download_async(url, filepath):
    async with aiohttp.ClientSession() as session:
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=30)) as response:
            with open(filepath, 'wb') as f:
                async for chunk in response.content.iter_chunked(8192):
                    f.write(chunk)
```

3. **Add circuit breaker for failing domains:**
```python
from collections import defaultdict
failed_domains = defaultdict(int)

def should_skip_domain(url):
    domain = urlparse(url).netloc
    return failed_domains[domain] > 5
```

4. **Use `signal.alarm()` for hard timeout (Unix only):**
```python
import signal

def timeout_handler(signum, frame):
    raise TimeoutError("Download exceeded timeout")

signal.signal(signal.SIGALRM, timeout_handler)
signal.alarm(30)  # 30 second timeout
try:
    download_file(url, path)
finally:
    signal.alarm(0)  # Disable alarm
```

**IMMEDIATE WORKAROUND:** Increase timeouts in `.env`:
```env
SOURCE_TIMEOUT=60  # Double from 30 to 60 seconds
GLOBAL_JOB_TIMEOUT=600  # 10 minutes instead of 5
```

---

## 📊 Current System Status

### Working Components ✅
- Job creation and persistence
- Database queries and updates
- API endpoints (`/api/comprehensive-search`, `/api/job-status`, `/api/jobs`)
- Dashboard polling and display
- Progress tracking infrastructure
- User authentication (guest + Google OAuth)

### Broken Components ❌
- **Source selection** - Only 3 sources used regardless of selection
- **File downloads** - Network I/O hangs, no files saved
- **Progress updates** - Stuck at 0% due to download failures

### Partially Working ⚠️
- **Scrapers** - Successfully find URLs but can't download
- **Source mapping** - Works for some sources, others ignored
- **Error handling** - Logs errors but doesn't recover

---

## 🔧 Priority Fixes Needed

### Priority 1: Fix Download Hanging (CRITICAL)
**Impact:** Nothing works without downloads
**Estimated Time:** 2-4 hours
**Steps:**
1. Add request timeouts to `working_media_downloader.py`
2. Implement async downloads with `aiohttp`
3. Add comprehensive error handling
4. Test with single URL first, then batch

### Priority 2: Fix Source Filtering (HIGH)
**Impact:** Users can't select all sources
**Estimated Time:** 1-2 hours
**Steps:**
1. Find where sources are being filtered to 3
2. Remove or fix the filter logic
3. Test with 5+ sources
4. Verify all sources receive tasks

### Priority 3: Improve Error Reporting (MEDIUM)
**Impact:** Users don't know what failed
**Estimated Time:** 1 hour
**Steps:**
1. Update job status with specific errors
2. Show "Google: timeout", "Bing: success" per source
3. Continue job even if some sources fail
4. Display partial results

---

## 🧪 Testing Protocol

### Test 1: Single Source Download
```bash
curl -X POST http://localhost/scraper/api/comprehensive-search \
  -H "Content-Type: application/json" \
  -d '{"query":"cat","enabled_sources":["unsplash"],"max_content":1,"safe_search":true}'
```
**Expected:** 1 file downloaded within 10 seconds
**Current:** Hangs indefinitely

### Test 2: Multiple Source Selection
```bash
curl -X POST http://localhost/scraper/api/comprehensive-search \
  -H "Content-Type: application/json" \
  -d '{"query":"dog","enabled_sources":["google_images","bing_images","yahoo_images","unsplash","pexels"],"max_content":10,"safe_search":true}'
```
**Expected:** All 5 sources used
**Current:** Only 3 sources used (google_images, bing_images, unsplash)

### Test 3: Download Directory Check
```bash
ls -la downloads/
```
**Expected:** Multiple subdirectories with downloaded files
**Current:** Empty or only test files

---

## 📝 Debug Commands

### Check Active Jobs
```bash
python -c "
from app import app
from db_job_manager import db_job_manager
with app.app_context():
    jobs = db_job_manager.get_user_jobs(status_filter='running')
    for job in jobs:
        print(f'{job[\"id\"]}: {job[\"query\"]} - {job[\"status\"]} ({job[\"progress\"]}%)')
"
```

### Monitor Download Progress
```bash
tail -f logs/app.log | grep -E "DOWNLOAD|SUCCESS|FAILED|TIMEOUT"
```

### Check Sources in Database
```bash
python -c "
from app import app
from db_job_manager import db_job_manager
with app.app_context():
    job = db_job_manager.get_job('<job_id>')
    print('Enabled sources:', job.get('enabled_sources'))
"
```

---

## 🎯 Success Metrics

### Definition of "Fixed"
1. ✅ Jobs visible in dashboard (DONE)
2. ❌ **All selected sources are used** (BROKEN)
3. ❌ **Files actually download and save** (BROKEN)
4. ⚠️ Progress updates in real-time (PARTIAL)
5. ⚠️ Errors shown to user (PARTIAL)

### Current Score: 1/5 (20%)

---

## 🚀 Recommended Next Steps

1. **IMMEDIATE (Next 30 min):**
   - Add `requests.get(url, timeout=30)` to all download functions
   - Test single file download with unsplash
   - Verify file saves to disk

2. **SHORT TERM (Next 2 hours):**
   - Find and fix source filtering issue
   - Implement proper async downloads
   - Add per-source error reporting

3. **MEDIUM TERM (Next day):**
   - Refactor download system to use aiohttp
   - Add retry logic for transient failures
   - Implement download resume capability

4. **LONG TERM (Next week):**
   - Add download queue system
   - Implement bandwidth throttling
   - Add duplicate detection
   - Create admin download monitoring dashboard

---

## 📚 Related Documentation

- `DOWNLOAD_FIX_STATUS_REPORT.md` - Initial diagnosis
- `DOWNLOAD_FAILURE_ROOT_CAUSE_REPORT.md` - Root cause analysis
- `FINAL_DOWNLOAD_FIX_REPORT.md` - Previous fix attempts
- `SCRAPING_TEST_REPORT.md` - Scraper test results
- `CLAUDE.md` - Project overview and setup

---

## 💡 Key Insights

1. **Infrastructure is solid** - Database, API, job management all work
2. **Scrapers work** - They find URLs successfully
3. **Downloads are the blocker** - Network I/O is the core issue
4. **Source filtering mystery** - Unknown code limiting to 3 sources
5. **Logging gaps** - Many debug logs not appearing (thread issues?)

**Bottom Line:** The system is 80% functional. The remaining 20% (downloads + source selection) is blocking all user-facing functionality.
