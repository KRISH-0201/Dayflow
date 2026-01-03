"""
Database Connection Test Script
Run this to verify MongoDB connection
Usage: python test_db.py
"""

from database import db, users_col

print("\n🔍 Testing database connection...\n")

if db is not None:
    try:
        # Test connection
        db.client.admin.command("ping")
        print("✅ MongoDB connection successful!")

        # Count users
        user_count = users_col.count_documents({})
        print(f"✅ Users in database: {user_count}")

        # List all users
        users = list(users_col.find({}, {"email": 1, "name": 1, "role": 1}))
        if users:
            print("\n📋 Users:")
            for user in users:
                print(f"   - {user.get('name')} ({user.get('email')}) - {user.get('role')}")

        print("\n✅ Database is ready!\n")

    except Exception as e:
        print(f"❌ Connection error: {e}\n")
else:
    print("❌ Database connection failed!\n")
    print("⚠️  Make sure:")
    print("   1. MongoDB URI is set in .env")
    print("   2. MongoDB cluster is accessible")
    print("   3. IP whitelist includes your machine\n")
