"""
Attendance Model - Check-in/Check-out Records
"""

from datetime import datetime
from bson import ObjectId

def create_attendance_doc(
    user_id,
    employee_id,
    name,
    check_type,  # "check_in" or "check_out"
    latitude=None,
    longitude=None,
    confidence=0.0,
    device_info="",
):
    """
    Create attendance record (check-in/check-out)
    """
    now = datetime.utcnow()
    
    return {
        "_id": ObjectId(),
        "user_id": user_id,
        "employee_id": employee_id,
        "name": name,
        "check_type": check_type,  # check_in or check_out
        "timestamp": now,
        "date": now.strftime("%Y-%m-%d"),
        "time": now.strftime("%H:%M:%S"),
        "latitude": latitude,
        "longitude": longitude,
        "confidence": confidence,
        "device_info": device_info,
        "verified_by": "face_recognition",
    }

def get_daily_attendance(user_id, date):
    """Get check-in and check-out for a specific date"""
    return {
        "date": date,
        "user_id": user_id,
        "check_in": None,
        "check_out": None,
        "status": "absent"
    }

def serialize_attendance(doc):
    """Serialize attendance document"""
    if not doc:
        return None
    
    return {
        "id": str(doc["_id"]),
        "user_id": str(doc["user_id"]),
        "employee_id": doc.get("employee_id"),
        "name": doc.get("name"),
        "check_type": doc.get("check_type"),
        "timestamp": str(doc.get("timestamp")),
        "date": doc.get("date"),
        "time": doc.get("time"),
        "confidence": doc.get("confidence", 0.0),
        "device_info": doc.get("device_info", ""),
    }
