"""
Pages Package Initialization
Allows importing pages as modules
"""

from . import login
from . import employee_dashboard
from . import admin_dashboard

__all__ = ["login", "employee_dashboard", "admin_dashboard"]
