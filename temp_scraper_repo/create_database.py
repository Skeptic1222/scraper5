#!/usr/bin/env python3
"""
Create and initialize SQL Server database for Enhanced Media Scraper
"""
import sys

import pyodbc


def create_database():
    """Create scraperdb database if it doesn't exist"""
    try:
        # Connect to master database
        # Try different connection methods
        servers_to_try = [
            '10.255.255.254\\SQLEXPRESS',
            '192.168.1.2\\SQLEXPRESS',
            'localhost\\SQLEXPRESS',
            '127.0.0.1\\SQLEXPRESS'
        ]

        conn = None
        for server in servers_to_try:
            try:
                print(f"Trying to connect to {server}...")
                conn = pyodbc.connect(
                    f'DRIVER={{ODBC Driver 17 for SQL Server}};'
                    f'SERVER={server};'
                    f'DATABASE=master;'
                    f'Trusted_Connection=yes;'
                    f'TrustServerCertificate=yes;',
                    timeout=5
                )
                print(f"✅ Connected successfully to {server}")
                break
            except Exception as e:
                print(f"❌ Failed to connect to {server}: {str(e)[:50]}")
                continue

        if not conn:
            raise Exception("Could not connect to SQL Server Express")
        conn.autocommit = True
        cursor = conn.cursor()

        # Check if database exists
        cursor.execute("SELECT name FROM sys.databases WHERE name = 'scraperdb'")
        result = cursor.fetchone()

        if not result:
            print("Creating database 'scraperdb'...")
            cursor.execute("CREATE DATABASE scraperdb")
            print("✅ Database 'scraperdb' created successfully")
        else:
            print("✅ Database 'scraperdb' already exists")

        cursor.close()
        conn.close()

        # Test connection to the new database
        print("\nTesting connection to scraperdb...")
        test_conn = pyodbc.connect(
            'DRIVER={ODBC Driver 17 for SQL Server};'
            'SERVER=localhost\\SQLEXPRESS;'
            'DATABASE=scraperdb;'
            'Trusted_Connection=yes;'
        )
        print("✅ Successfully connected to scraperdb")
        test_conn.close()

        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    if create_database():
        print("\n✅ Database setup complete!")
        print("You can now start the application with: python3 start.py")
        sys.exit(0)
    else:
        print("\n❌ Database setup failed")
        sys.exit(1)
