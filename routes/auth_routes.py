"""
Enterprise Authentication Routes
"""

from flask import Blueprint
from flask import jsonify

from controllers.auth_controller import (

    register,
    login,
    refresh_token,
    get_profile,
    setup_admin,

)

from utils.jwt_utils import (
    require_auth,
)

# =====================================================
# BLUEPRINT
# =====================================================

auth_bp = Blueprint(

    "auth",

    __name__,

    url_prefix="/api/auth"

)

# =====================================================
# TEST ROUTE
# =====================================================

@auth_bp.route(
    "/test123",
    methods=["GET"]
)

def test123():

    return jsonify({

        "success": True,

        "message":
            "TEST ROUTE WORKING"

    }), 200


# =====================================================
# HEALTH
# =====================================================

@auth_bp.route(
    "/health",
    methods=["GET"]
)

def auth_health():

    return jsonify({

        "success": True,

        "service":
            "Authentication",

        "status":
            "running",

    }), 200


# =====================================================
# REGISTER
# =====================================================

@auth_bp.route(
    "/register",
    methods=["POST"]
)

def register_route():

    return register()


# =====================================================
# LOGIN
# =====================================================

@auth_bp.route(
    "/login",
    methods=["POST"]
)

def login_route():

    return login()


# =====================================================
# LOGOUT
# =====================================================

@auth_bp.route(
    "/logout",
    methods=["POST"]
)

@require_auth

def logout_route():

    return jsonify({
        "success": True,
        "message": "Logged out successfully"
    }), 200


# =====================================================
# REFRESH TOKEN
# =====================================================

@auth_bp.route(
    "/refresh",
    methods=["POST"]
)

def refresh_route():

    return refresh_token()


# =====================================================
# SETUP ADMIN
# =====================================================

@auth_bp.route(
    "/setup-admin",
    methods=[
        "GET",
        "POST",
    ]
)

def setup_admin_route():

    return setup_admin()


# =====================================================
# PROFILE
# =====================================================

@auth_bp.route(
    "/profile",
    methods=["GET"]
)

@require_auth

def profile():

    return get_profile()


# =====================================================
# VERIFY TOKEN
# =====================================================

@auth_bp.route(
    "/verify",
    methods=["GET"]
)

@require_auth

def verify():

    return jsonify({

        "success": True,

        "message":
            "Token valid",

        "authenticated":
            True,

    }), 200


# =====================================================
# ROUTE LIST
# =====================================================

@auth_bp.route(
    "/routes",
    methods=["GET"]
)

def auth_routes_list():

    routes = [

        "/api/auth/login",
        "/api/auth/register",
        "/api/auth/logout",
        "/api/auth/profile",
        "/api/auth/refresh",
        "/api/auth/setup-admin",
        "/api/auth/verify",

    ]

    return jsonify({

        "success": True,

        "routes":
            routes

    }), 200

