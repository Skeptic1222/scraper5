# Enhanced Media Scraper - Project Plan

## Current Issues to Fix

### 1. ❌ Server Control
- **Issue**: `start.bat` not working properly
- **Fix**: Update start.bat to properly handle Python execution
- **Status**: Need to fix batch file

### 2. ❌ Google Badge Colors
- **Issue**: Colors not displaying correctly for user avatars
- **Fix**: Implement proper color assignment based on initials
- **Status**: Need to add data-color attribute dynamically

### 3. ❌ Assets Page Empty
- **Issue**: Assets not loading despite being in database
- **Fix**: Debug asset loading query or provide option to clear database
- **Status**: Need to investigate asset retrieval

### 4. ❌ Double-Wide Checkboxes
- **Issue**: Checkboxes are double-width throughout the site
- **Fix**: Find and remove duplicate checkbox styling or conflicting CSS
- **Status**: High priority - affects entire UI

### 5. ❌ Remove Refresh Link
- **Issue**: Unnecessary refresh link in bottom left column
- **Fix**: Remove from sidebar template
- **Status**: Simple fix

### 6. ❌ Broken Pages
- **Issue**: Subscription, account settings pages not working
- **Fix**: Debug and restore functionality
- **Status**: Critical - core features broken

### 7. ❌ Admin Settings in Dropdown
- **Issue**: Admin link not in user dropdown for sop1973@gmail.com
- **Fix**: Add conditional admin link in navbar dropdown
- **Status**: Need to implement

### 8. ❌ AI Assistant Not Working
- **Issue**: AI assistant not opening when clicked
- **Fix**: Debug JavaScript initialization and event handlers
- **Status**: Feature incomplete

## Previous Requests Still Pending

### From Original Request:
1. ✅ Enable account management screen for admin (sop1973@gmail.com)
2. ✅ Add ability to add/subtract credits from accounts
3. ✅ Reduce Google sign-in button size
4. ❌ Make Google badge use standard Google colors (partially done)
5. ❌ Fix assets library to display videos and images
6. ❌ Fix checkboxes to be square (not double-wide)
7. ✅ Add all source locations back (Reddit, Motherless, Bing, etc.)
8. ✅ Fix theme button (completed)
9. ✅ Add "sign in to receive 50 free credits" message
10. ✅ Implement 50 credits for first-time sign-ins
11. ✅ Credits per download (not per search)
12. ❌ Get AI assistant working with chat dialog

## Implementation Order

### Phase 1: Critical Fixes (Immediate)
1. Fix double-wide checkboxes
2. Fix assets page loading
3. Fix server start.bat
4. Restore broken pages (subscription, account settings)

### Phase 2: UI/UX Improvements
1. Fix Google badge colors
2. Add admin dropdown link
3. Remove refresh link from sidebar
4. Fix AI assistant toggle

### Phase 3: Feature Completion
1. Complete AI assistant functionality
2. Test all admin features
3. Verify all source integrations

## Technical Tasks

### CSS Fixes Needed:
- Find and fix double-width checkbox issue
- Ensure Google colors apply correctly to badges
- Remove any conflicting styles

### JavaScript Fixes Needed:
- Fix AI assistant initialization
- Fix Google badge color assignment
- Fix asset loading functions

### Template Fixes Needed:
- Add admin link to navbar dropdown
- Remove refresh link from sidebar
- Fix subscription/account pages

### Backend Fixes Needed:
- Debug asset retrieval query
- Ensure proper user permissions
- Fix any routing issues

## Testing Checklist

After implementation:
- [ ] Server starts and stops properly
- [ ] All checkboxes are square (not double-wide)
- [ ] Assets load correctly
- [ ] Google badges show correct colors
- [ ] Admin dropdown appears for sop1973@gmail.com
- [ ] AI assistant opens and functions
- [ ] Subscription page works
- [ ] Account settings page works
- [ ] All sources appear in search
- [ ] Theme toggle continues to work
- [ ] Sign-in bonus banner appears for new users

## Success Criteria

The implementation will be complete when:
1. All UI elements display correctly
2. All pages load without errors
3. Admin features are accessible
4. AI assistant is functional
5. Assets can be viewed and managed
6. Server can be controlled with start/stop/restart commands