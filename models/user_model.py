"""
Enterprise User Model
AI Attendance Management System
"""

import re
import uuid

from datetime import datetime

from werkzeug.security import (
    generate_password_hash,
    check_password_hash,
)

# =========================================================
# VALIDATE EMAIL
# =========================================================

def validate_email(email):

    pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"

    return re.match(
        pattern,
        email
    ) is not None

# =========================================================
# VALIDATE PASSWORD
# =========================================================

def validate_password(password):

    if len(password) < 8:

        return {
            "valid": False,
            "error":
                "Password must contain at least 8 characters"
        }

    if not re.search(r"[A-Z]", password):

        return {
            "valid": False,
            "error":
                "Password must contain uppercase letter"
        }

    if not re.search(r"[a-z]", password):

        return {
            "valid": False,
            "error":
                "Password must contain lowercase letter"
        }

    if not re.search(r"\d", password):

        return {
            "valid": False,
            "error":
                "Password must contain number"
        }

    return {
        "valid": True
    }

# =========================================================
# HASH PASSWORD
# =========================================================

def hash_password(password):

    return generate_password_hash(
        password
    )

# =========================================================
# VERIFY PASSWORD
# =========================================================

def verify_password(
    password,
    hashed_password
):

    return check_password_hash(
        hashed_password,
        password
    )

# =========================================================
# CREATE USER DOCUMENT
# =========================================================

def create_user_doc(

    name,
    email,
    password,
    role="employee",
    employee_id=None,
    department="",
    phone="",

):

    # =====================================================
    # GENERATE EMPLOYEE ID
    # =====================================================

    if not employee_id:

        employee_id = (
            "EMP-" +
            str(uuid.uuid4())[:8]
        )

    # =====================================================
    # HASH PASSWORD
    # =====================================================

    hashed_password = hash_password(
        password
    )

    # =====================================================
    # USER DOCUMENT
    # =====================================================

    user_doc = {

        "name":
            name.strip(),

        "email":
            email.strip().lower(),

        "password":
            hashed_password,

        "employee_id":
            employee_id,

        "role":
            role,

        "department":
            department,

        "phone":
            phone,

        # =============================================
        # FACE AI
        # =============================================

        "face_registered":
            False,

        "face_embeddings":
            None,

        "face_registered_at":
            None,

        # =============================================
        # STATUS
        # =============================================

        "is_active":
            True,

        "is_verified":
            True,

        # =============================================
        # ATTENDANCE
        # =============================================

        "attendance_enabled":
            True,

        "last_login":
            None,

        # =============================================
        # SECURITY
        # =============================================

        "failed_login_attempts":
            0,

        "account_locked":
            False,

        # =============================================
        # TIMESTAMPS
        # =============================================

        "created_at":
            datetime.utcnow(),

        "updated_at":
            datetime.utcnow(),

    }

    return user_doc

# =========================================================
# SERIALIZE USER
# =========================================================

def serialize_user(user):

    return {

        "id":
            str(user["_id"]),

        "name":
            user.get("name"),

        "email":
            user.get("email"),

        "employee_id":
            user.get("employee_id"),

        "role":
            user.get("role"),

        "department":
            user.get("department"),

        "phone":
            user.get("phone"),

        "face_registered":
            user.get(
                "face_registered",
                False
            ),

        "attendance_enabled":
            user.get(
                "attendance_enabled",
                True
            ),

        "is_active":
            user.get(
                "is_active",
                True
            ),

        "is_blocked":
            not user.get(
                "is_active",
                True
            ),

        "created_at":

            user.get(
                "created_at"
            ).isoformat()

            if user.get(
                "created_at"
            )

            else None,

    }

# =========================================================
# ROLE HELPERS
# =========================================================

def is_admin(user):

    return user.get(
        "role"
    ) == "admin"

def is_hr(user):

    return user.get(
        "role"
    ) == "hr"

def is_teamleader(user):

    return user.get(
        "role"
    ) == "teamleader"

def is_employee(user):

    return user.get(
        "role"
    ) == "employee"