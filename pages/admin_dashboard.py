"""
Admin Dashboard Page
Manage employees and approve/reject leave requests
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import sys
from pathlib import Path

# Add parent directory to path to import modules from root
sys.path.insert(0, str(Path(__file__).parent.parent))
from database import leave_requests_col, employees_col, users_col, attendance_col, working_hours_col

def show():
    """Display admin dashboard"""
    st.set_page_config(
        page_title="Admin Dashboard",
        page_icon="👨‍💼",
        layout="wide"
    )
    
    # Initialize session state if not exists
    if "user" not in st.session_state:
        st.error("❌ Please login first")
        st.stop()
    
    user = st.session_state.user
    
    # Check if user is admin
    if user.get("role") != "admin":
        st.error("❌ Access Denied! Only admins can access this page.")
        st.stop()
    
    st.markdown("# 👨‍💼 Admin Dashboard")
    st.markdown(f"**Logged in as:** {user['name']}")
    st.markdown("---")
    
    # Tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📈 Dashboard",
        "📋 Leave Requests",
        "👥 Employees",
        "📊 Attendance",
        "⏱️ Working Hours"
    ])
    
    # =========================================================
    # TAB 1: DASHBOARD
    # =========================================================
    with tab1:
        st.subheader("📈 Dashboard Overview")
        
        col1, col2, col3, col4 = st.columns(4)
        
        total_employees = 0
        total_pending_leaves = 0
        total_present_today = 0
        total_absent_today = 0
        
        if employees_col is not None:
            total_employees = employees_col.count_documents({})
        
        if leave_requests_col is not None:
            total_pending_leaves = leave_requests_col.count_documents({"status": "pending"})
        
        # ✅ FIX: Use datetime.datetime instead of datetime.date
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        
        if attendance_col is not None:
            today_records = list(attendance_col.find({
                "date": today
            }))
            total_present_today = len([r for r in today_records if r["status"] == "present"])
            total_absent_today = len([r for r in today_records if r["status"] == "absent"])
        
        with col1:
            st.metric("👥 Total Employees", total_employees)
        with col2:
            st.metric("⏳ Pending Leaves", total_pending_leaves)
        with col3:
            st.metric("✅ Present Today", total_present_today)
        with col4:
            st.metric("❌ Absent Today", total_absent_today)
    
    # =========================================================
    # TAB 2: LEAVE REQUESTS
    # =========================================================
    with tab2:
        st.subheader("📋 Leave Requests Management")
        
        if leave_requests_col is not None:
            leaves = list(leave_requests_col.find({}))
            
            if leaves:
                # Filter by status
                status_filter = st.selectbox(
                    "Filter by Status",
                    ["All", "pending", "approved", "rejected"]
                )
                
                if status_filter != "All":
                    leaves = [l for l in leaves if l["status"] == status_filter]
                
                for leave in leaves:
                    with st.expander(
                        f"{leave['leave_type'].upper()} - {leave['employee_id']} - {leave['status'].upper()}"
                    ):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.write(f"**Employee ID:** {leave['employee_id']}")
                            st.write(f"**From:** {leave['start_date'].replace(hour=0, minute=0, second=0, microsecond=0)}")
                            st.write(f"**To:** {leave['end_date'].replace(hour=0, minute=0, second=0, microsecond=0)}")
                            st.write(f"**Days:** {leave['days']}")
                            st.write(f"**Type:** {leave['leave_type'].capitalize()}")
                            st.write(f"**Reason:** {leave['reason']}")
                        
                        with col2:
                            if leave["status"] == "pending":
                                col_a, col_r = st.columns(2)
                                with col_a:
                                    if st.button("✅ Approve", key=f"approve_{leave['_id']}"):
                                        leave_requests_col.update_one(
                                            {"_id": leave["_id"]},
                                            {"$set": {"status": "approved"}}
                                        )
                                        st.success("✅ Leave approved!")
                                        st.rerun()
                                with col_r:
                                    if st.button("❌ Reject", key=f"reject_{leave['_id']}"):
                                        leave_requests_col.update_one(
                                            {"_id": leave["_id"]},
                                            {"$set": {"status": "rejected"}}
                                        )
                                        st.error("❌ Leave rejected!")
                                        st.rerun()
                            else:
                                st.write(f"**Status:** {leave['status'].upper()}")
            else:
                st.info("No leave requests found")
    
    # =========================================================
    # TAB 3: EMPLOYEES
    # =========================================================
    with tab3:
        st.subheader("👥 Manage Employees")
        
        if employees_col is not None and users_col is not None:
            employees = list(employees_col.find({}))
            
            if employees:
                # Dropdown to select employee
                selected_emp_label = st.selectbox(
                    "Select Employee",
                    options=[f"{e['employee_id']} - {e['name']}" for e in employees],
                    key="admin_emp_select"
                )
                emp_id = selected_emp_label.split(" - ")[0]
                emp = employees_col.find_one({"employee_id": emp_id})

                if emp:
                    st.markdown("### 🧾 Full Employee Details (Admin Editable)")
                    col1, col2 = st.columns(2)

                    # LEFT: personal & contact
                    with col1:
                        st.markdown("#### 👤 Personal & Contact")
                        name = st.text_input("Name", value=emp.get("name",""), key="adm_name")
                        department = st.text_input("Department", value=emp.get("department",""), key="adm_dept")
                        designation = st.text_input("Designation", value=emp.get("designation",""), key="adm_desig")

                        contact = emp.get("contact", {})
                        email = st.text_input("Email", value=contact.get("email",""), key="adm_email")
                        phone = st.text_input("Phone", value=contact.get("phone",""), key="adm_phone")
                        address = st.text_area("Address", value=contact.get("address",""), key="adm_address", height=80)

                        profile_picture = st.text_input(
                            "Profile Picture URL",
                            value=emp.get("profile_picture",""),
                            key="adm_profile_pic"
                        )

                    # RIGHT: job, salary, documents
                    with col2:
                        st.markdown("#### 💼 Job Details")
                        job = emp.get("job_details", {})
                        employment_type = st.text_input(
                            "Employment Type",
                            value=job.get("employment_type",""),
                            key="adm_emp_type"
                        )
                        manager = st.text_input(
                            "Manager",
                            value=job.get("manager",""),
                            key="adm_manager"
                        )
                        joining_date_str = st.text_input(
                            "Joining Date (YYYY-MM-DD)",
                            value=str(job.get("joining_date","")),
                            key="adm_joining_date"
                        )

                        st.markdown("#### 💰 Salary Structure")
                        salary = emp.get("salary_structure", {})
                        basic = st.number_input("Basic", value=float(salary.get("basic",0)), step=1000.0, key="adm_basic")
                        hra = st.number_input("HRA", value=float(salary.get("hra",0)), step=1000.0, key="adm_hra")
                        allowances = st.number_input("Allowances", value=float(salary.get("allowances",0)), step=1000.0, key="adm_allow")
                        deductions = st.number_input("Deductions", value=float(salary.get("deductions",0)), step=1000.0, key="adm_deduct")

                        st.markdown("#### 📂 Documents (view only in UI)")
                        docs = emp.get("documents", [])
                        if docs:
                            for d in docs:
                                st.write(f"- [{d.get('title','Document')}]({d.get('url','#')}) ({d.get('type','')})")
                        else:
                            st.write("No documents.")

                    # Save button
                    if st.button("💾 Save All Changes", key="adm_emp_save"):
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
                                "job_details.manager": manager,
                                "salary_structure.basic": basic,
                                "salary_structure.hra": hra,
                                "salary_structure.allowances": allowances,
                                "salary_structure.deductions": deductions
                            }
                            
                            if joining_date_str:
                                try:
                                    update_doc["job_details.joining_date"] = datetime.strptime(joining_date_str, "%Y-%m-%d")
                                except ValueError:
                                    st.warning("⚠️ Joining date format invalid, skipping update for that field.")

                            employees_col.update_one(
                                {"employee_id": emp_id},
                                {"$set": update_doc}
                            )
                            st.success("✅ Employee details updated successfully!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ Error updating employee: {e}")
            else:
                st.info("👥 No employees found")
    
    # =========================================================
    # TAB 4: ATTENDANCE
    # =========================================================
    with tab4:
        st.subheader("📊 Attendance Records")
        
        if attendance_col is not None and employees_col is not None:
            # Date range filter
            col1, col2 = st.columns(2)
            with col1:
                start_date = st.date_input("From Date", datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=30), key="att_start_admin")
            with col2:
                end_date = st.date_input("To Date", datetime.now().replace(hour=0, minute=0, second=0, microsecond=0), key="att_end_admin")
            
            # ✅ FIX: Convert date to datetime.datetime
            start_dt = datetime(start_date.year, start_date.month, start_date.day)
            end_dt = datetime(end_date.year, end_date.month, end_date.day, 23, 59, 59)
            
            # Get all employees for filter
            employees = list(employees_col.find({}))
            emp_filter = st.multiselect(
                "Select Employees",
                options=[f"{e['employee_id']} - {e['name']}" for e in employees],
                default=[f"{employees[0]['employee_id']} - {employees[0]['name']}"] if employees else [],
                key="att_emp_filter"
            )
            
            if emp_filter:
                emp_ids = [e.split(" - ")[0] for e in emp_filter]
                
                all_records = []
                for emp_id in emp_ids:
                    records = list(attendance_col.find({
                        "employee_id": emp_id,
                        "date": {"$gte": start_dt, "$lte": end_dt}
                    }).sort("date", -1))
                    
                    for r in records:
                        emp_data = employees_col.find_one({"employee_id": emp_id})
                        all_records.append({
                            "Employee ID": emp_id,
                            "Employee Name": emp_data["name"] if emp_data else "-",
                            "Date": r["date"].strftime("%Y-%m-%d"),
                            "Status": r["status"].upper(),
                            "Check In": r.get("check_in", "-"),
                            "Check Out": r.get("check_out", "-"),
                            "Hours": f"{r.get('working_hours', 0):.2f}" if r.get('working_hours') else "-"
                        })
                
                if all_records:
                    df = pd.DataFrame(all_records)
                    st.dataframe(df, use_container_width=True, hide_index=True)
                else:
                    st.info("No attendance records found")
    
    # =========================================================
    # TAB 5: WORKING HOURS
    # =========================================================
    with tab5:
        st.subheader("⏱️ Working Hours Tracking")
        
        if employees_col is not None and working_hours_col is not None:
            employees = list(employees_col.find({}))
            
            if employees:
                # Date range filter
                col1, col2 = st.columns(2)
                with col1:
                    start_date = st.date_input("From Date", datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=30), key="wh_start_admin")
                with col2:
                    end_date = st.date_input("To Date", datetime.now().replace(hour=0, minute=0, second=0, microsecond=0), key="wh_end_admin")
                
                # ✅ FIX: Convert date to datetime.datetime
                start_dt = datetime(start_date.year, start_date.month, start_date.day)
                end_dt = datetime(end_date.year, end_date.month, end_date.day)
                
                # Filter by employee
                emp_filter = st.multiselect(
                    "Select Employees",
                    options=[f"{e['employee_id']} - {e['name']}" for e in employees],
                    default=[f"{employees[0]['employee_id']} - {employees[0]['name']}"] if employees else [],
                    key="wh_emp_filter_admin"
                )
                
                if emp_filter:
                    emp_ids = [e.split(" - ")[0] for e in emp_filter]
                    
                    all_hours = []
                    for emp_id in emp_ids:
                        records = list(working_hours_col.find({
                            "employee_id": emp_id,
                            "date": {"$gte": start_dt, "$lte": end_dt}
                        }).sort("date", -1))
                        
                        for r in records:
                            emp_name = employees_col.find_one({"employee_id": emp_id})
                            all_hours.append({
                                "Employee ID": emp_id,
                                "Employee Name": emp_name["name"] if emp_name else "-",
                                "Date": r["date"].strftime("%Y-%m-%d"),
                                "Check In": r.get("check_in", "-"),
                                "Check Out": r.get("check_out", "-"),
                                "Working Hours": f"{r.get('working_hours', 0):.2f}",
                                "Status": r.get("status", "-").upper()
                            })
                    
                    if all_hours:
                        df = pd.DataFrame(all_hours)
                        st.dataframe(df, use_container_width=True, hide_index=True)
                        
                        # Summary statistics
                        st.markdown("---")
                        st.markdown("### 📊 Summary Statistics")
                        col1, col2, col3 = st.columns(3)
                        
                        total_hours = sum(float(r["Working Hours"]) for r in all_hours)
                        avg_hours = total_hours / len(all_hours) if all_hours else 0
                        checked_out = len([r for r in all_hours if r["Status"] == "CHECKED_OUT"])
                        
                        with col1:
                            st.metric("Total Hours", f"{total_hours:.2f}")
                        with col2:
                            st.metric("Average Hours/Day", f"{avg_hours:.2f}")
                        with col3:
                            st.metric("Days Tracked", checked_out)
                    else:
                        st.info("No working hours records found for selected period")

def show_leave_requests():
    """Show leave requests management"""
    show()

if __name__ == "__main__":
    show()