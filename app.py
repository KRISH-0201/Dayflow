"""
Dayflow HRMS - Main Application
STRICT role-based access control
"""

import streamlit as st
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

# Import pages
from pages import login, employee_dashboard, admin_dashboard

# ======================================================
# PAGE CONFIG (ONLY ONCE)
# ======================================================
st.set_page_config(
    page_title="Dayflow HRMS",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ======================================================
# SESSION STATE INIT
# ======================================================
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if "user" not in st.session_state:
    st.session_state.user = None


def main():
    """Main controller"""

    # --------------------------------------------------
    # NOT LOGGED IN → LOGIN PAGE
    # --------------------------------------------------
    if not st.session_state.authenticated:
        login.show()
        return

    # --------------------------------------------------
    # LOGGED IN → ROLE BASED DASHBOARD
    # --------------------------------------------------
    user = st.session_state.user
    role = user.get("role", "employee").lower()

    # ---------------- SIDEBAR ----------------
    with st.sidebar:
        st.markdown("# 🏢 Dayflow HRMS")
        st.markdown(f"### 👤 {user.get('name')}")
        st.markdown(f"**Role:** {role.upper()}")
        st.markdown(f"**Email:** {user.get('email')}")
        st.divider()

        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.user = None
            st.rerun()

    # ---------------- STRICT ROUTING ----------------
    if role == "admin":
        # ✅ Admin ONLY sees admin dashboard
        admin_dashboard.show()
    elif role == "employee":
        # ✅ Employee ONLY sees employee dashboard
        employee_dashboard.show()
    else:
        # ❌ Unknown role = blocked
        st.error("❌ Unauthorized role")
        st.stop()


if __name__ == "__main__":
    main()
