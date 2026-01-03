"""
Admin Dashboard Page
Manage employees, approve/reject leave requests, view profiles
"""

import streamlit as st
import pandas as pd
from datetime import datetime
import sys
from pathlib import Path

# Allow imports from project root
sys.path.insert(0, str(Path(__file__).parent.parent))

from database import (
    leave_requests_col,
    employees_col,
    users_col,
    attendance_col
)


def show():
    """Display admin dashboard"""

    # ❗ Keep page config ONLY if not already in app.py
    st.set_page_config(
        page_title="Admin Dashboard",
        page_icon="👨‍💼",
        layout="wide"
    )

    # -------------------------
    # AUTH CHECK
    # -------------------------
    if "user" not in st.session_state:
        st.error("❌ Please login first")
        st.stop()

    user = st.session_state.user
    if user.get("role") != "admin":
        st.error("❌ Access denied")
        st.stop()

    st.markdown("# 🔧 Admin Dashboard")
    st.markdown(f"Welcome, **{user.get('name')}**")
    st.markdown("---")

    # -------------------------
    # TABS
    # -------------------------
    tab1, tab2, tab3, tab4 = st.tabs([
        "📥 Pending Leaves",
        "👥 Employees",
        "👤 Manage Employee",
        "📅 Attendance"
    ])

    # ======================================================
    # TAB 1: PENDING LEAVES
    # ======================================================
    with tab1:
        st.subheader("📥 Leave Approval Queue")

        pending = list(leave_requests_col.find({"status": "pending"}))

        if not pending:
            st.success("✅ No pending leave requests")
        else:
            for leave in pending:
                col1, col2, col3 = st.columns([2, 1, 1])

                with col1:
                    st.markdown(
                        f"""
                        **Employee ID:** {leave['employee_id']}  
                        **Type:** {leave['leave_type'].upper()}  
                        **Days:** {leave['days']}  
                        **Period:** {leave['start_date'].date()} → {leave['end_date'].date()}  
                        **Reason:** _{leave['reason']}_
                        """
                    )

                with col2:
                    if st.button("✅ Approve", key=f"approve_{leave['_id']}"):
                        leave_requests_col.update_one(
                            {"_id": leave["_id"]},
                            {"$set": {
                                "status": "approved",
                                "approved_at": datetime.now()
                            }}
                        )
                        st.success("Leave approved")
                        st.rerun()

                with col3:
                    if st.button("❌ Reject", key=f"reject_{leave['_id']}"):
                        leave_requests_col.update_one(
                            {"_id": leave["_id"]},
                            {"$set": {
                                "status": "rejected",
                                "approved_at": datetime.now()
                            }}
                        )
                        st.error("Leave rejected")
                        st.rerun()

                st.divider()

    # ======================================================
    # TAB 2: EMPLOYEES LIST
    # ======================================================
    with tab2:
        st.subheader("👥 All Employees")

        employees = list(users_col.find({"role": "employee"}))

        if employees:
            df = pd.DataFrame([
                {
                    "Employee ID": e["employee_id"],
                    "Name": e.get("name", ""),
                    "Email": e.get("email", "")
                }
                for e in employees
            ])
            st.dataframe(df, use_container_width=True, hide_index=True)

            st.download_button(
                "📥 Download CSV",
                df.to_csv(index=False),
                file_name="employees.csv",
                mime="text/csv"
            )
        else:
            st.info("No employees found")

    # ======================================================
    # TAB 3: MANAGE EMPLOYEE (VIEW + EDIT)
    # ======================================================
    with tab3:
        st.subheader("👤 Manage Employee Profile")

        employees = list(employees_col.find({}))

        if not employees:
            st.info("No employee profiles found")
        else:
            selected_label = st.selectbox(
                "Select Employee",
                [f"{e['employee_id']} - {e['name']}" for e in employees]
            )

            emp_id = selected_label.split(" - ")[0]
            emp = employees_col.find_one({"employee_id": emp_id})

            if emp:
                col1, col2 = st.columns(2)

                # LEFT
                with col1:
                    st.markdown("### 👤 Basic Info")
                    name = st.text_input("Name", emp.get("name", ""))
                    department = st.text_input("Department", emp.get("department", ""))
                    designation = st.text_input("Designation", emp.get("designation", ""))

                    contact = emp.get("contact", {})
                    email = st.text_input("Email", contact.get("email", ""))
                    phone = st.text_input("Phone", contact.get("phone", ""))
                    address = st.text_area("Address", contact.get("address", ""), height=80)

                    profile_picture = st.text_input(
                        "Profile Picture URL",
                        emp.get("profile_picture", "")
                    )

                # RIGHT
                with col2:
                    st.markdown("### 💼 Job Details")
                    job = emp.get("job_details", {})
                    employment_type = st.text_input(
                        "Employment Type",
                        job.get("employment_type", "")
                    )
                    manager = st.text_input("Manager", job.get("manager", ""))

                    joining_date_str = st.text_input(
                        "Joining Date (YYYY-MM-DD)",
                        job.get("joining_date", "").strftime("%Y-%m-%d")
                        if isinstance(job.get("joining_date"), datetime)
                        else ""
                    )

                    st.markdown("### 💰 Salary")
                    salary = emp.get("salary_structure", {})
                    basic = st.number_input("Basic", value=float(salary.get("basic", 0)))
                    hra = st.number_input("HRA", value=float(salary.get("hra", 0)))
                    allowances = st.number_input(
                        "Allowances", value=float(salary.get("allowances", 0))
                    )
                    deductions = st.number_input(
                        "Deductions", value=float(salary.get("deductions", 0))
                    )

                # SAVE
                if st.button("💾 Save Changes"):
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
                            update_doc["job_details.joining_date"] = datetime.strptime(
                                joining_date_str, "%Y-%m-%d"
                            )
                        except ValueError:
                            st.warning("Invalid joining date format")

                    employees_col.update_one(
                        {"employee_id": emp_id},
                        {"$set": update_doc}
                    )

                    st.success("✅ Employee updated successfully")
                    st.rerun()

    # ======================================================
    # TAB 4: ATTENDANCE
    # ======================================================
    with tab4:
        st.subheader("📅 Employee Attendance")

        employees = list(users_col.find({"role": "employee"}))

        if employees:
            selected = st.selectbox(
                "Select Employee",
                employees,
                format_func=lambda x: f"{x['name']} ({x['employee_id']})"
            )

            records = list(attendance_col.find(
                {"employee_id": selected["employee_id"]}
            ).sort("date", -1).limit(30))

            if records:
                df = pd.DataFrame([
                    {
                        "Date": r["date"].strftime("%Y-%m-%d"),
                        "Status": r["status"],
                        "Check In": r.get("check_in", "-"),
                        "Check Out": r.get("check_out", "-")
                    }
                    for r in records
                ])
                st.dataframe(df, use_container_width=True, hide_index=True)
            else:
                st.info("No attendance records")
        else:
            st.info("No employees found")


if __name__ == "__main__":
    show()
