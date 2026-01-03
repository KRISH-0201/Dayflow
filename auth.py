"""
Authentication Module
Handles user login, signup, and password hashing
"""

import bcrypt
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))
from database import users_col

def hash_password(password: str) -> bytes:
    """Hash a password using bcrypt"""
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt())

def verify_password(password: str, hashed: bytes) -> bool:
    """Verify a password against its hash"""
    return bcrypt.checkpw(password.encode(), hashed)

def login_user(email: str, password: str) -> tuple:
    """
    Authenticate user login
    
    Args:
        email: User email
        password: User password
    
    Returns:
        (success: bool, result: dict/str)
        - If success: (True, user_dict)
        - If failed: (False, error_message)
    """
    if users_col is None:
        return False, "❌ Database connection failed"
    
    try:
        # Find user by email
        user = users_col.find_one({"email": email})
        
        if not user:
            return False, "❌ Email not found. Please signup first."
        
        # Verify password
        if verify_password(password, user["password"]):
            # Remove password from returned user object
            user.pop("password", None)
            return True, user
        else:
            return False, "❌ Incorrect password"
    
    except Exception as e:
        return False, f"❌ Login error: {str(e)}"

def signup_user(email: str, password: str, name: str, employee_id: str, role: str = "employee") -> tuple:
    """
    Register a new user
    
    Args:
        email: User email
        password: User password
        name: User full name
        employee_id: Employee ID
        role: User role (employee or admin) - default is employee
    
    Returns:
        (success: bool, message: str)
    """
    if users_col is None:
        return False, "❌ Database connection failed"
    
    try:
        # Check if email already exists
        existing_user = users_col.find_one({"email": email})
        if existing_user:
            return False, "❌ Email already registered"
        
        # Check if employee_id already exists
        existing_employee = users_col.find_one({"employee_id": employee_id})
        if existing_employee:
            return False, "❌ Employee ID already registered"
        
        # Create new user
        new_user = {
            "email": email,
            "password": hash_password(password),
            "name": name,
            "employee_id": employee_id,
            "role": role.lower()  # Ensure role is lowercase
        }
        
        result = users_col.insert_one(new_user)
        
        if result.inserted_id:
            return True, f"✅ Account created successfully as {role.upper()}!"
        else:
            return False, "❌ Failed to create account"
    
    except Exception as e:
        return False, f"❌ Signup error: {str(e)}"

def check_role(required_role: str) -> bool:
    """
    Check if current user has the required role
    
    Args:
        required_role: Required role (employee or admin)
    
    Returns:
        True if user has required role, False otherwise
    """
    import streamlit as st
    
    if "user" not in st.session_state:
        return False
    
    user = st.session_state.user
    return user.get("role") == required_role.lower()
