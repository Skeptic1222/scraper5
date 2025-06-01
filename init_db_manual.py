import os
from app import app
from models import db, init_db, User, Role, UserRole
from sqlalchemy import text

print("🔄 Manually initializing database...")
print(f"📍 Database URI: {app.config['SQLALCHEMY_DATABASE_URI']}")
print(f"📁 Current directory: {os.getcwd()}")

with app.app_context():
    try:
        print("🔍 Checking database connection...")
        # Test database connection with correct SQLAlchemy syntax
        with db.engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("✅ Database connection successful")
        
        # Drop all tables first to ensure clean state
        print("🗑️ Dropping existing tables...")
        db.drop_all()
        print("✅ Dropped existing tables")
        
        # Create all tables
        print("🏗️ Creating all tables...")
        db.create_all()
        print("✅ Created all tables")
        
        # Check if tables were created
        print("🔍 Checking created tables...")
        inspector = db.inspect(db.engine)
        tables = inspector.get_table_names()
        print(f"📋 Tables created: {tables}")
        
        # Initialize with default data
        print("📝 Initializing default data...")
        init_db()
        print("✅ Initialized default data")
        
        # Verify data was inserted
        print("🔍 Verifying data...")
        roles = Role.query.all()
        print(f"📊 Roles in database: {[r.name for r in roles]}")
        
        print("🎉 Database initialization complete!")
        
    except Exception as e:
        print(f"❌ Error during database initialization: {e}")
        import traceback
        traceback.print_exc() 