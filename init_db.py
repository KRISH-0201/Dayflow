"""
Database Initialization Script
Run this ONCE to populate demo data
Usage: python init_db.py
"""

from database import users_col, employees_col, attendance_col, leave_requests_col
from datetime import datetime, timedelta
import bcrypt

def init_demo_data():
    """Initialize database with demo users and data"""
    
    print("🔄 Initializing demo data...")
    
    # Clear existing data
    if users_col is not None:
        users_col.delete_many({})
        print("  ✓ Cleared users")
    
    if employees_col is not None:
        employees_col.delete_many({})
        print("  ✓ Cleared employees")
    
    if attendance_col is not None:
        attendance_col.delete_many({})
        print("  ✓ Cleared attendance")
    
    if leave_requests_col is not None:
        leave_requests_col.delete_many({})
        print("  ✓ Cleared leave requests")
    
    # Demo users
    demo_users = [
        {
            "employee_id": "EMP001",
            "email": "john@company.com",
            "password": bcrypt.hashpw("pass123".encode(), bcrypt.gensalt()),
            "name": "John Doe",
            "role": "employee"
        },
        {
            "employee_id": "EMP002",
            "email": "jane@company.com",
            "password": bcrypt.hashpw("pass123".encode(), bcrypt.gensalt()),
            "name": "Jane Smith",
            "role": "employee"
        },
        {
            "employee_id": "EMP003",
            "email": "bob@company.com",
            "password": bcrypt.hashpw("pass123".encode(), bcrypt.gensalt()),
            "name": "Bob Wilson",
            "role": "employee"
        },
        {
            "employee_id": "ADMIN001",
            "email": "admin@company.com",
            "password": bcrypt.hashpw("admin123".encode(), bcrypt.gensalt()),
            "name": "Admin User",
            "role": "admin"
        }
    ]
    
    # Insert users and create employee profiles
    for user in demo_users:
        if users_col is not None:
            users_col.insert_one(user)
            print(f"  ✓ Added user: {user['name']}")
            
            # Create employee record only for employees (not admin)
            if user["role"] == "employee" and employees_col is not None:
                employees_col.insert_one({
                    "employee_id": user["employee_id"],
                    "name": user["name"],
                    "department": "Engineering",
                    "designation": "Developer",
                    "job_details": {
                        "joining_date": datetime.now().replace(
                            hour=0, minute=0, second=0, microsecond=0
                        ),
                        "employment_type": "Full-time",
                        "manager": "Jane Manager"
                    },
                    "salary_structure": {
                        "basic": 50000,
                        "hra": 20000,
                        "allowances": 10000,
                        "deductions": 5000
                    },
                    # SAFE DEFAULTS so employee can enter these via Profile tab
                    "contact": {
                        "email": user["email"],
                        "phone": "",
                        "address": ""
                    },
                    "documents": [
                        {
                            "title": "Offer Letter",
                            "type": "pdf",
                            "url": "https://example.com/offer-letter.pdf"
                        },
                        {
                            "title": "ID Proof",
                            "type": "image",
                            "url": "https://example.com/id-proof.png"
                        }
                    ],
                    "profile_picture": "",
                    "leaves_balance": {
                        "paid": 20,
                        "sick": 10,
                        "unpaid": 5
                    }
                })
                print(f"    ✓ Created employee profile")
    
    # Demo attendance records (last 30 days) for EMP001
    if attendance_col is not None:
        today = datetime.now()
        for i in range(30):
            date = today - timedelta(days=i)
            # Only add weekday records
            if date.weekday() < 5:
                status = "present" if i % 3 != 0 else "absent"
                check_in = "09:30 AM" if status == "present" else None
                check_out = "06:00 PM" if status == "present" else None
                
                attendance_col.insert_one({
                    "employee_id": "EMP001",
                    "date": date.replace(hour=0, minute=0, second=0, microsecond=0),
                    "status": status,
                    "check_in": check_in,
                    "check_out": check_out
                })
        
        print(f"  ✓ Added 30 days attendance records for EMP001")
    
    # Demo leave requests
    if leave_requests_col is not None:
        demo_leaves = [
            {
                "employee_id": "EMP001",
                "start_date": (datetime.now() + timedelta(days=5)).replace(
                    hour=0, minute=0, second=0, microsecond=0
                ),
                "end_date": (datetime.now() + timedelta(days=7)).replace(
                    hour=0, minute=0, second=0, microsecond=0
                ),
                "leave_type": "paid",
                "reason": "Personal work",
                "status": "pending",
                "days": 3,
                "applied_at": datetime.now()
            },
            {
                "employee_id": "EMP002",
                "start_date": (datetime.now() + timedelta(days=10)).replace(
                    hour=0, minute=0, second=0, microsecond=0
                ),
                "end_date": (datetime.now() + timedelta(days=12)).replace(
                    hour=0, minute=0, second=0, microsecond=0
                ),
                "leave_type": "sick",
                "reason": "Medical appointment",
                "status": "pending",
                "days": 3,
                "applied_at": datetime.now()
            },
            {
                "employee_id": "EMP003",
                "start_date": (datetime.now() + timedelta(days=2)).replace(
                    hour=0, minute=0, second=0, microsecond=0
                ),
                "end_date": (datetime.now() + timedelta(days=4)).replace(
                    hour=0, minute=0, second=0, microsecond=0
                ),
                "leave_type": "unpaid",
                "reason": "Family emergency",
                "status": "pending",
                "days": 3,
                "applied_at": datetime.now()
            }
        ]
        
        leave_requests_col.insert_many(demo_leaves)
        print(f"  ✓ Added 3 demo leave requests")
    
    print("\n✅ Demo data initialization complete!\n")
    print("📝 Demo Credentials:")
    print("   Employee: john@company.com / pass123")
    print("   Admin: admin@company.com / admin123\n")

if __name__ == "__main__":
    init_demo_data()
