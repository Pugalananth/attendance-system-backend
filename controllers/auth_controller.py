"""
Enterprise Authentication Controller
AI Employee Attendance System
"""

import os
import logging

from datetime import (
    datetime,
    timezone,
)

from flask import (
    request,
    jsonify,
)

from bson import ObjectId

from utils.db import get_db

from utils.jwt_utils import (

    generate_access_token,
    generate_refresh_token,
    decode_token,

)

from models.user_model import (

    create_user_doc,
    serialize_user,
    verify_password,
    validate_email,
    validate_password,

)

logger = logging.getLogger(__name__)

# =========================================================
# REGISTER
# =========================================================

def register():

    try:

        data = request.get_json()

        if not data:

            return jsonify({

                "success": False,

                "message":
                    "Request body required"

            }), 400

        # =================================================
        # REQUEST DATA
        # =================================================

        name = str(
            data.get(
                "name",
                ""
            )
        ).strip()

        email = str(
            data.get(
                "email",
                ""
            )
        ).strip().lower()

        password = str(
            data.get(
                "password",
                ""
            )
        )

        role = str(
            data.get(
                "role",
                "employee"
            )
        ).lower()

        employee_id = str(
            data.get(
                "employee_id",
                ""
            )
        ).strip()

        department = str(
            data.get(
                "department",
                ""
            )
        ).strip()

        phone = str(
            data.get(
                "phone",
                ""
            )
        ).strip()

        # =================================================
        # VALIDATION
        # =================================================

        if not name:

            return jsonify({

                "success": False,

                "message":
                    "Name is required"

            }), 400

        if not email:

            return jsonify({

                "success": False,

                "message":
                    "Email is required"

            }), 400

        if not password:

            return jsonify({

                "success": False,

                "message":
                    "Password is required"

            }), 400

        if not validate_email(email):

            return jsonify({

                "success": False,

                "message":
                    "Invalid email format"

            }), 400

        pwd_check = validate_password(
            password
        )

        if not pwd_check["valid"]:

            return jsonify({

                "success": False,

                "message":
                    pwd_check["error"]

            }), 400

        valid_roles = [

            "admin",
            "hr",
            "teamleader",
            "employee",

        ]

        if role not in valid_roles:

            return jsonify({

                "success": False,

                "message":
                    "Invalid role"

            }), 400

        if not employee_id:

            return jsonify({

                "success": False,

                "message":
                    "Employee ID required"

            }), 400

        # =================================================
        # DATABASE
        # =================================================

        db = get_db()

        existing_email = db["users"].find_one({

            "email": email

        })

        if existing_email:

            return jsonify({

                "success": False,

                "message":
                    "Email already registered"

            }), 409

        existing_employee = db["users"].find_one({

            "employee_id":
                employee_id

        })

        if existing_employee:

            return jsonify({

                "success": False,

                "message":
                    "Employee ID already exists"

            }), 409

        # =================================================
        # USER DOC
        # =================================================

        user_doc = create_user_doc(

            name=name,

            email=email,

            password=password,

            role=role,

            employee_id=employee_id,

            department=department,

            phone=phone,

        )

        # =================================================
        # INSERT
        # =================================================

        result = db["users"].insert_one(
            user_doc
        )

        created_user = db["users"].find_one({

            "_id":
                result.inserted_id

        })

        user_id = str(
            result.inserted_id
        )

        # =================================================
        # TOKENS
        # =================================================

        access_token = \
            generate_access_token(

                user_id,

                role,

                email,

            )

        refresh_token = \
            generate_refresh_token(
                user_id
            )

        logger.info(
            f"User registered: {email}"
        )

        # =================================================
        # RESPONSE
        # =================================================

        return jsonify({

            "success": True,

            "message":
                "Registration successful",

            "data": {

                "user":
                    serialize_user(
                        created_user
                    ),

                "access_token":
                    access_token,

                "refresh_token":
                    refresh_token,

                "token_type":
                    "Bearer",

            }

        }), 201

    except Exception as e:

        logger.error(
            f"Registration error: {e}"
        )

        return jsonify({

            "success": False,

            "message":
                str(e)

        }), 500


# =========================================================
# LOGIN
# =========================================================

