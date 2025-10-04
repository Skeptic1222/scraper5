# Comprehensive Test Plan: Bulk Download Functionality

**Application:** Enhanced Media Scraper v3.0
**Feature:** Bulk Download (`/api/media/bulk-download`)
**Date:** 2025-10-04
**Author:** Test Engineer (Claude Code)

---

## Executive Summary

This document outlines a comprehensive testing strategy for the bulk download functionality, covering unit tests, integration tests, and end-to-end tests using Playwright. The test suite validates 20+ scenarios including edge cases, performance, security, and user experience.

**Coverage Goal:** 85%+ code coverage for bulk download endpoint
**Test Duration:** ~15 minutes (unit) + ~30 minutes (E2E)
**Automation Level:** 100% automated

---

## 1. Feature Overview

### 1.1 Endpoint Details
- **URL:** `POST /scraper/api/media/bulk-download`
- **Authentication:** Required (Flask-Login session)
- **Input:** JSON body with `asset_ids` array
- **Output:** Streamed ZIP file with selected assets

### 1.2 Frontend Integration
- **Location:** `static/js/modules/asset-library-enhanced.js`
- **Single file:** Direct download via `/api/media/{id}/download`
- **Multiple files:** Calls bulk-download endpoint
- **UI Feedback:** Button shows "Creating ZIP (N files)..." during processing

### 1.3 Key Features
- Streams ZIP file to avoid memory issues
- Auto-deletes temporary ZIP after streaming
- Handles duplicate filenames with numbering (_1, _2, etc.)
- Supports both database-stored (MediaBlob) and filesystem-stored assets
- Returns headers: `X-Files-Added`, `X-Files-Failed`
- Access control: Users can only download their own assets (unless admin)

---

## 2. Test Scenarios

### 2.1 Core Functionality Tests

#### TC-01: Single File Download
**Type:** Unit Test
**Priority:** High
**File:** `test_bulk_download.py::test_01_single_file_download`

**Steps:**
1. Create 1 asset with MediaBlob
2. POST to endpoint with single asset ID
3. Verify response is ZIP file
4. Verify ZIP contains exactly 1 file
5. Verify headers: X-Files-Added=1, X-Files-Failed=0

**Expected Result:**
- Status: 200 OK
- Content-Type: application/zip
- ZIP contains single file with correct name

**Coverage:** Basic happy path

---

#### TC-02: Multiple Files Small Batch (2-5 assets)
**Type:** Unit Test
**Priority:** High
**File:** `test_bulk_download.py::test_02_multiple_files_small_batch`

**Steps:**
1. Create 3 assets with MediaBlobs
2. POST with 3 asset IDs
3. Verify ZIP contains all 3 files
4. Verify file contents match original data

**Expected Result:**
- Status: 200 OK
- ZIP contains 3 files
- All filenames preserved correctly

**Coverage:** Standard multi-file download

---

#### TC-03: Large Batch Download (50+ assets)
**Type:** Unit Test + Performance
**Priority:** High
**File:** `test_bulk_download.py::test_03_large_batch_streaming`

**Steps:**
1. Create 50 assets with MediaBlobs
2. POST with all 50 asset IDs
3. Measure response time
4. Verify ZIP integrity
5. Verify all 50 files present

**Expected Result:**
- Status: 200 OK
- Response time < 30 seconds
- ZIP file valid and contains all 50 files
- No timeout errors

**Coverage:** Performance, streaming functionality

---

### 2.2 Error Handling Tests

#### TC-04: Empty Selection
**Type:** Unit Test
**Priority:** High
**File:** `test_bulk_download.py::test_04_empty_selection`

**Steps:**
1. POST with empty `asset_ids` array
2. Verify error response

**Expected Result:**
- Status: 400 Bad Request
- Error message: "No assets specified"

**Coverage:** Input validation

---

#### TC-05: Missing asset_ids Key
**Type:** Unit Test
**Priority:** Medium
**File:** `test_bulk_download.py::test_05_missing_asset_ids_key`

