# Google OAuth Authentication Fix Documentation

## Issue Summary
Google OAuth login was broken after code cleanup. The authentication flow would fail with various errors including redirect_uri_mismatch and user creation failures.

## Root Causes

### 1. Wrong Login Template
**Problem**: The app was using `splash.html` which implements server-side OAuth flow, but the working implementation used `splash_gis.html` with Google Identity Services (client-side OAuth).

**Solution**: Changed `app.py` line 461:
```python
# From:
return render_template('splash.html', google_configured=google_configured)

# To:
return render_template('splash_gis.html', google_client_id=os.environ.get('GOOGLE_CLIENT_ID'), google_configured=google_configured)
```

### 2. User Model Mismatch
**Problem**: The `auth.py` file was trying to create users with fields that don't exist in the User model:
- `daily_limit` (doesn't exist)
- `monthly_limit` (doesn't exist)
- `is_admin` (doesn't exist - uses roles instead)

**Solution**: Fixed `auth.py` lines 605-617 to only use valid User model fields:
```python
user = User(
    email=email,
    name=name or email.split('@')[0],
    google_id=google_id,
    picture=picture,
    created_at=datetime.utcnow(),
    credits=999999 if is_admin else 50,
    subscription_plan='premium' if is_admin else 'trial',
    subscription_status='active' if is_admin else 'active'
)
```

### 3. Missing Python Packages
**Problem**: Google authentication packages were not installed despite being in requirements.txt.

**Solution**: Installed required packages:
```bash
pip install google-auth google-auth-oauthlib google-auth-httplib2
```

### 4. Invalid Template References
**Problem**: The navbar template referenced `admin.get_stats` which doesn't exist.

**Solution**: Changed to use `admin_test` in `templates/components/navbar.html` line 120.

## How Google OAuth Works in This App

This application uses **Google Identity Services (GIS)** for client-side authentication:

1. **Client-Side Flow**: 
   - Uses `splash_gis.html` template with Google's GSI JavaScript library
   - Shows a Google Sign-In popup/iframe
   - User authenticates directly with Google

2. **Token Verification**:
   - Google returns an ID token to the client
   - Client sends token to `/auth/google/verify` endpoint via POST
   - Server verifies the token with Google's servers
   - Server creates/updates user in database

3. **Session Creation**:
   - Server creates a Flask session for the authenticated user
   - User is redirected to the main application

## Configuration Requirements

### Environment Variables (.env)
```bash
GOOGLE_CLIENT_ID=your_google_client_id_here
GOOGLE_CLIENT_SECRET=your_google_client_secret_here
```

### Google Cloud Console
The following redirect URIs should be registered:
- `http://localhost/scraper/auth/google/callback` (IIS deployment)
- `/scraper/auth/google/callback` (development; use IIS proxy even locally)

Note: The client-side flow doesn't actually use these redirect URIs, but they may be needed for fallback scenarios.

## Testing OAuth

1. Start the server:
```bash
python3 start.py
```

2. Navigate to http://localhost/scraper

3. Click "Sign in with Google"

4. Select account in Google popup

5. Should redirect to main app after successful authentication

## Common Issues

1. **"An error has occurred" in Google popup**: Usually means the Google Client ID is not configured correctly or the domain is not authorized in Google Cloud Console.

2. **500 error after authentication**: Check that the User model fields match what's being set in auth.py

3. **Template errors after login**: Ensure all referenced routes exist in app.py

## Files Involved

- `/app.py` - Main application, renders login template
- `/auth.py` - OAuth handlers and user creation
- `/templates/splash_gis.html` - Client-side OAuth login page
- `/models.py` - User model definition
- `/templates/components/navbar.html` - Navigation with user info
