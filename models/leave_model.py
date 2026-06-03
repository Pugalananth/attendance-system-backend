"""
Leave Model - Leave Requests
"""

from datetime import datetime
from bson import ObjectId

def create_leave_doc(
    user_id,
    employee_id,
    name,
    leave_type,  # casual, sick, earned, unpaid
    start_date,
    end_date,
    reason="",
    status="pending",  # pending, approved, rejected
):
    """Create leave request document"""
    now = datetime.utcnow()
    
    return {
        "_id": ObjectId(),
        "user_id": user_id,
        "employee_id": employee_id,
        "name": name,
        "leave_type": leave_type,
        "start_date": start_date,
        "end_date": end_date,
        "reason": reason,
        "status": status,  # pending, approved, rejected
        "approved_by": None,
        "approval_date": None,
        "remarks": "",
        "created_at": now,
        "updated_at": now,
    }

def serialize_leave(doc):
    """Serialize leave document"""
    if not doc:
        return None
    
    return {
        "id": str(doc["_id"]),
        "user_id": str(doc["user_id"]),
        "employee_id": doc.get("employee_id"),
        "name": doc.get("name"),
        "leave_type": doc.get("leave_type"),
        "start_date": doc.get("start_date"),
        "end_date": doc.get("end_date"),
        "reason": doc.get("reason"),
        "status": doc.get("status"),
        "approved_by": doc.get("approved_by"),
        "approval_date": doc.get("approval_date"),
        "remarks": doc.get("remarks"),
        "created_at": str(doc.get("created_at")),
        "updated_at": str(doc.get("updated_at")),
    }
