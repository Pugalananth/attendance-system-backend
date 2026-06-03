"""
Enterprise JWT Utilities
AI Attendance System Security Layer
"""

import jwt

from functools import wraps

from flask import (
    request,
    jsonify,
)

from datetime import (
    datetime,
    timedelta,
)

from bson import ObjectId

from utils.db import get_db

import os

# =========================================================
# CONFIG
# =========================================================

JWT_SECRET = os.getenv(
    "JWT_SECRET",
    "SUPER_SECRET_ENTERPRISE_KEY"
)

JWT_ALGORITHM = "HS256"

ACCESS_TOKEN_EXPIRE_HOURS = 12

REFRESH_TOKEN_EXPIRE_DAYS = 7

# =========================================================
# ACCESS TOKEN
# =========================================================

def generate_access_token(

    user_id,
    role,
    email,

):

    payload = {

        "user_id":
            user_id,

        "role":
            role,

        "email":
            email,

        "type":
            "access",

        "exp":

            datetime.utcnow()

            + timedelta(
                hours=
                ACCESS_TOKEN_EXPIRE_HOURS
            ),

        "iat":
            datetime.utcnow(),

    }

    token = jwt.encode(

        payload,

        JWT_SECRET,

        algorithm=
            JWT_ALGORITHM

    )

    return token

# =========================================================
# REFRESH TOKEN
# =========================================================

def generate_refresh_token(
    user_id
):

    payload = {

        "user_id":
            user_id,

        "type":
            "refresh",

        "exp":

            datetime.utcnow()

            + timedelta(
                days=
                REFRESH_TOKEN_EXPIRE_DAYS
            ),

        "iat":
            datetime.utcnow(),

    }

    token = jwt.encode(

        payload,

        JWT_SECRET,

        algorithm=
            JWT_ALGORITHM

    )

    return token

# =========================================================
# DECODE TOKEN
# =========================================================

def decode_token(token):

    try:

        payload = jwt.decode(

            token,

            JWT_SECRET,

            algorithms=[
                JWT_ALGORITHM
            ]

        )

        return {

            "valid": True,

            "payload":
                payload,

        }

    except jwt.ExpiredSignatureError:

        return {

            "valid": False,

            "error":
                "Token expired",

        }

    except jwt.InvalidTokenError:

        return {

            "valid": False,

            "error":
                "Invalid token",

        }

# =========================================================
# AUTH DECORATOR
# =========================================================

def require_auth(f):

    @wraps(f)

    def decorated(
        *args,
        **kwargs
    ):

        token = None

        auth_header = request.headers.get(
            "Authorization"
        )

        if auth_header and \
            auth_header.startswith(
                "Bearer "
            ):

            token = auth_header.split(
                " "
            )[1]

        if not token:

            return jsonify({

                "success": False,

                "message":
                    "Authorization token missing"

            }), 401

        result = decode_token(
            token
        )

        if not result["valid"]:

            return jsonify({

                "success": False,

                "message":
                    result["error"]

            }), 401

        payload = result["payload"]

        if payload.get("type") != "access":

            return jsonify({

                "success": False,

                "message":
                    "Invalid access token"

            }), 401

        db = get_db()

        user = db["users"].find_one({

            "_id":
                ObjectId(
                    payload["user_id"]
                ),

            "is_active":
                True,

        })

        if not user:

            return jsonify({

                "success": False,

                "message":
                    "User not found"

            }), 404

        request.current_user = {

            "user_id":
                str(user["_id"]),

            "email":
                user["email"],

            "role":
                user["role"],

            "employee_id":
                user.get(
                    "employee_id"
                ),

        }

        return f(
            *args,
            **kwargs
        )

    return decorated

# =========================================================
# ROLE AUTHORIZATION
# =========================================================

def require_role(role):

    def decorator(f):

        @wraps(f)

        def decorated(
            *args,
            **kwargs
        ):

            current_user = getattr(

                request,

                "current_user",

                None

            )

            if not current_user:

                return jsonify({

                    "success": False,

                    "message":
                        "Unauthorized"

                }), 401

            if current_user["role"] != role:

                return jsonify({

                    "success": False,

                    "message":
                        f"{role} access required"

                }), 403

            return f(
                *args,
                **kwargs
            )

        return decorated

    return decorator

# =========================================================
# ADMIN ACCESS
# =========================================================

def require_admin(f):

    @require_auth

    @wraps(f)

    def decorated(
        *args,
        **kwargs
    ):

        if request.current_user[
            "role"
        ] != "admin":

            return jsonify({

                "success": False,

                "message":
                    "Admin access required"

            }), 403

        return f(
            *args,
            **kwargs
        )

    return decorated

# =========================================================
# HR ACCESS
# =========================================================

def require_hr(f):

    @require_auth

    @wraps(f)

    def decorated(
        *args,
        **kwargs
    ):

        role = str(
            request.current_user[
                "role"
            ]
        ).lower()

        if role not in [
            "hr",
            "admin",
        ]:

            return jsonify({

                "success": False,

                "message":
                    "HR access required"

            }), 403

        return f(
            *args,
            **kwargs
        )

    return decorated

# =========================================================
# TEAM LEADER ACCESS
# =========================================================

def require_teamleader(f):

    @require_auth

    @wraps(f)

    def decorated(
        *args,
        **kwargs
    ):

        if request.current_user[
            "role"
        ] != "teamleader":

            return jsonify({

                "success": False,

                "message":
                    "Team Leader access required"

            }), 403

        return f(
            *args,
            **kwargs
        )

    return decorated

# =========================================================
# EMPLOYEE ACCESS
# =========================================================

def require_employee(f):

    @require_auth

    @wraps(f)

    def decorated(
        *args,
        **kwargs
    ):

        if request.current_user[
            "role"
        ] != "employee":

            return jsonify({

                "success": False,

                "message":
                    "Employee access required"

            }), 403

        return f(
            *args,
            **kwargs
        )

    return decorated
