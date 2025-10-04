"""
Fix media_blobs user_id constraint to allow NULL for guest users
"""
import sys
sys.path.insert(0, '.')

from app import app, db
from models import MediaBlob

print("Fixing media_blobs.user_id constraint...")

with app.app_context():
    # For SQLite, we need to recreate the table
    # Check if there are any existing media blobs
    try:
        count = db.session.query(MediaBlob).count()
        print(f"Found {count} existing media blobs")

        if count > 0:
            print("WARNING: This will delete existing media blobs!")
            response = input("Continue? (yes/no): ")
            if response.lower() != 'yes':
                print("Aborted")
                sys.exit(0)
    except Exception as e:
        print(f"Could not query media_blobs: {e}")

    # Drop and recreate the table
    try:
        print("\nDropping media_blobs table...")
        MediaBlob.__table__.drop(db.engine, checkfirst=True)

        print("Creating media_blobs table with new schema...")
        MediaBlob.__table__.create(db.engine, checkfirst=True)

        print("\n✅ SUCCESS! media_blobs table updated")
        print("   user_id is now nullable (allows guest users)")

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