**Steps:**
1. POST with JSON body: `{}`
2. Verify error handling

**Expected Result:**
- Status: 400 Bad Request
- Graceful error message

**Coverage:** Malformed request handling

---

#### TC-06: Non-existent Asset IDs
**Type:** Unit Test
**Priority:** High
**File:** `test_bulk_download.py::test_06_non_existent_assets`

**Steps:**
1. POST with fake asset IDs [99999, 99998, 99997]
2. Verify response

**Expected Result:**
- Status: 404 Not Found
- Error: "No files could be added to download"
- X-Files-Added: 0
- X-Files-Failed: 3

**Coverage:** Database query validation

---

#### TC-07: Mixed Valid and Invalid IDs
**Type:** Unit Test
**Priority:** Medium
**File:** `test_bulk_download.py::test_07_mixed_valid_invalid_assets`

**Steps:**
1. Create 2 valid assets
2. POST with 2 valid IDs + 2 invalid IDs
3. Verify partial success

**Expected Result:**
- Status: 200 OK (partial success)
- X-Files-Added: 2
- X-Files-Failed: 2
- ZIP contains 2 valid files

**Coverage:** Partial failure handling

---

### 2.3 Security & Permission Tests

#### TC-08: Access Permission Denied
**Type:** Unit Test
**Priority:** Critical
**File:** `test_bulk_download.py::test_08_access_permission_denied`

**Steps:**
1. Create asset owned by User A
2. Login as User B
3. Attempt to download User A's asset
4. Verify access denied

**Expected Result:**
- Status: 404 Not Found
- Asset filtered out due to permission check
- Error: "No files could be added"

**Coverage:** Authorization, access control

---

#### TC-17: Admin Access to Other Users' Assets
**Type:** Unit Test
**Priority:** High
**File:** `test_bulk_download.py::test_17_admin_access_other_users_assets`

**Steps:**
1. Create asset owned by regular user
2. Login as admin
3. Download the asset
4. Verify success

**Expected Result:**
- Status: 200 OK
- Admin can access any user's assets
- ZIP contains requested file

**Coverage:** Admin privileges

---

### 2.4 Edge Cases

#### TC-09: Duplicate Filenames
**Type:** Unit Test
**Priority:** High
**File:** `test_bulk_download.py::test_09_duplicate_filenames`

**Steps:**
1. Create 3 assets all named "duplicate.jpg"
2. Download all 3
3. Verify filename deduplication

**Expected Result:**
- ZIP contains:
  - `duplicate.jpg`
  - `duplicate_1.jpg`
  - `duplicate_2.jpg`

**Coverage:** Filename collision handling

---

#### TC-10: Special Characters in Filenames
**Type:** Unit Test
**Priority:** Medium
**File:** `test_bulk_download.py::test_10_special_characters_in_filename`

**Steps:**
1. Create assets with names:
   - `test_emoji_🎉.jpg`
   - `test_unicode_日本語.jpg`
   - `test_spaces in name.jpg`
   - `test-dashes-and_underscores.jpg`
2. Download all
3. Verify filenames preserved

**Expected Result:**
- Status: 200 OK
- All filenames correctly preserved in ZIP
- Special characters/Unicode handled properly

**Coverage:** Encoding, internationalization

---

#### TC-11: File Stored on Filesystem
**Type:** Unit Test
**Priority:** Medium
**File:** `test_bulk_download.py::test_11_file_stored_on_filesystem`

**Steps:**
1. Create asset with file on disk (not in MediaBlob)
2. Download asset
3. Verify file read from filesystem

**Expected Result:**
- Status: 200 OK
- File read from `asset.file_path`
- Added to ZIP successfully

**Coverage:** Filesystem storage path

---

#### TC-12: Missing Filesystem File
**Type:** Unit Test
**Priority:** Medium
**File:** `test_bulk_download.py::test_12_missing_filesystem_file`

**Steps:**
1. Create asset pointing to non-existent file path
2. Attempt download
3. Verify graceful failure

**Expected Result:**
- Status: 404 Not Found
- File skipped
- X-Files-Failed: 1
- Warning logged

