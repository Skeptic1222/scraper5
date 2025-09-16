#!/usr/bin/env python3
"""
Database initialization script for SQL Server Express
"""
from sqlalchemy import create_engine, text
from models import db, User, Role, UserRole, AppSetting
import os

def init_database():
    """Initialize SQL Server Express database with tables and default data"""
    # SQL Server Express connection
    engine = create_engine(
        'mssql+pyodbc://localhost\\SQLEXPRESS/Scraped?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes',
        echo=True
    )
    
    print("🗄️  Connecting to SQL Server Express...")
    
    # Test connection
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))
        print("✅ SQL Server Express connection successful")
    
    # Create all tables
    from app import app
    with app.app_context():
        print("📋 Creating tables...")
        db.create_all()
        print("✅ All tables created successfully")
        
        # Create default roles if they don't exist
        if not Role.query.first():
            print("👤 Creating default roles...")
            
            # Create roles
            admin_role = Role(name='admin', description='Administrator with full access')
            user_role = Role(name='user', description='Standard user with basic access')
            guest_role = Role(name='guest', description='Guest user with limited access')
            
            db.session.add_all([admin_role, user_role, guest_role])
            db.session.commit()
            print("✅ Default roles created")
        
        # Create default settings if they don't exist
        if not AppSetting.query.first():
            print("⚙️  Creating default settings...")
            
            settings = [
                AppSetting(key='max_download_size', value='104857600', description='Maximum download size in bytes'),
                AppSetting(key='concurrent_downloads', value='3', description='Number of concurrent downloads'),
                AppSetting(key='enable_adult_content', value='false', description='Enable adult content sources'),
                AppSetting(key='default_safe_search', value='true', description='Enable safe search by default'),
            ]
            
            db.session.add_all(settings)
            db.session.commit()
            print("✅ Default settings created")
        
        print("🎉 Database initialization complete!")

if __name__ == "__main__":
    init_database() 