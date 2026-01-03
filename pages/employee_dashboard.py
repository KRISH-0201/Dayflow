"""
Employee Dashboard Page
Display personal information and attendance records
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import sys
from pathlib import Path

# Add parent directory to path to import modules from root
sys.path.insert(0, str(Path(__file__).parent.parent))
from database import employees_col, attendance_col, leave_requests_col, working_hours_col

def show():
    """Display employee dashboard"""
    
    # Initialize session state if not exists
    if "user" not in st.session_state:
        st.error("❌ Please login first")
        st.stop()
    
    user = st.session_state.user
    employee_id = user.get("employee_id")
    
    st.markdown("# 📊 Employee Dashboard")
    st.markdown(f"**Welcome, {user['name']}!**")
    st.markdown("---")
    
    # Get employee details
    if employees_col is None:
        st.error("❌ Database connection failed")
        return
    
    employee = employees_col.find_one({"employee_id": employee_id})
    
    if not employee:
        st.error("❌ Employee record not found")
        return
    
    # Tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📈 Overview",
        "👤 Profile",
        "📋 Attendance",
        "📅 Leave",
        "⏱️ Working Hours"
    ])
    
    # =========================================================
    # TAB 1: OVERVIEW / DASHBOARD
    # =========================================================
    with tab1:
        st.subheader("📈 Dashboard Overview")
        
        col1, col2, col3, col4 = st.columns(4)
        
        # Calculate metrics
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Today's status
        today_attendance = None
        if attendance_col is not None:
            today_attendance = attendance_col.find_one({
                "employee_id": employee_id,
                "date": today
            })
        
        today_status = "Not Marked" if not today_attendance else today_attendance.get("status", "Unknown").upper()
        today_hours = 0
        
        # Today's working hours
        if working_hours_col is not None:
            today_record = working_hours_col.find_one({
                "employee_id": employee_id,
                "date": today
            })
            if today_record:
                today_hours = today_record.get("working_hours", 0)
                check_in = today_record.get("check_in")
                check_out = today_record.get("check_out")
                
                if check_in and not check_out:
                    # Currently checked in - calculate live hours
                    current_time = datetime.now()
                    today_hours = (current_time - check_in).total_seconds() / 3600
        
        with col1:
            st.metric("📋 Today's Status", today_status)
        with col2:
            st.metric("⏱️ Today's Hours", f"{today_hours:.2f} hrs")
        
        # This week's hours
        week_start = today - timedelta(days=today.weekday())
        weekly_hours = 0
        if working_hours_col is not None:
            week_records = list(working_hours_col.find({
                "employee_id": employee_id,
                "date": {"$gte": week_start}
            }))
            weekly_hours = sum(r.get("working_hours", 0) for r in week_records)
        
        with col3:
            st.metric("📅 This Week", f"{weekly_hours:.2f} hrs")
        
        # Pending leaves
        pending_leaves = 0
        if leave_requests_col is not None:
            pending_leaves = leave_requests_col.count_documents({
                "employee_id": employee_id,
                "status": "pending"
            })
        
        with col4:
            st.metric("⏳ Pending Leaves", pending_leaves)
    
    # =========================================================
    # TAB 2: PROFILE (WITH EDIT FUNCTIONALITY)
    # =========================================================
    with tab2:
        st.subheader("👤 Employee Profile")
        
        # Check if we're in edit mode
        edit_mode = st.checkbox("✏️ Edit Profile", key="profile_edit_mode")
        
        if edit_mode:
            st.info("📝 Edit your profile information below")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### 👤 Personal Information")
                name = st.text_input("Name", value=employee.get("name", ""), key="emp_name_edit")
                department = st.text_input("Department", value=employee.get("department", ""), key="emp_dept_edit")
                designation = st.text_input("Designation", value=employee.get("designation", ""), key="emp_desig_edit")
                
                st.markdown("### 📞 Contact Details")
                contact = employee.get("contact", {})
                email = st.text_input("Email", value=contact.get("email", ""), key="emp_email_edit")
                phone = st.text_input("Phone", value=contact.get("phone", ""), key="emp_phone_edit")
                address = st.text_area("Address", value=contact.get("address", ""), key="emp_address_edit", height=80)
                
                profile_picture = st.text_input(
                    "Profile Picture URL",
                    value=employee.get("profile_picture", ""),
                    key="emp_profile_pic_edit"
                )
            
            with col2:
                st.markdown("### 💼 Job Details")
                job = employee.get("job_details", {})
                employment_type = st.text_input(
                    "Employment Type",
                    value=job.get("employment_type", ""),
                    key="emp_emp_type_edit"
                )
                manager = st.text_input(
                    "Manager",
                    value=job.get("manager", ""),
                    key="emp_manager_edit"
                )
                joining_date = job.get("joining_date")
                joining_date_str = joining_date.strftime("%Y-%m-%d") if joining_date else ""
                
                joining_date_input = st.text_input(
                    "Joining Date (YYYY-MM-DD)",
                    value=joining_date_str,
                    key="emp_joining_date_edit"
                )
                
                st.markdown("### 💰 Salary Structure (View Only)")
                salary = employee.get("salary_structure", {})
                st.write(f"**Basic:** ₹{salary.get('basic', 0):,.2f}")
                st.write(f"**HRA:** ₹{salary.get('hra', 0):,.2f}")
                st.write(f"**Allowances:** ₹{salary.get('allowances', 0):,.2f}")
                st.write(f"**Deductions:** ₹{salary.get('deductions', 0):,.2f}")
                total_salary = (salary.get('basic', 0) + salary.get('hra', 0) + 
                               salary.get('allowances', 0) - salary.get('deductions', 0))
                st.write(f"**Total:** ₹{total_salary:,.2f}")
            
            # Save button
            if st.button("💾 Save Profile Changes", use_container_width=True, key="save_profile_changes"):
                try:
                    update_doc = {
                        "name": name,
                        "department": department,
                        "designation": designation,
                        "contact.email": email,
                        "contact.phone": phone,
                        "contact.address": address,
                        "profile_picture": profile_picture,
                        "job_details.employment_type": employment_type,
                        "job_details.manager": manager
                    }
                    
                    if joining_date_input:
                        try:
                            update_doc["job_details.joining_date"] = datetime.strptime(joining_date_input, "%Y-%m-%d")
                        except ValueError:
                            st.warning("⚠️ Joining date format invalid. Use YYYY-MM-DD")
                    
                    employees_col.update_one(
                        {"employee_id": employee_id},
                        {"$set": update_doc}
                    )
                    st.success("✅ Profile updated successfully!")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error updating profile: {e}")
        
        else:
            # View mode (read-only)
            col1, col2 = st.columns([1, 2])
            
            with col1:
                profile_pic = employee.get("profile_picture", "")
                if profile_pic:
                    st.image(profile_pic, width=150)
                else:
                    st.info("📷 No profile picture")
            
            with col2:
                st.markdown("### 👤 Personal Information")
                st.write(f"**Employee ID:** {employee.get('employee_id', '-')}")
                st.write(f"**Name:** {employee.get('name', '-')}")
                st.write(f"**Department:** {employee.get('department', '-')}")
                st.write(f"**Designation:** {employee.get('designation', '-')}")
            
            st.markdown("---")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### 📞 Contact Details")
                contact = employee.get("contact", {})
                st.write(f"**Email:** {contact.get('email', '-')}")
                st.write(f"**Phone:** {contact.get('phone', '-')}")
                st.write(f"**Address:** {contact.get('address', '-')}")
            
            with col2:
                st.markdown("### 💼 Job Details")
                job = employee.get("job_details", {})
                st.write(f"**Employment Type:** {job.get('employment_type', '-')}")
                st.write(f"**Manager:** {job.get('manager', '-')}")
                st.write(f"**Joining Date:** {str(job.get('joining_date', '-'))}")
            
            st.markdown("---")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### 💰 Salary Structure")
                salary = employee.get("salary_structure", {})
                st.write(f"**Basic:** ₹{salary.get('basic', 0):,.2f}")
                st.write(f"**HRA:** ₹{salary.get('hra', 0):,.2f}")
                st.write(f"**Allowances:** ₹{salary.get('allowances', 0):,.2f}")
                st.write(f"**Deductions:** ₹{salary.get('deductions', 0):,.2f}")
                total_salary = (salary.get('basic', 0) + salary.get('hra', 0) + 
                               salary.get('allowances', 0) - salary.get('deductions', 0))
                st.write(f"**Total:** ₹{total_salary:,.2f}")
            
            with col2:
                st.markdown("### 📂 Documents")
                docs = employee.get("documents", [])
                if docs:
                    for d in docs:
                        st.write(f"- [{d.get('title', 'Document')}]({d.get('url', '#')}) ({d.get('type', '')})")
                else:
                    st.info("No documents uploaded")
            
            st.markdown("---")
            
            st.markdown("### 📊 Working Hours Summary")
            col_wh1, col_wh2, col_wh3 = st.columns(3)
            
            # Calculate weekly and monthly working hours
            today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            week_start = today - timedelta(days=today.weekday())
            month_start = today.replace(day=1)
            
            weekly_hours = 0
            monthly_hours = 0
            
            if working_hours_col is not None:
                # Weekly hours
                week_records = list(working_hours_col.find({
                    "employee_id": employee_id,
                    "date": {"$gte": week_start}
                }))
                weekly_hours = sum(r.get("working_hours", 0) for r in week_records)
                
                # Monthly hours
                month_records = list(working_hours_col.find({
                    "employee_id": employee_id,
                    "date": {"$gte": month_start}
                }))
                monthly_hours = sum(r.get("working_hours", 0) for r in month_records)
            
            with col_wh1:
                st.metric("📅 This Week", f"{weekly_hours:.2f} hrs")
            with col_wh2:
                st.metric("📆 This Month", f"{monthly_hours:.2f} hrs")
            with col_wh3:
                st.metric("⏱️ Daily Target", "6 hrs")
    
    # =========================================================
    # TAB 3: ATTENDANCE
    # =========================================================
    with tab3:
        st.subheader("📋 Attendance Records")
        
        # Date range filter
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("From Date", datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=30), key="att_start")
        with col2:
            end_date = st.date_input("To Date", datetime.now().replace(hour=0, minute=0, second=0, microsecond=0), key="att_end")
        
        if attendance_col is not None:
            # ✅ FIX: Use datetime.datetime for database queries
            start_dt = datetime(start_date.year, start_date.month, start_date.day)
            end_dt = datetime(end_date.year, end_date.month, end_date.day, 23, 59, 59)
            
            records = list(attendance_col.find({
                "employee_id": employee_id,
                "date": {"$gte": start_dt, "$lte": end_dt}
            }).sort("date", -1))
            
            if records:
                df = pd.DataFrame([
                    {
                        "Date": r["date"].strftime("%Y-%m-%d"),
                        "Status": "✅ Present" if r["status"] == "present" else "❌ Absent",
                        "Check In": r.get("check_in", "-"),
                        "Check Out": r.get("check_out", "-"),
                        "Hours": f"{r.get('working_hours', 0):.2f}" if r.get('working_hours') else "-"
                    }
                    for r in records
                ])
                
                st.dataframe(df, use_container_width=True, hide_index=True)
                
                # Statistics
                st.markdown("---")
                col1, col2, col3 = st.columns(3)
                present_count = len([r for r in records if r["status"] == "present"])
                absent_count = len([r for r in records if r["status"] == "absent"])
                
                with col1:
                    st.metric("✅ Present", present_count)
                with col2:
                    st.metric("❌ Absent", absent_count)
                with col3:
                    st.metric("📊 Total Days", len(records))
            else:
                st.info("No attendance records found")
    
    # =========================================================
    # TAB 4: LEAVE
    # =========================================================
    with tab4:
        st.subheader("📅 Leave Management")
        
        # Leave request form
        with st.expander("📝 Apply for Leave", expanded=False):
            col1, col2 = st.columns(2)
            with col1:
                leave_type = st.selectbox(
                    "Leave Type",
                    ["Sick Leave", "Casual Leave", "Earned Leave", "Maternity Leave", "Other"]
                )
                start_leave = st.date_input("From Date", key="leave_start")
            
            with col2:
                reason = st.text_input("Reason")
                end_leave = st.date_input("To Date", key="leave_end")
            
            days = (end_leave - start_leave).days + 1
            st.write(f"**Duration:** {days} day(s)")
            
            if st.button("📤 Submit Leave Request", use_container_width=True):
                if leave_requests_col is not None:
                    leave_requests_col.insert_one({
                        "employee_id": employee_id,
                        "leave_type": leave_type,
                        "start_date": datetime(start_leave.year, start_leave.month, start_leave.day),
                        "end_date": datetime(end_leave.year, end_leave.month, end_leave.day),
                        "days": days,
                        "reason": reason,
                        "status": "pending",
                        "applied_on": datetime.now()
                    })
                    st.success("✅ Leave request submitted!")
                    st.rerun()
        
        st.markdown("---")
        
        # Leave requests history
        st.markdown("### 📋 Leave History")
        
        if leave_requests_col is not None:
            leaves = list(leave_requests_col.find({"employee_id": employee_id}).sort("applied_on", -1))
            
            if leaves:
                for leave in leaves:
                    status_color = "🟢" if leave["status"] == "approved" else "🔴" if leave["status"] == "rejected" else "🟡"
                    with st.expander(f"{status_color} {leave['leave_type']} - {leave['start_date'].replace(hour=0, minute=0, second=0, microsecond=0)} to {leave['end_date'].replace(hour=0, minute=0, second=0, microsecond=0)}"):
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write(f"**Status:** {leave['status'].upper()}")
                            st.write(f"**Days:** {leave['days']}")
                            st.write(f"**Reason:** {leave['reason']}")
                        with col2:
                            st.write(f"**Applied On:** {leave['applied_on'].replace(hour=0, minute=0, second=0, microsecond=0)}")
            else:
                st.info("No leave requests found")
    
    # =========================================================
    # TAB 5: WORKING HOURS
    # =========================================================
    with tab5:
        st.subheader("⏱️ Working Hours History")
        
        # Date range filter
        col1, col2 = st.columns(2)
        with col1:
            wh_start_date = st.date_input("From Date", datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=30), key="wh_start")
        with col2:
            wh_end_date = st.date_input("To Date", datetime.now().replace(hour=0, minute=0, second=0, microsecond=0), key="wh_end")
        
        if working_hours_col is not None:
            # ✅ FIX: Use datetime.datetime for database queries
            wh_start_dt = datetime(wh_start_date.year, wh_start_date.month, wh_start_date.day)
            wh_end_dt = datetime(wh_end_date.year, wh_end_date.month, wh_end_date.day, 23, 59, 59)
            
            records = list(working_hours_col.find({
                "employee_id": employee_id,
                "date": {"$gte": wh_start_dt, "$lte": wh_end_dt}
            }).sort("date", -1))
            
            if records:
                df = pd.DataFrame([
                    {
                        "Date": r["date"].strftime("%Y-%m-%d"),
                        "Check In": r.get("check_in", "-"),
                        "Check Out": r.get("check_out", "-"),
                        "Hours": f"{r.get('working_hours', 0):.2f}",
                        "Status": r.get("status", "-").upper()
                    }
                    for r in records
                ])
                
                st.dataframe(df, use_container_width=True, hide_index=True)
                
                # Summary statistics
                st.markdown("---")
                st.markdown("### 📊 Summary Statistics")
                col1, col2, col3, col4 = st.columns(4)
                
                total_hours = sum(r.get("working_hours", 0) for r in records)
                avg_hours = total_hours / len(records) if records else 0
                checked_out = len([r for r in records if r.get("status") == "checked_out"])
                days_below_6 = len([r for r in records if r.get("working_hours", 0) < 6])
                
                with col1:
                    st.metric("Total Hours", f"{total_hours:.2f}")
                with col2:
                    st.metric("Average/Day", f"{avg_hours:.2f}")
                with col3:
                    st.metric("Days Tracked", checked_out)
                with col4:
                    st.metric("Below 6hrs", days_below_6)
            else:
                st.info("No working hours records found for selected period")

if __name__ == "__main__":
    show()