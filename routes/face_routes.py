"""
Enterprise Face Recognition Routes
"""

from flask import Blueprint

from controllers.face_controller import (
    register_face,
    verify_face_endpoint,
    get_face_status,
    delete_face,
)

from utils.jwt_utils import (
    require_auth,
    require_admin,
)

# =====================================================
# BLUEPRINT
# =====================================================

face_bp = Blueprint(

    "face",

    __name__,

    url_prefix="/api/face"

)

# =====================================================
# HEALTH
# =====================================================

@face_bp.route(
    "/health",
    methods=["GET"]
)

def health():

    return {

        "success": True,

        "service": "Face Recognition",

        "status": "running"

    }, 200


# =====================================================
# REGISTER FACE
# =====================================================

@face_bp.route(
    "/register",
    methods=["POST"]
)

@require_auth

def face_register():

    return register_face()


# =====================================================
# VERIFY FACE
# =====================================================

@face_bp.route(
    "/verify",
    methods=["POST"]
)

@require_auth

def face_verify():

    return verify_face_endpoint()


# =====================================================
# FACE STATUS
# =====================================================

@face_bp.route(
    "/status/<employee_id>",
    methods=["GET"]
)

@require_auth

def face_status(employee_id):

    return get_face_status(employee_id)


# =====================================================
# DELETE FACE
# =====================================================

@face_bp.route(
    "/delete/<employee_id>",
    methods=["DELETE"]
)

@require_admin

def face_delete(employee_id):

    return delete_face(employee_id)


# =====================================================
# TEST ROUTE
# =====================================================

@face_bp.route(
    "/test123",
    methods=["GET"]
)

def test123():

    return {

        "success": True,

        "message":
            "Face Routes Working"

    }, 200