"""
Enterprise Employee Routes
"""

from flask import Blueprint, jsonify

from utils.jwt_utils import (
    require_auth,
    require_hr,
)

from controllers.employee_controller import (
    get_employee_profile,
    get_employees_for_hr,
    delete_employee_for_hr,
    get_employee_stats,
    update_employee_profile,
    get_employee_dashboard,
    get_hr_dashboard_summary,
    get_hr_analytics,
    update_employee_verification,
    get_recent_activity,
)

# =====================================================
# BLUEPRINT
# =====================================================

employee_bp = Blueprint(
    "employee",
    __name__,
    url_prefix="/api/employee"
)

# =====================================================
# HEALTH
# =====================================================

@employee_bp.route(
    "/health",
    methods=["GET"]
)
def employee_health():
    return jsonify({
        "success": True,
        "service": "Employee",
        "status": "running",
    }), 200

# =====================================================
# HR EMPLOYEE DIRECTORY
# =====================================================

@employee_bp.route(
    "/employees",
    methods=["GET"]
)
@require_auth
def employees():
    return get_employees_for_hr()

@employee_bp.route(
    "/employees/<employee_id>",
    methods=["DELETE"]
)
@require_auth
def delete_employee(employee_id):
    return delete_employee_for_hr(
        employee_id
    )

@employee_bp.route(
    "/employees/<employee_id>/approve",
    methods=["POST"]
)
@require_hr
def approve_employee(employee_id):
    return update_employee_verification(
        employee_id,
        True
    )

@employee_bp.route(
    "/employees/<employee_id>/reject",
    methods=["POST"]
)
@require_hr
def reject_employee(employee_id):
    return update_employee_verification(
        employee_id,
        False
    )

# =====================================================
# GET PROFILE
# =====================================================

@employee_bp.route(
    "/profile",
    methods=["GET"]
)
@require_auth
def profile():
    return get_employee_profile()

# =====================================================
# UPDATE PROFILE
# =====================================================

@employee_bp.route(
    "/profile",
    methods=["PUT"]
)
@require_auth
def update_profile():
    return update_employee_profile()

# =====================================================
# GET STATS
# =====================================================

@employee_bp.route(
    "/stats",
    methods=["GET"]
)
@require_auth
def stats():
    return get_employee_stats()

# =====================================================
# GET DASHBOARD
# =====================================================

@employee_bp.route(
    "/dashboard",
    methods=["GET"]
)
@require_auth
def dashboard():
    return get_employee_dashboard()

# =====================================================
# GET HR DASHBOARD
# =====================================================

@employee_bp.route(
    "/hr-dashboard",
    methods=["GET"]
)
@require_hr
def hr_dashboard():
    return get_hr_dashboard_summary()

# =====================================================
# GET HR ANALYTICS
# =====================================================

@employee_bp.route(
    "/hr-analytics",
    methods=["GET"]
)
@require_hr
def hr_analytics():
    return get_hr_analytics()

# =====================================================
# GET RECENT ACTIVITY
# =====================================================

@employee_bp.route(
    "/activity",
    methods=["GET"]
)
@require_auth
def activity():
    return get_recent_activity()

# =====================================================
# ROUTES LIST
# =====================================================

@employee_bp.route(
    "/routes",
    methods=["GET"]
)
def employee_routes_list():
    return jsonify({
        "success": True,
        "routes": [
            "/api/employee/health",
            "/api/employee/employees",
            "/api/employee/employees/<employee_id>",
            "/api/employee/employees/<employee_id>/approve",
            "/api/employee/employees/<employee_id>/reject",
            "/api/employee/profile",
            "/api/employee/stats",
            "/api/employee/dashboard",
            "/api/employee/hr-dashboard",
            "/api/employee/hr-analytics",
            "/api/employee/activity",
        ]
    }), 200
