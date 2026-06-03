"""
Leave Routes - Leave Requests
"""

from flask import Blueprint
from flask_jwt_extended import jwt_required
from controllers.leave_controller import (
    create_leave_request,
    get_my_leaves,
    get_pending_leaves,
    approve_leave,
    reject_leave,
)
from utils.db import get_db

leave_bp = Blueprint(
    'leave',
    __name__,
    url_prefix='/api/leave'
)

@leave_bp.route('/request', methods=['POST'])
@jwt_required()
def create_leave():
    db = get_db()
    return create_leave_request(db)

@leave_bp.route('/my-leaves', methods=['GET'])
@jwt_required()
def my_leaves():
    db = get_db()
    return get_my_leaves(db)

@leave_bp.route('/pending', methods=['GET'])
@jwt_required()
def pending_leaves():
    db = get_db()
    return get_pending_leaves(db)

@leave_bp.route('/<leave_id>/approve', methods=['POST'])
@jwt_required()
def approve_leave_request(leave_id):
    db = get_db()
    return approve_leave(db, leave_id)

@leave_bp.route('/<leave_id>/reject', methods=['POST'])
@jwt_required()
def reject_leave_request(leave_id):
    db = get_db()
    return reject_leave(db, leave_id)
