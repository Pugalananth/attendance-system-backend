"""
Enterprise User Model
AI Attendance Management System - Role-based
"""

import re
import uuid
from datetime import datetime
from werkzeug.security import (
    generate_password_hash,
    check_password_hash,
)
from bson import ObjectId

# =========================================================
# VALIDATE EMAIL
# =========================================================

def validate_email(email):
    pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    return re.match(pattern, email) is not None

# =========================================================
# VALIDATE PASSWORD
# =========================================================

def validate_password(password):
    if len(password) < 8:
        return {
            "valid": False,
            "error": "Password must contain at least 8 characters"
        }
    if not re.search(r"[A-Z]", password):
        return {
            "valid": False,
            "error": "Password must contain uppercase letter"
        }
    if not re.search(r"[a-z]", password):
        return {
            "valid": False,
            "error": "Password must contain lowercase letter"
        }
    if not re.search(r"\d", password):
        return {
            "valid": False,
            "error": "Password must contain number"
        }
    return {"valid": True}

# =========================================================
# HASH & VERIFY PASSWORD
# =========================================================

def hash_password(password):
    return generate_password_hash(password)

def verify_password(password, hashed_password):
    return check_password_hash(hashed_password, password)

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
    team_id=None,
    team_leader_id=None
):
    """
    Create a new user document with role-based fields
    Roles: employee, hr, team_leader, admin
    """
    
    if not employee_id:
        employee_id = f"EMP-{str(uuid.uuid4())[:8]}"
    
    hashed_password = hash_password(password)
    now = datetime.utcnow()
    
    user_doc = {
        "_id": ObjectId(),
        "name": name.strip(),
        "email": email.strip().lower(),
        "password": hashed_password,
        "employee_id": employee_id,
        "role": role,  # employee, hr, team_leader, admin
        "department": department,
        "phone": phone,
        "team_id": team_id,
        "team_leader_id": team_leader_id,
        "designation": "",
        "date_of_joining": None,
        "status": "active",  # active, inactive
        "face_registered": False,
        "created_at": now,
        "updated_at": now,
        "last_login": None,
    }
    
    return user_doc

# =========================================================
# SERIALIZE USER DOCUMENT
# =========================================================

def serialize_user(user_doc):
    """Serialize user document for API response"""
    if not user_doc:
        return None
    
    return {
        "id": str(user_doc["_id"]),
        "name": user_doc.get("name"),
        "email": user_doc.get("email"),
        "employee_id": user_doc.get("employee_id"),
        "role": user_doc.get("role"),
        "department": user_doc.get("department"),
        "phone": user_doc.get("phone"),
        "team_id": user_doc.get("team_id"),
        "team_leader_id": user_doc.get("team_leader_id"),
        "designation": user_doc.get("designation"),
        "date_of_joining": user_doc.get("date_of_joining"),
        "status": user_doc.get("status"),
        "face_registered": user_doc.get("face_registered", False),
        "created_at": str(user_doc.get("created_at")),
        "updated_at": str(user_doc.get("updated_at")),
    }