**Coverage:** File not found handling

---

#### TC-13: Mixed Storage Types
**Type:** Unit Test
**Priority:** Medium
**File:** `test_bulk_download.py::test_13_mixed_storage_types`

**Steps:**
1. Create asset in MediaBlob
2. Create asset on filesystem
3. Download both
4. Verify both included

**Expected Result:**
- Status: 200 OK
- ZIP contains files from both storage types
- X-Files-Added: 2

**Coverage:** Hybrid storage support

---

### 2.5 Data Integrity Tests

#### TC-14: Content-Disposition Header
**Type:** Unit Test
**Priority:** Medium
**File:** `test_bulk_download.py::test_14_content_disposition_header`

**Steps:**
1. Download assets
2. Verify Content-Disposition header format

**Expected Result:**
- Header present: `attachment; filename="assets_download_YYYYMMDD_HHMMSS.zip"`
- Timestamp in filename
- Proper attachment directive

**Coverage:** HTTP headers

---

#### TC-15: ZIP File Integrity
**Type:** Unit Test
**Priority:** High
**File:** `test_bulk_download.py::test_15_zip_file_integrity`

**Steps:**
1. Download multiple assets
2. Test ZIP validity with `zipfile.testzip()`
3. Extract and verify file contents
4. Compare checksums

**Expected Result:**
- ZIP passes integrity test
- All files extractable
- File contents match original data

**Coverage:** Data integrity, ZIP correctness

---

#### TC-19: Video Files in ZIP
**Type:** Unit Test
**Priority:** Medium
**File:** `test_bulk_download.py::test_19_video_files_in_zip`

**Steps:**
1. Create video asset (.mp4)
2. Download
3. Verify video added to ZIP

**Expected Result:**
- Status: 200 OK
- Video file in ZIP
- MIME type preserved

**Coverage:** Video file handling

---

#### TC-20: Mixed Media Types
**Type:** Unit Test
**Priority:** Medium
**File:** `test_bulk_download.py::test_20_mixed_media_types`

**Steps:**
1. Create 2 images + 1 video
2. Download all
3. Verify all media types in ZIP

**Expected Result:**
- ZIP contains images and videos
- Correct MIME types
- All files valid

**Coverage:** Multi-format support

---

### 2.6 Concurrency & Performance

#### TC-18: Concurrent Download Safety
**Type:** Unit Test
**Priority:** Medium
**File:** `test_bulk_download.py::test_18_concurrent_download_safety`

**Steps:**
1. Simulate 3 concurrent download requests
2. Verify each gets unique temp file
3. Verify no conflicts

**Expected Result:**
- All 3 requests succeed
- Each gets separate ZIP file
- No race conditions

**Coverage:** Thread safety, temp file management

---

### 2.7 Input Validation

#### TC-16: Malformed JSON
**Type:** Unit Test
**Priority:** Low
**File:** `test_bulk_download.py::test_16_malformed_json`

**Steps:**
1. POST with invalid JSON: `"not valid json"`
2. Verify error handling

**Expected Result:**
- Status: 400 or 500
- Graceful error message
- No server crash

**Coverage:** JSON parsing error handling

---

## 3. End-to-End Tests (Playwright)

### 3.1 User Workflow Tests

#### E2E-01: Single File Direct Download
**Type:** E2E (Browser)
**Priority:** High
**File:** `test_bulk_download_e2e.py::test_01_single_file_direct_download`

**Steps:**
1. Login to application
2. Navigate to asset library
3. Check 1 asset checkbox
4. Click "Download Selected"
5. Verify file downloads (NOT as ZIP)

**Expected Result:**
- Download initiates
- File saves to disk
- Filename preserved
- Not a ZIP file

**Coverage:** Frontend single file path

---

#### E2E-02: Multiple Files ZIP Download
**Type:** E2E (Browser)
**Priority:** High
**File:** `test_bulk_download_e2e.py::test_02_multiple_files_zip_download`

