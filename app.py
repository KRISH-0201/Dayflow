"""
Dayflow HRMS - Main Application
Human Resource Management System
"""

import streamlit as st
import sys
from pathlib import Path
from datetime import datetime

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

# Import page modules
from pages import login, employee_dashboard, admin_dashboard
from database import working_hours_col

# Page configuration
st.set_page_config(
    page_title="Dayflow HRMS",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom theme and styling
st.markdown("""
<style>
    :root {
        --primary-color: #2E86AB;
        --secondary-color: #A23B72;
        --success-color: #06A77D;
        --danger-color: #F18F01;
    }
    
    .sidebar .sidebar-content {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    .main {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.user = None
    st.session_state.user_role = None
    st.session_state.checked_in = False

def main():
    """Main application logic"""
    
    # Check if user is authenticated
    if not st.session_state.authenticated:
        # Show login page
        login.show()
    else:
        # User is authenticated
        user = st.session_state.user
        user_role = user.get("role", "employee").lower()
        employee_id = user.get("employee_id")
        
        # Sidebar
        with st.sidebar:
            st.markdown("# 🏢 Dayflow HRMS")
            st.markdown(f"### 👤 {user['name']}")
            st.markdown(f"**Role:** {user_role.upper()}")
            st.markdown(f"**Email:** {user['email']}")
            st.markdown("---")
            
            # ✅ CHECK-IN / CHECK-OUT for Employees
            if user_role == "employee":
                st.markdown("### ⏱️ Attendance Tracker")
                
                # ✅ FIX: Use datetime.datetime instead of datetime.date
                today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
                today_record = None
                if working_hours_col is not None:
                    today_record = working_hours_col.find_one({
                        "employee_id": employee_id,
                        "date": today
                    })
                
                col1, col2 = st.columns(2)
                
                if today_record is None:
                    # Not checked in
                    with col1:
                        if st.button("✅ Check In", use_container_width=True):
                            working_hours_col.insert_one({
                                "employee_id": employee_id,
                                "date": today,
                                "check_in": datetime.now(),
                                "check_out": None,
                                "working_hours": 0,
                                "status": "checked_in"
                            })
                            st.success("✅ Checked in successfully!")
                            st.rerun()
                elif today_record.get("status") == "checked_in":
                    # Already checked in, show check-out
                    check_in_time = today_record.get("check_in")
                    current_time = datetime.now()
                    hours_worked = (current_time - check_in_time).total_seconds() / 3600
                    
                    st.info(f"⏱️ Worked: {hours_worked:.2f} hours")
                    
                    with col1:
                        if st.button("🔴 Check Out", use_container_width=True):
                            check_out_time = datetime.now()
                            hours = (check_out_time - check_in_time).total_seconds() / 3600
                            
                            # Determine status: absent if < 6 hours, else present
                            status = "absent" if hours < 6 else "present"
                            
                            # Show warning if < 6 hours
                            if hours < 6:
                                st.warning(f"⚠️ You've only worked {hours:.2f} hours. Minimum 6 hours required!")
                                st.warning("❌ You will be marked ABSENT")
                                import time
                                time.sleep(2)
                            
                            # Update working hours record
                            working_hours_col.update_one(
                                {"_id": today_record["_id"]},
                                {"$set": {
                                    "check_out": check_out_time,
                                    "working_hours": round(hours, 2),
                                    "status": "checked_out"
                                }}
                            )
                            
                            # Update attendance record
                            from database import attendance_col
                            attendance_col.update_one(
                                {
                                    "employee_id": employee_id,
                                    "date": today
                                },
                                {
                                    "$set": {
                                        "status": status,
                                        "check_in": check_in_time.strftime("%H:%M %p"),
                                        "check_out": check_out_time.strftime("%H:%M %p"),
                                        "working_hours": round(hours, 2)
                                    }
                                },
                                upsert=True
                            )
                            
                            st.success(f"✅ Checked out! Status: {status.upper()}")
                            st.info(f"Working hours: {hours:.2f} hrs")
                            import time
                            time.sleep(2)
                            st.rerun()
                else:
                    # Already checked out today
                    st.success("✅ Checked out for today")
                    st.metric("Working Hours", today_record.get("working_hours", 0))
            
            st.markdown("---")
            
            # Navigation based on role
            if user_role == "admin":
                st.markdown("### 📊 Admin Menu")
                page = st.radio(
                    "Navigation",
                    ["📈 Dashboard", "👥 Manage Users", "📋 Leave Requests", "📊 Reports"],
                    label_visibility="collapsed"
                )
            else:
                st.markdown("### 📊 Employee Menu")
                st.markdown("📊 Dashboard")
                page = "📊 Dashboard"
            
            st.markdown("---")
            
            # Logout button
            if st.button(
                "🚪 Logout",
                use_container_width=True,
                key="logout_btn"
            ):
                st.session_state.authenticated = False
                st.session_state.user = None
                st.session_state.user_role = None
                st.success("✅ Logged out successfully!")
                st.rerun()
        
        # Route to appropriate page based on role
        if user_role == "admin":
            # Admin pages
            if page == "📈 Dashboard":
                admin_dashboard.show()
            elif page == "👥 Manage Users":
                st.info("👥 Manage Users page coming soon...")
            elif page == "📋 Leave Requests":
                admin_dashboard.show_leave_requests()
            elif page == "📊 Reports":
                st.info("📊 Reports page coming soon...")
        else:
            # Employee: Just show the dashboard (all tabs included)
            employee_dashboard.show()

if __name__ == "__main__":
    main()