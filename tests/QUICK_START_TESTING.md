# Quick Start: Bulk Download Testing

**Last Updated:** 2025-10-04
**Estimated Setup Time:** 15 minutes

---

## Prerequisites Check

Before you start, ensure you have:

- [ ] Python 3.8+ installed
- [ ] Flask application running (test mode)
- [ ] Database accessible (SQLite or SQL Server)
- [ ] Admin access to install packages

---

## Step 1: Install Test Dependencies (5 min)

### Option A: Install Everything
```bash
cd C:\inetpub\wwwroot\scraper
pip install -r requirements-dev.txt
playwright install chromium
```

### Option B: Install Only Unit Testing
```bash
pip install pytest pytest-cov pytest-asyncio pytest-mock
```

### Option C: Add E2E Testing Later
```bash
pip install playwright
playwright install chromium
```

---

## Step 2: Generate Test Data (2 min)

```bash
# Generate standard test data (20 images, 10 videos, edge cases)
python tests/test_data_setup.py --generate

# Or with large batch (100+ assets for performance testing)
python tests/test_data_setup.py --generate --large-batch
```

**Expected Output:**
```
============================================================
GENERATING TEST DATA FOR BULK DOWNLOAD TESTS
============================================================

✓ Created test users:
  - bulktest1@example.com (ID: 123)
  - bulktest2@example.com (ID: 124)
  - admin@example.com (ID: 125)

✓ Created 20 image assets for bulktest1@example.com
✓ Created 10 video assets for bulktest1@example.com

✓ Created 5 assets with duplicate filenames
✓ Created 10 assets with special character filenames

✓ Created mixed ownership assets:
  - User 1: 5 assets
  - User 2: 5 assets

============================================================
TEST DATA GENERATION COMPLETE
============================================================
```

---

## Step 3: Run Unit Tests (5 min)

### Quick Smoke Test (3 tests, ~30 seconds)
```bash
pytest tests/test_bulk_download.py::TestBulkDownload::test_01_single_file_download -v
pytest tests/test_bulk_download.py::TestBulkDownload::test_02_multiple_files_small_batch -v
pytest tests/test_bulk_download.py::TestBulkDownload::test_04_empty_selection -v
```

### Run All Unit Tests (~5 minutes)
```bash
pytest tests/test_bulk_download.py -v
```

### Run with Coverage Report
```bash
pytest tests/test_bulk_download.py --cov=blueprints.assets --cov-report=html
```

**View Coverage:**
```
Open in browser: htmlcov/index.html
```

---

## Step 4: Run E2E Tests (Optional, 20 min)

### Prerequisites for E2E
1. Flask server must be running:
```bash
# In separate terminal
cd C:\inetpub\wwwroot\scraper
python app.py
```

2. Login credentials configured (or OAuth mocked)

### Run E2E Tests
```bash
# Run with visible browser (debugging)
pytest tests/test_bulk_download_e2e.py -v --headed

# Run headless (CI/CD mode)
pytest tests/test_bulk_download_e2e.py -v
```

### Run Single E2E Test
```bash
pytest tests/test_bulk_download_e2e.py::TestBulkDownloadE2E::test_02_multiple_files_zip_download -v --headed
```

---

## Step 5: Review Results

### Test Summary
After tests complete, you'll see:

```
============================================================ test session starts ============================================================
platform win32 -- Python 3.10.11, pytest-7.4.3
collected 20 items

tests/test_bulk_download.py::TestBulkDownload::test_01_single_file_download PASSED                                                   [  5%]
tests/test_bulk_download.py::TestBulkDownload::test_02_multiple_files_small_batch PASSED                                             [ 10%]
tests/test_bulk_download.py::TestBulkDownload::test_03_large_batch_streaming PASSED                                                  [ 15%]
...
tests/test_bulk_download.py::TestBulkDownload::test_20_mixed_media_types PASSED                                                      [100%]

============================================================ 20 passed in 87.23s ============================================================
```

### Coverage Report
```
Name                        Stmts   Miss  Cover
-----------------------------------------------
blueprints/assets.py          120     12    90%
models.py                     425     45    89%
-----------------------------------------------
TOTAL                         545     57    90%
```

---

## Common Commands Reference

### Test Selection

**Run by marker:**
```bash
# Only unit tests
pytest -m unit

# Only E2E tests
pytest -m e2e

# Only slow tests
pytest -m slow
```

**Run by keyword:**
```bash
# All download-related tests
pytest -k download

# All duplicate filename tests
pytest -k duplicate
```

**Run specific test:**
```bash
pytest tests/test_bulk_download.py::TestBulkDownload::test_09_duplicate_filenames
```

### Output Control

**Show print statements:**
```bash
pytest tests/test_bulk_download.py -s
```

**Stop on first failure:**
```bash
pytest tests/test_bulk_download.py -x
```

**Run last failed tests:**
```bash
pytest --lf
```

**Show detailed output:**
```bash
pytest tests/test_bulk_download.py -vv
```