**Steps:**
1. Login
2. Select 3 assets
3. Verify selection count shows "3"
4. Click "Download Selected"
5. Verify button shows "Creating ZIP (3 files)..."
6. Wait for ZIP download
7. Extract and verify ZIP contents

**Expected Result:**
- ZIP file downloads
- Contains exactly 3 files
- ZIP valid and extractable
- Filenames match selected assets

**Coverage:** Frontend multi-file path, UI feedback

---

#### E2E-03: Large Batch Download
**Type:** E2E (Browser)
**Priority:** Medium
**File:** `test_bulk_download_e2e.py::test_03_large_batch_download`

**Steps:**
1. Login
2. Click "Select All" checkbox
3. Verify 50+ assets selected
4. Click download
5. Wait for completion (timeout: 60s)

**Expected Result:**
- Large ZIP downloads successfully
- No timeout errors
- File size reasonable
- Browser doesn't freeze

**Coverage:** Performance, large dataset handling

---

#### E2E-04: Empty Selection Handling
**Type:** E2E (Browser)
**Priority:** Medium
**File:** `test_bulk_download_e2e.py::test_04_empty_selection_no_download`

**Steps:**
1. Navigate to asset library
2. Ensure no assets selected
3. Verify download button disabled/hidden

**Expected Result:**
- Download button disabled or not visible
- User cannot trigger download with empty selection

**Coverage:** UI validation

---

#### E2E-05: Selection State Management
**Type:** E2E (Browser)
**Priority:** Medium
**File:** `test_bulk_download_e2e.py::test_05_deselect_and_reselect`

**Steps:**
1. Select asset 1 → count = 1
2. Select asset 2 → count = 2
3. Deselect asset 1 → count = 1
4. Reselect asset 1 → count = 2

**Expected Result:**
- Selection count updates correctly
- State maintained properly
- Download button reflects current selection

**Coverage:** Frontend state management

---

#### E2E-06: Download Button Feedback
**Type:** E2E (Browser)
**Priority:** High
**File:** `test_bulk_download_e2e.py::test_06_download_button_feedback`

**Steps:**
1. Select multiple assets
2. Click download button
3. Verify button text changes
4. Verify spinner/loading indicator shows

**Expected Result:**
- Button disabled during download
- Text shows "Creating ZIP..." or similar
- Spinner icon visible
- Button re-enabled after download

**Coverage:** User experience, visual feedback

---

#### E2E-07: Network Error Handling
**Type:** E2E (Browser)
**Priority:** Medium
**File:** `test_bulk_download_e2e.py::test_07_network_error_handling`

**Steps:**
1. Intercept API request and force failure
2. Attempt download
3. Verify error handling

**Expected Result:**
- Error message shown to user
- Button returns to enabled state
- No silent failure

**Coverage:** Error user experience

---

#### E2E-08: Concurrent User Downloads
**Type:** E2E (Browser)
**Priority:** Low
**File:** `test_bulk_download_e2e.py::test_08_concurrent_user_downloads`

**Steps:**
1. Open 2 browser contexts
2. Both users select assets
3. Both click download simultaneously
4. Verify both succeed

**Expected Result:**
- Both downloads complete
- No interference
- Each gets correct files

**Coverage:** Multi-user scenario

---

#### E2E-09: Select All Functionality
**Type:** E2E (Browser)
**Priority:** Medium
**File:** `test_bulk_download_e2e.py::test_09_select_all_functionality`

**Steps:**
1. Click "Select All" checkbox
2. Verify all assets selected
3. Click "Select All" again to deselect
4. Verify all deselected

**Expected Result:**
- Select All works both directions
- Selection count accurate
- Individual checkboxes sync correctly

**Coverage:** Bulk selection UI

---

#### E2E-10: Filename Preservation
**Type:** E2E (Browser)
**Priority:** Medium
**File:** `test_bulk_download_e2e.py::test_10_download_preserves_filename`

**Steps:**
1. Download multiple assets
2. Verify ZIP filename format
3. Extract timestamp from filename

