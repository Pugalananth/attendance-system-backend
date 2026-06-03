"""
Permission Routes - Permission Requests
"""

from flask import Blueprint
from utils.jwt_utils import (
    require_auth,
    require_hr,
)
from controllers.permission_controller import (
    create_permission_request,
    get_my_permissions,
    get_pending_permissions,
    get_all_permissions_hr,
    approve_permission,
    reject_permission,
)
from utils.db import get_db

permission_bp = Blueprint(
    'permission',
    __name__
)

@permission_bp.route('/request', methods=['POST'])
@require_auth
def create_permission():
    db = get_db()
    return create_permission_request(db)

@permission_bp.route('/my-permissions', methods=['GET'])
@require_auth
def my_permissions():
    db = get_db()
    return get_my_permissions(db)

@permission_bp.route('/pending', methods=['GET'])
@require_hr
def pending_permissions():
    db = get_db()
    return get_pending_permissions(db)

@permission_bp.route('/history', methods=['GET'])
@require_hr
def permission_history_hr():
    db = get_db()
    return get_all_permissions_hr(db)

@permission_bp.route('/<permission_id>/approve', methods=['POST'])
@require_hr
def approve_permission_request(permission_id):
    db = get_db()
    return approve_permission(db, permission_id)

@permission_bp.route('/<permission_id>/reject', methods=['POST'])
@require_hr
def reject_permission_request(permission_id):
    db = get_db()
    return reject_permission(db, permission_id)
