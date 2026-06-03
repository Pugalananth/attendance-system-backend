"""
Enterprise Leave Routes
"""

from flask import Blueprint, jsonify, request

from utils.jwt_utils import (
    require_auth,
    require_admin,
    require_hr,
    require_employee,
)

from controllers.leave_controller import (
    request_leave,
    get_my_leave_requests,
    get_all_leave_requests,
    approve_leave,
    reject_leave,
    cancel_leave,
    get_leave_summary,
)

# =====================================================
# BLUEPRINT
# =====================================================

leave_bp = Blueprint(
    "leave",
    __name__,
    url_prefix="/api/leave"
)

def require_hr_access():
    role = str(
        request.current_user.get(
            "role",
            ""
        )
    ).lower()

    if role not in [
        "hr",
        "admin",
    ]:
        return jsonify({
            "success": False,
            "message": "HR access required"
        }), 403

    return None

# =====================================================
# HEALTH
# =====================================================

@leave_bp.route(
    "/health",
    methods=["GET"]
)
def leave_health():
    return jsonify({
        "success": True,
        "service": "Leave",
        "status": "running",
    }), 200

# =====================================================
# REQUEST LEAVE
# =====================================================

@leave_bp.route(
    "/request",
    methods=["POST"]
)
@require_employee
def request_leave_route():
    return request_leave()

# =====================================================
# GET MY LEAVE REQUESTS
# =====================================================

@leave_bp.route(
    "/my-requests",
    methods=["GET"]
)
@require_auth
def my_leave_requests():
    return get_my_leave_requests()

# =====================================================
# GET ALL LEAVE REQUESTS (ADMIN/HR)
# =====================================================

@leave_bp.route(
    "/all",
    methods=["GET"]
)
@require_auth
def all_leave_requests():
    denied = require_hr_access()
    if denied:
        return denied

    return get_all_leave_requests()

# =====================================================
# APPROVE LEAVE REQUEST
# =====================================================

@leave_bp.route(
    "/approve/<leave_id>",
    methods=["POST"]
)
@require_auth
def approve_leave_route(leave_id):
    denied = require_hr_access()
    if denied:
        return denied

    return approve_leave(leave_id)

# =====================================================
# REJECT LEAVE REQUEST
# =====================================================

@leave_bp.route(
    "/reject/<leave_id>",
    methods=["POST"]
)
@require_auth
def reject_leave_route(leave_id):
    denied = require_hr_access()
    if denied:
        return denied

    return reject_leave(leave_id)

# =====================================================
# CANCEL LEAVE REQUEST
# =====================================================

@leave_bp.route(
    "/cancel/<leave_id>",
    methods=["POST"]
)
@require_auth
def cancel_leave_route(leave_id):
    return cancel_leave(leave_id)

# =====================================================
# GET LEAVE SUMMARY
# =====================================================

@leave_bp.route(
    "/summary",
    methods=["GET"]
)
@require_auth
def leave_summary():
    return get_leave_summary()

# =====================================================
# ROUTES LIST
# =====================================================

@leave_bp.route(
    "/routes",
    methods=["GET"]
)
def leave_routes_list():
    return jsonify({
        "success": True,
        "routes": [
            "/api/leave/health",
            "/api/leave/request",
            "/api/leave/my-requests",
            "/api/leave/all",
            "/api/leave/approve/<leave_id>",
            "/api/leave/reject/<leave_id>",
            "/api/leave/cancel/<leave_id>",
            "/api/leave/summary",
        ]
    }), 200
