#!/usr/bin/env python3
"""
Verification Script - Confirms all timeout fixes are in place
Run this before restarting the Flask server
"""
import os
import sys
from pathlib import Path

def check_file_contains(filepath, search_strings):
    """Check if file contains all search strings"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            results = {}
            for search_str in search_strings:
                results[search_str] = search_str in content
            return results
    except Exception as e:
        print(f"  ERROR: {e}")
        return {s: False for s in search_strings}

def main():
    print("\n" + "="*80)
    print("DOWNLOAD HANG FIX - VERIFICATION REPORT")
    print("="*80 + "\n")

    all_good = True

    # 1. Check enhanced_working_downloader.py
    print("1. Checking enhanced_working_downloader.py...")
    downloader_checks = {
        'job_start_time = time.time()': 'Job start time tracking',
        'global_job_timeout = int(os.getenv': 'Global timeout configuration',
        'if elapsed > global_job_timeout:': 'Global timeout enforcement',
        'except TimeoutError as global_timeout:': 'Global timeout exception handler',
        'error_logger.info(f"SOURCE COMPLETED:': 'Enhanced logging',
        'CONFIG: MAX_CONCURRENT_SOURCES=': 'Configuration logging'
    }

    results = check_file_contains(
        'C:/inetpub/wwwroot/scraper/enhanced_working_downloader.py',
        downloader_checks.keys()
    )

    for check, description in downloader_checks.items():
        status = "[PASS]" if results[check] else "[FAIL]"
        print(f"  {status} - {description}")
        if not results[check]:
            all_good = False

    # 2. Check .env file
    print("\n2. Checking .env configuration...")
    env_checks = {
        'GLOBAL_JOB_TIMEOUT=300': 'Global job timeout setting',
        'SOURCE_TIMEOUT=30': 'Source timeout setting',
        'MAX_CONCURRENT_SOURCES=5': 'Concurrent sources setting'
    }

    results = check_file_contains(
        'C:/inetpub/wwwroot/scraper/.env',
        env_checks.keys()
    )

    for check, description in env_checks.items():
        status = "[PASS]" if results[check] else "[FAIL]"
        print(f"  {status} - {description}")
        if not results[check]:
            all_good = False

    # 3. Check cleanup script exists
    print("\n3. Checking cleanup script...")
    cleanup_script = Path('C:/inetpub/wwwroot/scraper/cleanup_stuck_jobs.py')
    if cleanup_script.exists():
        print(f"  [PASS] - Cleanup script exists")
    else:
        print(f"  [FAIL] - Cleanup script missing")
        all_good = False

    # 4. Test import
    print("\n4. Testing import...")
    try:
        sys.path.insert(0, 'C:/inetpub/wwwroot/scraper')
        from enhanced_working_downloader import run_download_job
        print(f"  [PASS] - Import successful")
    except Exception as e:
        print(f"  [FAIL] - Import failed: {e}")
        all_good = False

    # 5. Check for stuck jobs
    print("\n5. Checking for stuck jobs...")
    try:
        import sqlite3
        conn = sqlite3.connect('C:/inetpub/wwwroot/scraper/instance/scraper.db')
        cursor = conn.cursor()
        cursor.execute("""
            SELECT COUNT(*) FROM scrape_jobs
            WHERE status IN ('running', 'downloading', 'processing')
        """)
        count = cursor.fetchone()[0]
        cursor.close()
        conn.close()

        if count == 0:
            print(f"  [PASS] - No stuck jobs")
        else:
            print(f"  [WARN] - {count} jobs still in running state")
            print(f"    Run: python fix_stuck_job.py")
    except Exception as e:
        print(f"  [WARN] - Could not check database: {e}")

    # Summary
    print("\n" + "="*80)
    if all_good:
        print("[SUCCESS] ALL CHECKS PASSED - Ready to restart Flask server")
        print("\nNext steps:")
        print("1. Kill any running Python processes: pkill -f python")
        print("2. Start Flask server: python app.py")
        print("3. Test a download with query: 'cats' and 2-3 sources")
        print("4. Monitor logs: tail -f logs/download_errors.log")
    else:
        print("[ERROR] SOME CHECKS FAILED - Review errors above before proceeding")
    print("="*80 + "\n")

    return all_good

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
