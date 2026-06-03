"""
Work From Home Model - WFH Requests
"""

from datetime import datetime
from bson import ObjectId

def create_wfh_doc(
    user_id,
    employee_id,
    name,
    start_date,
    end_date,
    reason="",
    status="pending",
):
    """Create work from home request document"""
    now = datetime.utcnow()
    
    return {
        "_id": ObjectId(),
        "user_id": user_id,
        "employee_id": employee_id,
        "name": name,
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

def serialize_wfh(doc):
    """Serialize WFH document"""
    if not doc:
        return None
    
    return {
        "id": str(doc["_id"]),
        "user_id": str(doc["user_id"]),
        "employee_id": doc.get("employee_id"),
        "name": doc.get("name"),
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
