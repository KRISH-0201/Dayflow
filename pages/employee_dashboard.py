"""
Employee Dashboard Page
View profile, salary (read-only), attendance, and leave management
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import sys
from pathlib import Path
import base64

# Allow imports from project root
sys.path.insert(0, str(Path(__file__).parent.parent))

from database import attendance_col, leave_requests_col, employees_col


# ======================================================
# Helpers
# ======================================================
def encode_image_to_base64(uploaded_file):
    try:
        return base64.b64encode(uploaded_file.read()).decode("utf-8")
    except Exception:
        return None


def decode_base64_image(base64_str):
    try:
        if not base64_str or not isinstance(base64_str, str):
            return None
        return base64.b64decode(base64_str)
    except Exception:
        return None


def show():
    """Display employee dashboard"""

    st.set_page_config(
        page_title="Employee Dashboard",
        page_icon="👤",
        layout="wide"
    )

    # -------------------------
    # AUTH CHECK
    # -------------------------
    if "user" not in st.session_state:
        st.error("❌ Please login first")
        st.stop()

    user = st.session_state.user
    employee_id = user.get("employee_id")

    # -------------------------
    # FETCH OR CREATE PROFILE
    # -------------------------
    employee = employees_col.find_one({"employee_id": employee_id})

    if employee is None:
        employees_col.insert_one({
            "employee_id": employee_id,
            "name": user.get("name", ""),
            "department": "Not Assigned",
            "designation": "Employee",
            "job_details": {
                "joining_date": datetime.now(),
                "employment_type": "Full-time",
                "manager": "-"
            },
            "leaves_balance": {
                "paid": 20,
                "sick": 10,
                "unpaid": 5
            },
            "salary_structure": {
                "basic": 0,
                "hra": 0,
                "allowances": 0,
                "deductions": 0
            },
            "contact": {
                "email": user.get("email", ""),
                "phone": "",
                "address": ""
            },
            "documents": [],
            "profile_picture": None
        })
        employee = employees_col.find_one({"employee_id": employee_id})

    # -------------------------
    # HEADER
    # -------------------------
    st.markdown(f"# 👋 Welcome, {employee.get('name')}!")
    st.markdown(f"Employee ID: **{employee_id}**")
    st.markdown("---")

    # -------------------------
    # METRICS
    # -------------------------
    col1, col2, col3, col4 = st.columns(4)

    today = datetime.now()
    month_start = datetime(today.year, today.month, 1)

    records = list(attendance_col.find({
        "employee_id": employee_id,
        "date": {"$gte": month_start}
    }))

    present = sum(1 for r in records if r["status"] == "present")
    absent = sum(1 for r in records if r["status"] == "absent")

    lb = employee.get("leaves_balance", {})

    col1.metric("📊 Present", present)
    col2.metric("❌ Absent", absent)
    col3.metric("🎫 Paid Leaves", lb.get("paid", 0))
    col4.metric("🏥 Sick Leaves", lb.get("sick", 0))

    st.markdown("---")

    # -------------------------
    # TABS
    # -------------------------
    tab1, tab2, tab3, tab4 = st.tabs([
        "👤 Profile",
        "📅 Attendance",
        "📋 Leave Requests",
        "🗓️ Apply Leave"
    ])

    # ======================================================
    # TAB 1: PROFILE
    # ======================================================
    with tab1:
        col_left, col_right = st.columns([1, 2])

        # LEFT – PROFILE PHOTO
        with col_left:
            st.markdown("### 🖼️ Profile Photo")

            img_bytes = decode_base64_image(employee.get("profile_picture"))

            if img_bytes:
                st.image(img_bytes, width=130)
            else:
                st.image(
                    "https://via.placeholder.com/130x130.png?text=EMP",
                    width=130
                )

            uploaded = st.file_uploader(
                "Upload new photo",
                type=["png", "jpg", "jpeg"]
            )

            if uploaded:
                encoded = encode_image_to_base64(uploaded)
                if encoded:
                    employees_col.update_one(
                        {"employee_id": employee_id},
                        {"$set": {"profile_picture": encoded}}
                    )
                    st.success("Profile photo updated")
                    st.rerun()
                else:
                    st.error("Invalid image file")

            st.write(f"**Name:** {employee.get('name')}")
            st.write(f"**Department:** {employee.get('department')}")
            st.write(f"**Designation:** {employee.get('designation')}")

        # RIGHT – DETAILS + SALARY
        with col_right:
            st.markdown("### 🧾 Job Details")

            job = employee.get("job_details", {})
            st.write(f"**Joining Date:** {job.get('joining_date')}")
            st.write(f"**Employment Type:** {job.get('employment_type')}")
            st.write(f"**Manager:** {job.get('manager')}")

            st.markdown("### 💰 Salary Structure (Read Only)")
            salary = employee.get("salary_structure", {})

            basic = salary.get("basic", 0)
            hra = salary.get("hra", 0)
            allowances = salary.get("allowances", 0)
            deductions = salary.get("deductions", 0)

            gross = basic + hra + allowances
            net = gross - deductions

            c1, c2 = st.columns(2)
            c1.metric("Basic", f"₹{basic:,.0f}")
            c1.metric("HRA", f"₹{hra:,.0f}")
            c1.metric("Allowances", f"₹{allowances:,.0f}")
            c2.metric("Deductions", f"₹{deductions:,.0f}")
            c2.metric("Gross", f"₹{gross:,.0f}")
            c2.metric("Net Salary", f"₹{net:,.0f}")

            st.markdown("### ✏️ Contact Details")
            contact = employee.get("contact", {})
            phone = st.text_input("Phone", contact.get("phone", ""))
            address = st.text_area("Address", contact.get("address", ""), height=80)

            if st.button("💾 Save Contact"):
                employees_col.update_one(
                    {"employee_id": employee_id},
                    {"$set": {
                        "contact.phone": phone,
                        "contact.address": address
                    }}
                )
                st.success("Contact updated")
                st.rerun()

    # ======================================================
    # TAB 2: ATTENDANCE
    # ======================================================
    with tab2:
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

    # ======================================================
    # TAB 3: LEAVE REQUESTS
    # ======================================================
    with tab3:
        leaves = list(leave_requests_col.find({"employee_id": employee_id}))
        if leaves:
            for l in leaves:
                with st.expander(f"{l['leave_type'].upper()} | {l['status'].upper()}"):
                    st.write(f"From: {l['start_date'].date()}")
                    st.write(f"To: {l['end_date'].date()}")
                    st.write(f"Days: {l['days']}")
                    st.write(f"Reason: {l['reason']}")
        else:
            st.info("No leave requests")

    # ======================================================
    # TAB 4: APPLY LEAVE
    # ======================================================
    with tab4:
        leave_type = st.selectbox("Leave Type", ["paid", "sick", "unpaid"])
        start_date = st.date_input("Start Date", datetime.now().date())
        end_date = st.date_input("End Date", datetime.now().date() + timedelta(days=1))
        reason = st.text_area("Reason")

        if st.button("📤 Submit Leave"):
            if start_date > end_date:
                st.error("End date must be after start date")
            else:
                leave_requests_col.insert_one({
                    "employee_id": employee_id,
                    "start_date": datetime(start_date.year, start_date.month, start_date.day),
                    "end_date": datetime(end_date.year, end_date.month, end_date.day),
                    "leave_type": leave_type,
                    "reason": reason,
                    "days": (end_date - start_date).days + 1,
                    "status": "pending",
                    "applied_at": datetime.now()
                })
                st.success("Leave request submitted")
                st.balloons()
                st.rerun()


if __name__ == "__main__":
    show()
