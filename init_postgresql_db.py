#!/usr/bin/env python3
"""
Initialize PostgreSQL database for Enhanced Media Scraper
Creates all necessary tables and default data
"""

import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

def get_database_url():
    """Get the database URL from environment"""
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        # Fallback to SQLite for Replit
        return 'sqlite:///scraped.db'
    return database_url