**Expected Result:**
- Filename: `assets_download_YYYYMMDD_HHMMSS.zip`
- Timestamp accurate (within 1 minute)
- No special characters breaking filename

**Coverage:** Filename generation

---

## 4. Test Environment Setup

### 4.1 Prerequisites

**Software:**
- Python 3.8+
- pytest 7.0+
- pytest-asyncio
- playwright
- Flask test dependencies

**Database:**
- SQL Server Express OR SQLite (test mode)
- Clean test database

**Browser (E2E):**
- Chromium (installed via Playwright)
- Optional: Firefox, WebKit

### 4.2 Environment Variables

Create `.env.test` file:

```env
FLASK_ENV=testing
SECRET_KEY=test-secret-key-12345
DATABASE_URL=sqlite:///test.db
ADMIN_EMAIL=admin@example.com

# Disable CSRF for testing
WTF_CSRF_ENABLED=False

# Google OAuth (mock in tests)
GOOGLE_CLIENT_ID=test-client-id
GOOGLE_CLIENT_SECRET=test-secret
```

### 4.3 Test Data Setup

**Generate test data:**
```bash
cd C:\inetpub\wwwroot\scraper
python tests/test_data_setup.py --generate
```

**Clean up test data:**
```bash
python tests/test_data_setup.py --cleanup
```

**Generate with large batch:**
```bash
python tests/test_data_setup.py --generate --large-batch
```

---

## 5. Running Tests

### 5.1 Unit Tests

**Run all unit tests:**
```bash
pytest tests/test_bulk_download.py -v
```

**Run specific test:**
```bash
pytest tests/test_bulk_download.py::TestBulkDownload::test_01_single_file_download -v
```

**Run with coverage:**
```bash
pytest tests/test_bulk_download.py --cov=blueprints.assets --cov-report=html
```

**Expected Duration:** ~5-10 minutes

### 5.2 E2E Tests

**Install Playwright browsers:**
```bash
playwright install chromium
```

**Run E2E tests:**
```bash
pytest tests/test_bulk_download_e2e.py -v
```

**Run with visible browser (debugging):**
```bash
pytest tests/test_bulk_download_e2e.py -v --headed
```

**Run specific E2E test:**
```bash
pytest tests/test_bulk_download_e2e.py::TestBulkDownloadE2E::test_02_multiple_files_zip_download -v
```

**Expected Duration:** ~20-30 minutes

### 5.3 Full Test Suite

**Run everything:**
```bash
pytest tests/test_bulk_download*.py -v --cov --html=report.html
```

---

## 6. Expected Coverage

### 6.1 Code Coverage Targets

**File: `blueprints/assets.py` (lines 502-621)**
- **Target:** 85%+
- **Critical paths:** 100%
  - Empty asset_ids check (line 512-513)
  - Access control (lines 537-543)
  - File data retrieval (lines 546-556)
  - Duplicate filename handling (lines 563-567)
  - Streaming generator (lines 591-602)

**File: `static/js/modules/asset-library-enhanced.js` (lines 486-656)**
- **Target:** 80%+
- **Critical paths:**
  - Single vs. multiple file logic (lines 569-584)
  - API call (lines 594-603)
  - Error handling (lines 607-610, 644-645)
  - Download trigger (lines 618-640)

### 6.2 Coverage Report

**Generate HTML report:**
```bash
pytest tests/test_bulk_download.py --cov=blueprints.assets --cov=models --cov-report=html
```

**View report:**
```
Open: htmlcov/index.html
```

**Expected metrics:**
- Line coverage: 85%+
- Branch coverage: 75%+
- Function coverage: 90%+

---

## 7. Test Dependencies

### 7.1 Python Packages

Add to `requirements-dev.txt`:

```txt
# Testing Framework
pytest==7.4.3
pytest-asyncio==0.21.1
pytest-cov==4.1.0
pytest-html==4.1.1
pytest-timeout==2.2.0

# Browser Automation
playwright==1.40.0

# Mocking and Fixtures
pytest-mock==3.12.0
faker==20.1.0

# Flask Testing
Flask-Testing==0.8.1
```

