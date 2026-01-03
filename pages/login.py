"""
Login and Signup Page
User authentication interface
"""

import streamlit as st
import sys
from pathlib import Path

# Add parent directory to path to import modules from root
sys.path.insert(0, str(Path(__file__).parent.parent))
from auth import login_user, signup_user

def show():
    """Display login/signup interface"""
    st.set_page_config(
        page_title="Dayflow - Login",
        page_icon="👥",
        layout="centered"
    )
    
    # Custom styling
    st.markdown("""
    <style>
    .login-container {
        max-width: 500px;
        margin: auto;
    }
    .demo-box {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 8px;
        margin-top: 20px;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Main container
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("# 👥 Dayflow HRMS")
        st.markdown("**Human Resource Management System**")
        st.markdown("---")
        
        # Tabs for login and signup
        tab1, tab2 = st.tabs(["🔐 Login", "📝 Signup"])
        
        # LOGIN TAB
        with tab1:
            st.subheader("Login to Your Account")
            
            # Role selection - NEW
            role = st.radio(
                "👤 Select Your Role",
                ["Employee", "Admin"],
                horizontal=True
            )
            
            st.markdown("---")
            
            email = st.text_input(
                "📧 Email",
                key="login_email",
                placeholder="your@email.com"
            )
            password = st.text_input(
                "🔑 Password",
                type="password",
                key="login_pass",
                placeholder="Enter your password"
            )
            
            # Login button
            if st.button(
                "🚀 Login",
                use_container_width=True,
                type="primary",
                key="login_btn"
            ):
                if not email or not password:
                    st.error("❌ Please enter both email and password")
                else:
                    # Convert role to lowercase for comparison
                    selected_role = role.lower()
                    
                    success, result = login_user(email, password)
                    
                    if success:
                        # Check if user role matches selected role - NEW
                        if result.get("role") != selected_role:
                            st.error(f"❌ This account is registered as {result.get('role').upper()}, not {selected_role.upper()}")
                        else:
                            st.session_state.user = result
                            st.session_state.authenticated = True
                            st.session_state.user_role = selected_role
                            st.success("✅ Login successful!")
                            st.balloons()
                            st.rerun()
                    else:
                        st.error(result)
            
            # Demo credentials
            st.markdown("---")
            st.markdown("### 📚 Demo Credentials")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Employee:**")
                st.code("john@company.com\npass123", language="text")
            
            with col2:
                st.markdown("**Admin:**")
                st.code("admin@company.com\nadmin123", language="text")
        
        # SIGNUP TAB
        with tab2:
            st.subheader("Create New Account")
            
            # Role selection for signup - NEW
            signup_role = st.radio(
                "👤 Account Type",
                ["Employee", "Admin"],
                horizontal=True,
                key="signup_role"
            )
            
            st.markdown("---")
            
            name = st.text_input(
                "👤 Full Name",
                key="signup_name",
                placeholder="John Doe"
            )
            email = st.text_input(
                "📧 Email",
                key="signup_email",
                placeholder="your@email.com"
            )
            employee_id = st.text_input(
                "🏢 Employee ID",
                key="signup_empid",
                placeholder="EMP001"
            )
            password = st.text_input(
                "🔑 Password",
                type="password",
                key="signup_pass",
                placeholder="Create a password"
            )
            
            # Signup button
            if st.button(
                "✨ Create Account",
                use_container_width=True,
                type="primary",
                key="signup_btn"
            ):
                if not all([name, email, employee_id, password]):
                    st.error("❌ All fields are required")
                elif len(password) < 6:
                    st.error("❌ Password must be at least 6 characters")
                else:
                    selected_role = signup_role.lower()
                    success, msg = signup_user(email, password, name, employee_id, role=selected_role)
                    
                    if success:
                        st.success(msg)
                        st.info("💡 Switch to Login tab and login with your credentials")
                    else:
                        st.error(msg)

if __name__ == "__main__":
    show()
