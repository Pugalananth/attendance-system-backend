"""
Permission Model - Permission Requests
AI Employee Attendance System
"""

from datetime import datetime
from bson import ObjectId

def create_permission_doc(
    user_id,
    employee_id,
    name,
    permission_type,
    start_time,
    end_time,
    reason="",
    status="pending",
):
    """Create permission request document"""
    now = datetime.utcnow()
    
    return {
        "_id": ObjectId(),
        "user_id": user_id,
        "employee_id": employee_id,
        "name": name,
        "permission_type": permission_type,
        "start_time": start_time,
        "end_time": end_time,
        "reason": reason,
        "status": status,  # pending, approved, rejected
        "approved_by": None,
        "approval_date": None,
        "remarks": "",
        "date": now.strftime("%Y-%m-%d"),
        "created_at": now,
        "updated_at": now,
    }

def serialize_permission(doc):
    """Serialize permission document for JSON response"""
    if not doc:
        return None
    
    # Helper to safely convert dates to ISO format or string
    def safe_date(val):
        if val is None: return None
        if isinstance(val, datetime): return val.isoformat()
        return str(val)

    return {
        "id": str(doc["_id"]),
        "user_id": str(doc.get("user_id", "")),
        "employee_id": doc.get("employee_id"),
        "name": doc.get("name"),
        "permission_type": doc.get("permission_type"),
        "start_time": doc.get("start_time"),
        "end_time": doc.get("end_time"),
        "reason": doc.get("reason"),
        "status": doc.get("status"),
        "approved_by": str(doc.get("approved_by")) if doc.get("approved_by") else None,
        "approval_date": safe_date(doc.get("approval_date")),
        "remarks": doc.get("remarks"),
        "date": doc.get("date"),
        "created_at": safe_date(doc.get("created_at")),
        "updated_at": safe_date(doc.get("updated_at")),
    }