**Install:**
```bash
pip install -r requirements-dev.txt
```

### 7.2 Playwright Setup

```bash
# Install Playwright
pip install playwright

# Install browsers
playwright install chromium

# Optional: Install all browsers
playwright install
```

---

## 8. Test Maintenance

### 8.1 Continuous Integration

**GitHub Actions workflow** (`.github/workflows/test.yml`):

```yaml
name: Bulk Download Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -r requirements-dev.txt
          playwright install chromium

      - name: Setup test data
        run: python tests/test_data_setup.py --generate

      - name: Run unit tests
        run: pytest tests/test_bulk_download.py -v --cov --cov-report=xml

      - name: Run E2E tests
        run: pytest tests/test_bulk_download_e2e.py -v

      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

### 8.2 Test Data Refresh

**Weekly:** Regenerate test data to catch schema changes
```bash
python tests/test_data_setup.py --cleanup
python tests/test_data_setup.py --generate
```

### 8.3 Browser Updates

**Monthly:** Update Playwright browsers
```bash
playwright install --with-deps
```

---

## 9. Known Issues & Limitations

### 9.1 Current Limitations

1. **OAuth Mocking:** E2E tests require manual OAuth setup or mocking
2. **Large Files:** Tests use small fake data; real-world large files not tested
3. **Network Simulation:** Limited network condition testing (latency, packet loss)
4. **Browser Coverage:** Primary testing on Chromium; Firefox/Safari optional

### 9.2 Future Enhancements

1. **Load Testing:** Add locust/k6 for concurrent user load
2. **Accessibility:** Add Pa11y/axe-core tests for WCAG compliance
3. **Visual Regression:** Integrate Percy/BackstopJS for UI changes
4. **Security Scanning:** Add OWASP ZAP for vulnerability testing
5. **Performance Profiling:** Add Flask-Profiler for endpoint optimization

---

## 10. Success Criteria

### 10.1 Test Pass Criteria

- **Unit Tests:** 100% pass rate
- **E2E Tests:** 95%+ pass rate (allowing for flaky network tests)
- **Code Coverage:** 85%+ for bulk download endpoint
- **Performance:** Large batch (50+ files) completes in < 30 seconds
- **Zero Critical Bugs:** No security vulnerabilities, no data loss

### 10.2 Definition of Done

- [ ] All 20 unit tests passing
- [ ] All 10 E2E tests passing
- [ ] Code coverage meets 85% threshold
- [ ] Test documentation complete
- [ ] CI/CD pipeline configured
- [ ] Test data setup automated
- [ ] Known issues documented

---

## 11. Appendix

### 11.1 Test File Structure

```
tests/
├── test_bulk_download.py           # 20 unit tests
├── test_bulk_download_e2e.py       # 10 E2E tests
├── test_data_setup.py              # Test data generator
├── BULK_DOWNLOAD_TEST_PLAN.md      # This document
├── conftest.py                     # Pytest fixtures (shared)
└── test_downloads/                 # E2E download destination
```

### 11.2 Related Files

**Backend:**
- `C:\inetpub\wwwroot\scraper\blueprints\assets.py` (lines 502-621)
- `C:\inetpub\wwwroot\scraper\models.py` (Asset, MediaBlob models)

**Frontend:**
- `C:\inetpub\wwwroot\scraper\static\js\modules\asset-library-enhanced.js` (lines 486-656)

**Configuration:**
- `C:\inetpub\wwwroot\scraper\requirements-dev.txt`
- `C:\inetpub\wwwroot\scraper\.env.test`

### 11.3 Glossary

- **MediaBlob:** Database model storing file binary data
- **Asset:** Database model with file metadata
- **Playwright:** Browser automation framework
- **pytest:** Python testing framework
- **Coverage:** Percentage of code executed during tests
- **E2E:** End-to-end (full user workflow testing)
- **Fixture:** Reusable test setup/teardown code

---

**Document Version:** 1.0
**Last Updated:** 2025-10-04
**Status:** Ready for Implementation
