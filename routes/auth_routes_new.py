"""
Authentication Routes
"""

from flask import Blueprint
from flask_jwt_extended import JWTManager
from controllers.auth_controller_new import (
    login_user,
    register_user,
)
from utils.db import get_db

auth_bp = Blueprint(
    'auth',
    __name__,
    url_prefix='/api/auth'
)

@auth_bp.route('/login', methods=['POST'])
def login():
    db = get_db()
    return login_user(db)

@auth_bp.route('/register', methods=['POST'])
def register():
    db = get_db()
    return register_user(db)
