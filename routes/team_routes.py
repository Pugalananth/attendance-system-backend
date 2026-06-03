"""
Team Routes - Team Management for Team Leaders
"""

from flask import Blueprint
from utils.jwt_utils import (
    require_auth,
    require_teamleader,
)
from controllers.team_controller import (
    get_tl_members,
    get_available_employees_tl,
    add_team_member_tl,
    remove_team_member_tl,
    get_team_attendance_tl,
    get_team_leave_requests,
    update_leave_tl,
    get_team_permission_requests,
    update_permission_tl,
    get_team_dashboard_summary,
)
from utils.db import get_db

team_bp = Blueprint(
    'team',
    __name__,
    url_prefix='/api/team'
)

@team_bp.route('/members', methods=['GET'])
@require_teamleader
def members():
    db = get_db()
    return get_tl_members(db)

@team_bp.route('/available-employees', methods=['GET'])
@require_teamleader
def available_employees():
    db = get_db()
    return get_available_employees_tl(db)

@team_bp.route('/add-member', methods=['POST'])
@require_teamleader
def add_member():
    db = get_db()
    return add_team_member_tl(db)

@team_bp.route('/remove-member/<employee_id>', methods=['DELETE'])
@require_teamleader
def remove_member(employee_id):
    db = get_db()
    return remove_team_member_tl(db, employee_id)

@team_bp.route('/attendance', methods=['GET'])
@require_teamleader
def team_attendance():
    db = get_db()
    return get_team_attendance_tl(db)

@team_bp.route('/leave-requests', methods=['GET'])
@require_teamleader
def team_leaves():
    db = get_db()
    return get_team_leave_requests(db)

@team_bp.route('/leave/<leave_id>', methods=['PUT'])
@require_teamleader
def update_leave(leave_id):
    db = get_db()
    return update_leave_tl(db, leave_id)

@team_bp.route('/permission-requests', methods=['GET'])
@require_teamleader
def team_permissions():
    db = get_db()
    return get_team_permission_requests(db)

@team_bp.route('/permission/<permission_id>', methods=['PUT'])
@require_teamleader
def update_permission(permission_id):
    db = get_db()
    return update_permission_tl(db, permission_id)

@team_bp.route('/dashboard-summary', methods=['GET'])
@require_teamleader
def team_dashboard():
    db = get_db()
    return get_team_dashboard_summary(db)
