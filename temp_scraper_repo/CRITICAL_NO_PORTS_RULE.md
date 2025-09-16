# ⚠️ CRITICAL: NEVER ADD PORTS TO URLS ⚠️

## THIS IS THE MOST IMPORTANT RULE IN THIS CODEBASE

### ❌ NEVER DO THIS:
- `http://localhost:5050/scraper` ❌ WRONG!
- `http://localhost:5000/api/...` ❌ WRONG!
- `http://192.168.1.100:3000/scraper` ❌ WRONG!
- `window.APP_BASE = 'http://localhost:5050/scraper'` ❌ WRONG!

### ✅ ALWAYS DO THIS:
- `http://localhost/scraper` ✅ CORRECT!
- `http://192.168.1.100/scraper` ✅ CORRECT!
- `window.APP_BASE = '/scraper'` ✅ CORRECT!
- All API calls: `/scraper/api/...` ✅ CORRECT!

## WHY THIS RULE EXISTS

The application runs behind an IIS reverse proxy that handles port routing internally:
- IIS listens on port 80 (standard HTTP)
- IIS forwards `/scraper/*` requests to Flask on port 5050
- The browser should NEVER know about port 5050
- ALL URLs must go through the IIS proxy without ports

## HOW IT WORKS

```
Browser Request:           IIS Proxy:              Flask Backend:
localhost/scraper  -----> Port 80 -----> Forward to localhost:5050
                          (NO PORT!)      (Internal only - hidden from browser)
```

## ACCESS PATTERNS

### From Windows (Browser):
- URL: `http://localhost/scraper`
- API: `http://localhost/scraper/api/...`
- NO PORTS EVER!

### From WSL (Playwright/Testing):
- URL: `http://<internal-ip>/scraper`
- Example: `http://192.168.1.100/scraper`
- NO PORTS EVER!

### From Flask Backend (Internal):
- The backend runs on port 5050
- This is ONLY for internal IIS-to-Flask communication
- NEVER expose this port in frontend URLs

## FILES THAT ENFORCE THIS RULE

1. **templates/base.html**
   - Line 17: `window.APP_BASE = '/scraper';  // NEVER add :port here!`

2. **static/js/fixes/api-path-fix.js**
   - Strips any port numbers from URLs
   - Forces /scraper prefix on all API calls

3. **static/js/fixes/asset-library-fix.js**
   - Hardcoded to use `/scraper/api/...` without ports

## CHECKLIST FOR DEVELOPERS

Before ANY commit or change:
- [ ] Check that NO URLs contain `:5050`, `:5000`, or ANY port number
- [ ] Verify `window.APP_BASE = '/scraper'` (NO PORT!)
- [ ] Test with `http://localhost/scraper` (NO PORT!)
- [ ] Ensure all API calls use `/scraper/api/...` prefix
- [ ] Never expose backend port 5050 to frontend

## COMMON MISTAKES TO AVOID

1. **Adding ports when debugging**
   - Even for testing, use the IIS proxy URL without ports

2. **Hardcoding localhost:5050 in JavaScript**
   - Always use relative paths with /scraper prefix

3. **Using direct backend access**
   - Never bypass IIS by accessing Flask directly

4. **Forgetting the /scraper prefix**
   - All paths must include /scraper for IIS routing

## TESTING COMMANDS

```bash
# CORRECT - Test through IIS proxy (NO PORT!)
curl http://localhost/scraper
curl http://localhost/scraper/api/assets

# WRONG - Never use these in production code
curl http://localhost:5050  # Internal only!
curl http://localhost:5000  # Wrong port anyway!
```

## ENFORCEMENT

This rule is enforced by:
- Warning comments throughout the codebase
- API path interceptor that strips ports
- IIS configuration that only accepts port 80/443

## REMEMBER

🚨 **If you add a port number to ANY URL, the application WILL break!** 🚨

The IIS proxy is the ONLY way to access the application.
Port 5050 is for internal IIS-to-Flask communication ONLY.

---
**Last Updated**: September 2025
**Critical Rule**: NO PORTS IN URLS - EVER!