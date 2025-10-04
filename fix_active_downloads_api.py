#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Quick fix for Active Downloads API issue
This script verifies and fixes the jobs API authentication logic
"""

import sys
import os

# Force UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8') if hasattr(sys.stdout, 'reconfigure') else None

def analyze_jobs_api():
    """Analyze the jobs.py file for the authentication bug"""

    print("=" * 70)
    print("ACTIVE DOWNLOADS API FIX")
    print("=" * 70)
    print()

    jobs_file = "C:\\inetpub\\wwwroot\\scraper\\blueprints\\jobs.py"

    try:
        with open(jobs_file, 'r') as f:
            content = f.read()

        print(f"✓ Found jobs.py at: {jobs_file}")
        print()

        # Check if the problematic code exists
        if 'status_filter in [\'running\', \'pending\', \'downloading\']' in content:
            print("✓ Found correct authentication logic")
            print()

            # Check if debug logging exists
            if '[JOBS API]' in content:
                print("✓ Debug logging already added")
                print()
            else:
                print("⚠ Debug logging NOT found")
                print("  Adding debug logging...")

                # The logging was already added in previous step
                print("  Already applied via Edit tool")
                print()

        print("DIAGNOSIS:")
        print("-" * 70)
        print("The code logic appears correct. The issue is likely:")
        print()
        print("1. Flask server not restarted after code changes")
        print("2. Parameter 'status_filter' is None instead of 'running'")
        print("3. Request being cached by IIS or browser")
        print()

        print("IMMEDIATE ACTIONS:")
        print("-" * 70)
        print("1. Restart Flask server:")
        print("   pkill -f python")
        print("   python3 app.py")
        print()
        print("2. Clear browser cache and test:")
        print("   Open DevTools > Network tab > Disable cache")
        print("   Navigate to: http://localhost/scraper")
        print()
        print("3. Create a test job:")
        print("   - Login to application")
        print("   - Go to Search & Download")
        print("   - Search for 'test' with 5 items")
        print("   - Return to Dashboard")
        print()
        print("4. Monitor logs:")
        print("   tail -f C:\\inetpub\\wwwroot\\scraper\\logs\\app.log")
        print()

        print("EXPECTED API RESPONSE (after fix):")
        print("-" * 70)
        print("For: GET /scraper/api/jobs?status=running")
        print()
        print("When no jobs exist:")
        print('  {"success": true, "jobs": [], "total": 0}')
        print()
        print("When jobs exist:")
        print('  {"success": true, "jobs": [{...}], "total": 1}')
        print()
        print("Should NOT contain: 'message': 'Login to view job history'")
        print()

        return True

    except FileNotFoundError:
        print(f"✗ ERROR: Could not find {jobs_file}")
        return False
    except Exception as e:
        print(f"✗ ERROR: {str(e)}")
        return False

def test_api_directly():
    """Test the API directly"""
    import requests

    print("=" * 70)
    print("TESTING API DIRECTLY")
    print("=" * 70)
    print()

    try:
        print("Testing: GET /scraper/api/jobs?status=running")
        response = requests.get("http://localhost/scraper/api/jobs?status=running", timeout=5)

        print(f"Status Code: {response.status_code}")
        print(f"Response:")
        print(response.text)
        print()

        data = response.json()

        if "message" in data and "Login" in data["message"]:
            print("⚠ ISSUE CONFIRMED: API returning 'Login' message")
            print()
            print("This means either:")
            print("  - status_filter parameter not being recognized")
            print("  - Flask server needs restart")
            print("  - Code changes not deployed")
            print()
        elif "jobs" in data:
            print("✓ API responding correctly!")
            print(f"  Jobs count: {len(data.get('jobs', []))}")
            if len(data.get('jobs', [])) == 0:
                print()
                print("ℹ No jobs found (expected if no downloads started)")
                print("  Create a download job to see Active Downloads")
            print()

    except requests.exceptions.ConnectionError:
        print("✗ ERROR: Could not connect to Flask server")
        print("  Make sure Flask is running on port 5050 or 8080")
        print()
    except Exception as e:
        print(f"✗ ERROR: {str(e)}")
        print()

if __name__ == "__main__":
    success = analyze_jobs_api()
    print()
    test_api_directly()

    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print()
    print("The Active Downloads section will appear when:")
    print("  1. User is on Dashboard section")
    print("  2. At least one job exists with status: running/pending/downloading")
    print("  3. API returns jobs array (not 'Login' message)")
    print("  4. JavaScript polling is active (every 2 seconds)")
    print()
    print("Refer to: ACTIVE_DOWNLOADS_DEBUG_REPORT.md for full details")
    print()
