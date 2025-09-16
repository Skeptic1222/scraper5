#!/usr/bin/env python3
"""Grant admin role to test user"""

import os
import sqlite3

db_path = 'instance/scraper.db'

if not os.path.exists(db_path):
    print(f"❌ Database not found at {db_path}")
    exit(1)

# Connect to SQLite database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# First, check if test user exists
cursor.execute("SELECT id, email, subscription_plan, credits FROM users WHERE email = 'test@example.com'")
user = cursor.fetchone()

if not user:
    print("❌ Test user not found!")
    exit(1)

user_id = user[0]
print(f"Found test user: ID={user_id}, Email={user[1]}")

# Update user to have premium subscription and credits
cursor.execute("""
    UPDATE users
    SET subscription_plan = 'premium',
        subscription_status = 'active',
        credits = 1000
    WHERE id = ?
""", (user_id,))
print("✅ Updated user subscription to premium with 1000 credits")

# Check if admin role exists
cursor.execute("SELECT id, name FROM roles WHERE name = 'admin'")
admin_role = cursor.fetchone()

if not admin_role:
    # Create admin role
    cursor.execute("""
        INSERT INTO roles (name, description)
        VALUES ('admin', 'Administrator with full permissions')
    """)
    role_id = cursor.lastrowid
    print(f"✅ Created admin role with ID={role_id}")
else:
    role_id = admin_role[0]
    print(f"Found existing admin role: ID={role_id}")

# Check if user already has a role assignment
cursor.execute("SELECT * FROM user_roles WHERE user_id = ?", (user_id,))
existing_role = cursor.fetchone()

if existing_role:
    # Update existing role
    cursor.execute("""
        UPDATE user_roles
        SET role_id = ?
        WHERE user_id = ?
    """, (role_id, user_id))
    print("✅ Updated user role to admin")
else:
    # Insert new role assignment
    cursor.execute("""
        INSERT INTO user_roles (user_id, role_id)
        VALUES (?, ?)
    """, (user_id, role_id))
    print("✅ Assigned admin role to user")

# Verify the changes
cursor.execute("""
    SELECT u.email, u.subscription_plan, u.credits, r.name
    FROM users u
    LEFT JOIN user_roles ur ON u.id = ur.user_id
    LEFT JOIN roles r ON ur.role_id = r.id
    WHERE u.email = 'test@example.com'
""")
result = cursor.fetchone()

if result:
    print("\n✅ Final user status:")
    print(f"  - Email: {result[0]}")
    print(f"  - Plan: {result[1]}")
    print(f"  - Credits: {result[2]}")
    print(f"  - Role: {result[3] or 'None'}")

conn.commit()
conn.close()

print("\n✅ User permissions fixed! The test user now has admin role with premium subscription.")
