"""
Admin Routes - Admin Operations
"""

from flask import Blueprint
from utils.jwt_utils import (
    require_auth,
    require_admin,
)
from controllers.admin_controller import (
    get_all_employees,
    create_employee,
    update_employee_role,
    deactivate_employee,
    get_attendance_analytics,
    get_monthly_report,
    get_company_details,
    update_company_details,
    get_admin_dashboard_summary,
    block_user,
    unblock_user,
    delete_user,
    update_user,
    get_request_history,
)
from utils.db import get_db

admin_bp = Blueprint(
    'admin',
    __name__,
    url_prefix='/api/admin'
)

@admin_bp.route('/employees', methods=['GET'])
@require_admin
def all_employees():
    db = get_db()
    return get_all_employees(db)

@admin_bp.route('/employee/create', methods=['POST'])
@require_admin
def create_emp():
    db = get_db()
    return create_employee(db)

@admin_bp.route('/employee/<user_id>/role', methods=['PUT'])
@require_admin
def update_role(user_id):
    db = get_db()
    return update_employee_role(db, user_id)

@admin_bp.route('/employee/<user_id>/deactivate', methods=['POST'])
@require_admin
def deactivate_emp(user_id):
    db = get_db()
    return deactivate_employee(db, user_id)

@admin_bp.route('/analytics', methods=['GET'])
@require_admin
def analytics():
    db = get_db()
    return get_attendance_analytics(db)

@admin_bp.route('/monthly-report', methods=['GET'])
@require_admin
def monthly_report():
    db = get_db()
    return get_monthly_report(db)

@admin_bp.route('/company', methods=['GET'])
@require_admin
def company_details():
    db = get_db()
    return get_company_details(db)

@admin_bp.route('/company', methods=['PUT'])
@require_admin
def update_company():
    db = get_db()
    return update_company_details(db)

@admin_bp.route('/dashboard-summary', methods=['GET'])
@require_admin
def dashboard_summary():
    db = get_db()
    return get_admin_dashboard_summary(db)

@admin_bp.route('/user/<employee_id>/block', methods=['PUT'])
@require_admin
def block(employee_id):
    db = get_db()
    return block_user(db, employee_id)

@admin_bp.route('/user/<employee_id>/unblock', methods=['PUT'])
@require_admin
def unblock(employee_id):
    db = get_db()
    return unblock_user(db, employee_id)

@admin_bp.route('/user/<employee_id>', methods=['DELETE'])
@require_admin
def delete(employee_id):
    db = get_db()
    return delete_user(db, employee_id)

@admin_bp.route('/user/<employee_id>', methods=['PUT'])
@require_admin
def update(employee_id):
    db = get_db()
    return update_user(db, employee_id)

@admin_bp.route('/requests-history', methods=['GET'])
@require_admin
def requests_history():
    db = get_db()
    return get_request_history(db)