### Coverage

**Text report:**
```bash
pytest --cov=blueprints.assets --cov-report=term
```

**HTML report:**
```bash
pytest --cov=blueprints.assets --cov-report=html
```

**XML report (for CI/CD):**
```bash
pytest --cov=blueprints.assets --cov-report=xml
```

**Missing lines only:**
```bash
pytest --cov=blueprints.assets --cov-report=term-missing
```

---

## Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'pytest'"
**Solution:**
```bash
pip install pytest
```

### Issue: "No module named 'app'"
**Solution:**
```bash
# Ensure you're in the correct directory
cd C:\inetpub\wwwroot\scraper
# Or add to PYTHONPATH
set PYTHONPATH=C:\inetpub\wwwroot\scraper
```

### Issue: "Database locked" (SQLite)
**Solution:**
```bash
# Close all connections to test.db
# Or use in-memory database (already configured in conftest.py)
```

### Issue: E2E tests fail with "Target closed"
**Solution:**
```bash
# Ensure Flask server is running
# Check URL in test matches your server (default: http://localhost/scraper)
```

### Issue: "Playwright browser not found"
**Solution:**
```bash
playwright install chromium
```

### Issue: Tests pass but coverage is 0%
**Solution:**
```bash
# Specify correct source directory
pytest --cov=blueprints --cov-report=html
```

---

## Test Data Management

### Clean Up Old Test Data
```bash
python tests/test_data_setup.py --cleanup
```

### Regenerate Fresh Test Data
```bash
python tests/test_data_setup.py --cleanup
python tests/test_data_setup.py --generate
```

### Check Test Data in Database
```bash
# SQLite
sqlite3 scraper.db "SELECT COUNT(*) FROM assets WHERE user_id IN (SELECT id FROM users WHERE email LIKE '%bulktest%');"

# SQL Server
sqlcmd -S .\SQLEXPRESS -d Scraped -Q "SELECT COUNT(*) FROM assets WHERE user_id IN (SELECT id FROM users WHERE email LIKE '%bulktest%')"
```

---

## CI/CD Integration

### GitHub Actions
Add to `.github/workflows/test.yml`:

```yaml
name: Test Bulk Download

on: [push, pull_request]

jobs:
  test:
    runs-on: windows-latest

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

      - name: Generate test data
        run: python tests/test_data_setup.py --generate

      - name: Run tests
        run: pytest tests/test_bulk_download.py --cov --cov-report=xml

      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml
```

### Local Pre-commit Hook
Create `.git/hooks/pre-commit`:

```bash
#!/bin/sh
# Run bulk download tests before commit

echo "Running bulk download tests..."
pytest tests/test_bulk_download.py -x

if [ $? -ne 0 ]; then
    echo "Tests failed! Commit aborted."
    exit 1
fi

echo "Tests passed!"
```

Make executable:
```bash
chmod +x .git/hooks/pre-commit
```

---

## Performance Benchmarking

### Measure Test Execution Time
```bash
pytest tests/test_bulk_download.py --durations=10
```

**Output:**
```
========================================== slowest 10 durations ==========================================
15.23s call     tests/test_bulk_download.py::TestBulkDownload::test_03_large_batch_streaming
5.67s call      tests/test_bulk_download.py::TestBulkDownload::test_13_mixed_storage_types
2.34s call      tests/test_bulk_download.py::TestBulkDownload::test_02_multiple_files_small_batch
...
```

### Profile Specific Test
```bash
pytest tests/test_bulk_download.py::TestBulkDownload::test_03_large_batch_streaming --profile
```

---

## Next Steps

After successfully running tests:

1. **Review Coverage Report**
   - Open `htmlcov/index.html`
   - Identify uncovered lines
   - Add tests for edge cases

2. **Check Test Plan**
   - Read `tests/BULK_DOWNLOAD_TEST_PLAN.md`
   - Verify all scenarios tested

3. **Add Custom Tests**
   - Create `test_bulk_download_custom.py`
   - Add project-specific scenarios

4. **Set Up CI/CD**
   - Configure GitHub Actions / Azure Pipelines
   - Add automated testing to PR workflow

5. **Performance Tuning**
   - Run large batch tests
   - Optimize slow endpoints
   - Add caching if needed

---

## Resources

- **Full Test Plan:** `tests/BULK_DOWNLOAD_TEST_PLAN.md`
- **Pytest Docs:** https://docs.pytest.org/
- **Playwright Docs:** https://playwright.dev/python/
- **Coverage Docs:** https://coverage.readthedocs.io/

---

## Support

**Issues with tests?**
1. Check `tests/test_output.log` for detailed logs
2. Run with `-vv -s` for verbose output
3. Review test plan for expected behavior
4. Check database has test data

**Need help?**
- Review individual test docstrings
- Check `conftest.py` for fixture definitions
- Consult `BULK_DOWNLOAD_TEST_PLAN.md` for detailed scenarios

---

**Happy Testing! 🧪**
