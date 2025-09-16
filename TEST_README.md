# OAuth and Sidebar Navigation Test Suite

This comprehensive test suite uses Playwright to test the Google OAuth login flow and sidebar navigation functionality of the Enhanced Media Scraper application.

## Files Created

- `test_oauth_and_sidebar.py` - Main test script with comprehensive OAuth and sidebar tests
- `run_tests.sh` - Convenient test runner script
- `test_config.json` - Configuration file for test scenarios and settings
- `playwright_config.json` - Browser configuration (already existed)

## Prerequisites

1. **Python 3** - Must be installed and accessible via `python3` command
2. **Playwright** - Will be automatically installed if not present
3. **Application Running** - The Enhanced Media Scraper should be running at `http://localhost:8080`

## Quick Start

### Method 1: Using the Test Runner (Recommended)

```bash
cd /mnt/c/inetpub/wwwroot/scraper
./run_tests.sh
```

### Method 2: Direct Python Execution

```bash
cd /mnt/c/inetpub/wwwroot/scraper
python3 test_oauth_and_sidebar.py
```

## What the Tests Do

### OAuth Login Flow Tests

1. **Initial Page Load** - Navigates to the application and takes a screenshot
2. **Sign-in Button Detection** - Locates the Google Sign-in button using multiple selectors
3. **OAuth Flow Handling** - Handles both real Google OAuth and mock authentication
4. **Login Verification** - Verifies successful login by checking for user indicators

### Sidebar Navigation Tests

1. **Sidebar Visibility** - Verifies the sidebar is visible and accessible
2. **Navigation Items** - Tests each navigation item:
   - Dashboard
   - Asset Library
   - Sources
   - AI Assistant
3. **Content Verification** - Confirms content changes when clicking navigation items
4. **Toggle Functionality** - Tests sidebar collapse/expand if available
5. **Persistence Testing** - Verifies sidebar persists after page refresh

## Test Output

The test suite generates comprehensive output in the `debug_logs/playwright/` directory:

### Screenshots
- `01_initial_load.png` - Initial page load
- `02_signin_button_found.png` - Sign-in button located
- `03_after_signin_click.png` - After clicking sign-in
- `04_*` - OAuth flow screenshots
- `05_login_verified.png` - Login verification
- `06_sidebar_visible.png` - Sidebar visibility
- `07_nav_*.png` - Each navigation item test
- `08_sidebar_collapsed.png` - Sidebar toggle test
- `09_sidebar_expanded.png` - Sidebar expand test
- `10_after_refresh.png` - After page refresh
- `11_final_state.png` - Final test state

### Video Recording
- Complete test session video in `debug_logs/playwright/videos/`

### Log Files
- Detailed test execution logs with timestamps
- Console messages from the browser
- Network request logs
- Error details and stack traces

### Test Results
- JSON file with comprehensive test results and metrics

## Configuration

### Browser Settings (`playwright_config.json`)
- Uses Microsoft Edge browser in non-headless mode
- 1920x1080 viewport
- Video recording enabled
- Network request logging
- Console message capture

### Test Settings (`test_config.json`)
- Navigation item selectors and expected content
- Timeout configurations
- Error recovery settings
- Test scenario toggles

## Troubleshooting

### Common Issues

1. **Application Not Running**
   ```
   Error: Application may not be running at http://localhost:8080
   ```
   **Solution**: Start the Enhanced Media Scraper application first

2. **Playwright Not Installed**
   ```
   Warning: Playwright not found. Installing...
   ```
   **Solution**: The script will automatically install Playwright

3. **Permission Denied**
   ```
   Permission denied: ./run_tests.sh
   ```
   **Solution**: Make the script executable: `chmod +x run_tests.sh`

### OAuth Testing Notes

- The test can handle both real Google OAuth and mock authentication
- For real OAuth testing, you would need test credentials (not included for security)
- The test will gracefully handle authentication failures and continue testing other components

### Sidebar Testing Notes

- Uses multiple selector strategies to find navigation elements
- Tests content switching by looking for expected content indicators
- Handles cases where sidebar toggle functionality may not be implemented

## Customization

### Adding New Navigation Items

Edit `test_config.json` and add new items to the `sidebar_items` array:

```json
{
  "name": "New Item",
  "selector": "[data-nav='new-item']",
  "alt_selectors": ["a:has-text('New Item')"],
  "expected_content": "new-item",
  "content_indicators": [".new-item-section"]
}
```

### Modifying Test Scenarios

Edit the `test_scenarios` section in `test_config.json` to enable/disable specific tests:

```json
"test_scenarios": {
  "oauth_flow": {
    "test_google_signin": true,
    "test_mock_login": false
  }
}
```

### Changing Browser Settings

Modify `playwright_config.json` to change browser behavior:

```json
{
  "browser": "chromium",  // or "firefox", "webkit"
  "headless": true,       // for headless testing
  "slowMo": 1000         // slow down actions
}
```

## Test Results Interpretation

### Successful Test
```
OAuth Login Test: PASSED
✓ Navigated to application
✓ Located sign-in button
✓ Clicked sign-in button
✓ Verified successful login

Sidebar Navigation Test: PASSED
✓ Sidebar is visible
✓ Tested navigation to Dashboard
✓ Tested navigation to Asset Library
```

### Failed Test
```
OAuth Login Test: FAILED
✓ Navigated to application
✗ Sign-in button not found on page
```

## Security Considerations

- This test suite does NOT include real OAuth credentials
- Screenshots and logs may contain sensitive information
- Test artifacts should not be committed to version control
- Use test accounts only, never production credentials

## Performance Notes

- Tests run with browser UI visible for debugging
- Video recording increases test execution time
- Full-page screenshots may be large files
- Consider running in headless mode for faster execution

## Support

For issues with the test suite:

1. Check the detailed log files in `debug_logs/playwright/`
2. Review screenshots to see the actual application state
3. Verify the application is running and accessible
4. Check browser console messages in the logs
5. Ensure all dependencies are properly installed