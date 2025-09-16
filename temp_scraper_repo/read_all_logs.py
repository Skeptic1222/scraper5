#!/usr/bin/env python3
"""
Comprehensive log reader - reads ALL logs from Flask, IIS, and debug outputs
Automatically finds and displays relevant OAuth errors
"""

import glob
import json
import os
from datetime import datetime


def read_latest_logs():
    """Read all available logs and find OAuth issues"""

    print("\n" + "=" * 80)
    print(f"COMPREHENSIVE LOG ANALYSIS - {datetime.now()}")
    print("=" * 80)

    logs_found = {}
    errors_found = []
    oauth_events = []

    # 1. Check Flask/Python logs
    log_paths = [
        'debug_logs/app_debug.log',
        'debug_logs/oauth_debug.log',
        'debug_logs/errors.log',
        'logs/oauth_debug.log',
        'flask.log',
        'server.log'
    ]

    print("\n📝 FLASK APPLICATION LOGS:")
    print("-" * 40)

    for log_path in log_paths:
        if os.path.exists(log_path):
            print(f"\nReading: {log_path}")
            try:
                with open(log_path, 'r') as f:
                    lines = f.readlines()
                    # Get last 20 lines
                    recent_lines = lines[-20:] if len(lines) > 20 else lines

                    oauth_related = []
                    errors = []

                    for line in recent_lines:
                        # Check for OAuth/auth related
                        if any(keyword in line.lower() for keyword in ['oauth', 'auth', 'google', 'callback', 'token', 'redirect']):
                            oauth_related.append(line.strip())
                            oauth_events.append({'source': log_path, 'line': line.strip()})

                        # Check for errors
                        if any(keyword in line.upper() for keyword in ['ERROR', 'EXCEPTION', 'FAILED', 'TIMEOUT']):
                            errors.append(line.strip())
                            errors_found.append({'source': log_path, 'error': line.strip()})

                    if oauth_related:
                        print("  OAuth Events:")
                        for event in oauth_related[-5:]:  # Last 5 OAuth events
                            print(f"    {event}")

                    if errors:
                        print("  ⚠️ Errors Found:")
                        for error in errors[-3:]:  # Last 3 errors
                            print(f"    {error}")

            except Exception as e:
                print(f"  Error reading file: {e}")

    # 2. Check IIS logs
    print("\n🌐 IIS LOGS:")
    print("-" * 40)

    iis_log_patterns = [
        'C:/inetpub/logs/LogFiles/W3SVC*/*.log',
        'debug_logs/iis_logs/*.log',
        'C:/Windows/System32/LogFiles/HTTPERR/*.log'
    ]

    for pattern in iis_log_patterns:
        files = glob.glob(pattern.replace('/', os.sep))
        if files:
            latest_file = max(files, key=os.path.getctime)
            print(f"\nReading IIS log: {latest_file}")

            try:
                with open(latest_file, 'r') as f:
                    lines = f.readlines()
                    # Get last 10 lines
                    recent_lines = lines[-10:] if len(lines) > 10 else lines

                    for line in recent_lines:
                        # Look for /auth or /oauth requests
                        if any(path in line for path in ['/auth', '/oauth', '/google', '/callback', '/scraper']):
                            # Parse IIS log line
                            parts = line.split()
                            if len(parts) > 10:
                                date_time = f"{parts[0]} {parts[1]}"
                                method = parts[3]
                                uri = parts[4]
                                status = parts[11] if len(parts) > 11 else 'unknown'
                                time_taken = parts[-1] if len(parts) > 15 else 'unknown'

                                print(f"  {date_time} - {method} {uri} - Status: {status} - Time: {time_taken}ms")

                                if int(status) >= 400:
                                    errors_found.append({'source': 'IIS', 'error': f"{method} {uri} returned {status}"})

            except Exception as e:
                print(f"  Error reading IIS log: {e}")

    # 3. Check background Flask processes
    print("\n🔄 BACKGROUND PROCESSES:")
    print("-" * 40)

    # Check for running Flask processes
    os.system("ps aux | grep 'python.*app.py' | grep -v grep | tail -3")

    # 4. Check recent authentication attempts
    print("\n🔐 RECENT AUTH ATTEMPTS:")
    print("-" * 40)

    # Look for session files or auth cookies
    session_paths = [
        'flask_session/*',
        'instance/*.db'
    ]

    for pattern in session_paths:
        files = glob.glob(pattern)
        if files:
            for file in files[-3:]:  # Last 3 files
                stat = os.stat(file)
                mod_time = datetime.fromtimestamp(stat.st_mtime)
                print(f"  {file} - Modified: {mod_time}")

    # 5. SUMMARY
    print("\n" + "=" * 80)
    print("📊 ANALYSIS SUMMARY:")
    print("=" * 80)

    if errors_found:
        print("\n❌ ERRORS DETECTED:")
        for error in errors_found[-5:]:  # Last 5 errors
            print(f"  Source: {error['source']}")
            print(f"  Error: {error['error'][:200]}")  # First 200 chars
            print()

    if oauth_events:
        print("\n🔑 OAUTH FLOW EVENTS:")
        # Group by time if possible
        for event in oauth_events[-10:]:  # Last 10 OAuth events
            print(f"  {event['source']}: {event['line'][:150]}")

    # 6. DIAGNOSIS
    print("\n" + "=" * 80)
    print("🔍 PROBABLE ISSUES:")
    print("=" * 80)

    issues = []

    # Check for common OAuth problems
    for error in errors_found:
        error_text = error['error'].lower()

        if 'timeout' in error_text:
            issues.append("⏱️ TIMEOUT: OAuth callback is timing out - check network/firewall")

        if 'redirect_uri_mismatch' in error_text:
            issues.append("🔗 REDIRECT URI MISMATCH: Google Console redirect URI doesn't match app")

        if 'invalid_grant' in error_text:
            issues.append("🔑 INVALID GRANT: Authorization code expired or already used")

        if '401' in error_text or 'unauthorized' in error_text:
            issues.append("🚫 UNAUTHORIZED: Client ID/Secret may be wrong")

        if '500' in error_text or 'internal server' in error_text:
            issues.append("💥 SERVER ERROR: Application crash during OAuth flow")

        if 'database' in error_text or 'sql' in error_text:
            issues.append("🗄️ DATABASE: SQL Server connection failing")

    if issues:
        for issue in set(issues):  # Unique issues only
            print(f"  {issue}")
    else:
        print("  No obvious issues detected in logs")

    print("\n" + "=" * 80)
    print("💡 RECOMMENDATIONS:")
    print("=" * 80)
    print("1. Check Google Console: https://console.cloud.google.com/apis/credentials")
    print("   Redirect URI must be: http://localhost/scraper/auth/google/callback")
    print("\n2. Test OAuth endpoint directly:")
    print("   curl -v http://localhost/scraper/auth/debug-oauth")
    print("\n3. Monitor live logs:")
    print("   tail -f debug_logs/oauth_debug.log")
    print("\n4. Check IIS Application Pool is running:")
    print("   Windows: inetmgr -> Application Pools -> Check status")

    return {
        'errors': errors_found,
        'oauth_events': oauth_events,
        'issues': list(set(issues))
    }

if __name__ == "__main__":
    results = read_latest_logs()

    # Save analysis to file
    with open('debug_logs/analysis_report.json', 'w') as f:
        json.dump(results, f, indent=2, default=str)

    print(f"\n📄 Full analysis saved to: debug_logs/analysis_report.json")
