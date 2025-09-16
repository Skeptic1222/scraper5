# Google OAuth Configuration Update Required

## Current Issue
The Google Sign-In is showing a 404 error because the redirect URI has changed from port 5050 to port 80 with IIS deployment.

## OAuth Configuration Status
✅ **Application configured correctly:**
- Redirect URI: `http://localhost/scraper/auth/google/callback`
- Client ID: `your_google_client_id_here`

## Action Required: Update Google Cloud Console

### Steps to Fix:

1. **Go to Google Cloud Console:**
   https://console.cloud.google.com/

2. **Navigate to OAuth 2.0 Client IDs:**
   - APIs & Services → Credentials
   - Click on your OAuth 2.0 Client ID

3. **Update Authorized redirect URIs:**
   
   **Remove old URI:**
   - `http://localhost:5050/auth/google/callback`
   
   **Add new URIs (add ALL of these):**
   - `http://localhost/scraper/auth/google/callback`
   - `http://192.168.1.2/scraper/auth/google/callback`
   - `http://[your-public-ip]/scraper/auth/google/callback`

4. **Save Changes**
   - Click "SAVE" at the bottom of the page
   - Wait 5-10 minutes for changes to propagate

### Testing After Update:

1. Access the application at: http://localhost/scraper
2. Click "Sign in with Google"
3. You should be redirected to Google's account selection
4. After signing in, you'll be redirected back to the application

### Additional URIs for Production:

If you plan to access from a domain name, also add:
- `https://yourdomain.com/scraper/auth/google/callback`

### Troubleshooting:

If you still get errors after updating:
- Clear browser cache and cookies
- Try incognito/private browsing mode
- Ensure the exact URI matches (no trailing slashes)
- Check that IIS is running: `powershell.exe -Command "Get-Service W3SVC"`

### Current Application Status:
- ✅ IIS running on port 80
- ✅ Application accessible at http://localhost/scraper
- ✅ OAuth callback configured correctly
- ⏳ Waiting for Google Console update