def login():

    try:

        data = request.get_json()

        if not data:

            return jsonify({

                "success": False,

                "message":
                    "Request body required"

            }), 400

        email = str(
            data.get(
                "email",
                ""
            )
        ).strip().lower()

        password = str(
            data.get(
                "password",
                ""
            )
        )

        if not email or not password:

            return jsonify({

                "success": False,

                "message":
                    "Email and password required"

            }), 400

        db = get_db()

        user = db["users"].find_one({

            "email":
                email,

            "is_active":
                True,

        })

        if not user:

            return jsonify({

                "success": False,

                "message":
                    "Invalid credentials"

            }), 401

        password_valid = verify_password(

            password,

            user["password"]

        )

        if not password_valid:

            return jsonify({

                "success": False,

                "message":
                    "Invalid credentials"

            }), 401

        # =================================================
        # UPDATE LOGIN
        # =================================================

        db["users"].update_one(

            {

                "_id":
                    user["_id"]

            },

            {

                "$set": {

                    "last_login":
                        datetime.now(
                            timezone.utc
                        )

                }

            }

        )

        # =================================================
        # TOKENS
        # =================================================

        user_id = str(
            user["_id"]
        )

        access_token = \
            generate_access_token(

                user_id,

                user["role"],

                user["email"]

            )

        refresh_token = \
            generate_refresh_token(
                user_id
            )

        logger.info(
            f"Login success: {email}"
        )

        # =================================================
        # RESPONSE
        # =================================================

        return jsonify({

            "success": True,

            "message":
                "Login successful",

            "data": {

                "user":
                    serialize_user(
                        user
                    ),

                "access_token":
                    access_token,

                "refresh_token":
                    refresh_token,

                "role":
                    user["role"],

                "token_type":
                    "Bearer",

            }

        }), 200

    except Exception as e:

        logger.error(
            f"Login error: {e}"
        )

        return jsonify({

            "success": False,

            "message":
                str(e)

        }), 500


# =========================================================
# REFRESH TOKEN
# =========================================================

def refresh_token():

    try:

        data = request.get_json()

        if not data:

            return jsonify({

                "success": False,

                "message":
                    "Request body required"

            }), 400

        refresh = data.get(
            "refresh_token"
        )

        if not refresh:

            return jsonify({

                "success": False,

                "message":
                    "Refresh token required"

            }), 400

        result = decode_token(
            refresh
        )

        if not result["valid"]:

            return jsonify({

                "success": False,

                "message":
                    result["error"]

            }), 401

        payload = result["payload"]

        user_id = payload.get(
            "user_id"
        )

        if not user_id:

            return jsonify({

                "success": False,

                "message":
                    "Invalid token payload"

            }), 401

        db = get_db()

        user = db["users"].find_one({

            "_id":
                ObjectId(user_id),

            "is_active":
                True

        })

        if not user:

            return jsonify({

                "success": False,

                "message":
                    "User not found"

            }), 404

        access_token = \
            generate_access_token(

                user_id,

                user["role"],

                user["email"]

            )

        return jsonify({

            "success": True,

            "data": {

                "access_token":
                    access_token,

                "token_type":
                    "Bearer",

            }

        }), 200

    except Exception as e:

        logger.error(
            f"Refresh token error: {e}"
        )

        return jsonify({

            "success": False,

            "message":
                str(e)

        }), 500


# =========================================================
# PROFILE
# =========================================================

def get_profile():

    try:

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

        user_id = current_user.get(
            "user_id"
        )

        db = get_db()

        user = db["users"].find_one({

            "_id":
                ObjectId(user_id)

        })

        if not user:

            return jsonify({

                "success": False,

                "message":
                    "User not found"

            }), 404

        return jsonify({

            "success": True,

            "data": {

                "user":
                    serialize_user(
                        user
                    )

            }

        }), 200

    except Exception as e:

        logger.error(
            f"Profile error: {e}"
        )

        return jsonify({

            "success": False,

            "message":
                str(e)

        }), 500


# =========================================================
# SETUP ADMIN
# =========================================================

def setup_admin():

    try:

        db = get_db()

        existing_admin = \
            db["users"].find_one({

                "role": "admin"

            })

        if existing_admin:

            return jsonify({

                "success": False,

                "message":
                    "Admin already exists"

            }), 409

        admin_email = os.getenv(

            "ADMIN_EMAIL",

            "admin@attendance.com"

        )

        admin_password = os.getenv(

            "ADMIN_PASSWORD",

            "Admin@123456"

        )

        admin_doc = create_user_doc(

            name="System Admin",

            email=admin_email,

            password=admin_password,

            role="admin",

            employee_id="ADMIN001",

            department="Administration",

            phone="0000000000",

        )

        result = db["users"].insert_one(
            admin_doc
        )

        logger.info(
            "Default admin created"
        )

        return jsonify({

            "success": True,

            "message":
                "Admin account created",

            "data": {

                "admin_id":
                    str(result.inserted_id),

                "email":
                    admin_email,

            }

        }), 201

    except Exception as e:

        logger.error(
            f"Setup admin error: {e}"
        )

        return jsonify({

            "success": False,

            "message":
                str(e)

        }), 500