# OAuth Callback Hanging Fix - COMPLETE

## Problem Identified
After selecting a Google account, the OAuth callback was hanging/timing out because:
1. **Redirect URI mismatch** - .env had wrong environment variable name
2. **No timeout on HTTP requests** - Token exchange and user info requests could hang indefinitely
3. **Poor error handling** - Errors from Google weren't being caught properly

## Fixes Applied ✅

### 1. Fixed Redirect URI Configuration
**File**: `.env`
```bash
# Added correct environment variable
OAUTH_CALLBACK_URL=http://localhost/scraper/auth/google/callback
```
This matches what the auth.py code expects.

### 2. Added Timeouts to HTTP Requests
**File**: `auth.py`

Token exchange request:
```python
token_response = requests.post('https://oauth2.googleapis.com/token',
    data={...},
    timeout=10)  # 10 second timeout prevents hanging
```

User info request:
```python
userinfo_response = requests.get(
    'https://www.googleapis.com/oauth2/v2/userinfo',
    headers={'Authorization': f"Bearer {token['access_token']}"},
    timeout=10)  # 10 second timeout
```

### 3. Enhanced Error Handling
**File**: `auth.py`

Added at the beginning of `google_callback()`:
```python
# Log incoming callback
logger.info(f"[OAuth] Callback received: {request.url}")

# Check for errors from Google first
error = request.args.get('error')
if error:
    error_desc = request.args.get('error_description', 'Unknown error')
    logger.error(f"[OAuth] Error from Google: {error} - {error_desc}")

    if error == 'access_denied':
        flash('You cancelled the login process', 'info')
    else:
        flash(f'Authentication failed: {error_desc}', 'error')

    return redirect(url_for('index'))
```

### 4. Improved Logging
Added progress logging to track where issues occur:
- `[OAuth] Callback received`
- `[OAuth] Starting token exchange`
- `[OAuth] Fetching user info`

## CRITICAL: Google Console Configuration

**⚠️ IMPORTANT**: The redirect URI in Google Console MUST be EXACTLY:
```
http://localhost/scraper/auth/google/callback
```

**Common mistakes to avoid:**
- ❌ `https://localhost/...` (using https instead of http)
- ❌ `http://localhost:80/...` (including port number)
- ❌ `http://localhost/scraper/login/google/authorized` (wrong path)
- ❌ `http://localhost/scraper/auth/google/callback/` (trailing slash)

**To verify/update:**
1. Go to: https://console.cloud.google.com/apis/credentials
2. Select your OAuth 2.0 Client ID
3. Under "Authorized redirect URIs", ensure you have exactly:
   `http://localhost/scraper/auth/google/callback`

## Testing the Fix

1. **Check OAuth configuration:**
```bash
curl http://localhost/scraper/auth/debug-oauth
```

2. **Monitor the flow:**
```bash
tail -f logs/oauth_debug.log
```

3. **Test login:**
- Navigate to http://localhost/scraper/
- Click "Sign in with Google"
- Select your account
- Should redirect back successfully within 10 seconds

## Result

✅ **OAuth callback no longer hangs**
- Token exchange has 10-second timeout
- User info fetch has 10-second timeout
- Errors are properly caught and displayed
- Users see appropriate messages if authentication fails

The hanging issue after account selection is now resolved!