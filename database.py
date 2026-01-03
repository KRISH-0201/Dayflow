"""
MongoDB Database Configuration
Handles all database connections and collections
"""

import os
from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# MongoDB connection
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = "Cluster0"

try:
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    # Test connection
    client.admin.command('ping')
    print("✅ Connected to MongoDB")
    
    db = client[DB_NAME]
    
    # Collections
    users_col = db["users"]
    employees_col = db["employees"]
    attendance_col = db["attendance"]
    leave_requests_col = db["leave_requests"]
    
    # Create indexes for better performance
    users_col.create_index("employee_id", unique=True)
    users_col.create_index("email", unique=True)
    employees_col.create_index("employee_id", unique=True)
    attendance_col.create_index([("employee_id", 1), ("date", -1)])
    leave_requests_col.create_index([("employee_id", 1), ("status", 1)])
    
    print("✅ Database indexes created")
    
except Exception as e:
    print(f"❌ MongoDB connection failed: {e}")
    users_col = None
    employees_col = None
    attendance_col = None
    leave_requests_col = None
