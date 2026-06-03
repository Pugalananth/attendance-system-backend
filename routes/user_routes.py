"""
User Routes - Profile and User Management
"""

from flask import Blueprint
from flask_jwt_extended import jwt_required
from controllers.user_controller import (
    get_profile,
    update_profile,
    get_user_by_id,
    get_all_employees,
)
from utils.db import get_db

user_bp = Blueprint(
    'user',
    __name__,
    url_prefix='/api/user'
)

@user_bp.route('/profile', methods=['GET'])
@jwt_required()
def profile():
    db = get_db()
    return get_profile(db)

@user_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_user_profile():
    db = get_db()
    return update_profile(db)

@user_bp.route('/employees', methods=['GET'])
@jwt_required()
def all_employees():
    db = get_db()
    return get_all_employees(db)

@user_bp.route('/<user_id>', methods=['GET'])
@jwt_required()
def user_by_id(user_id):
    db = get_db()
    return get_user_by_id(db, user_id)
