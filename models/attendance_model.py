"""
Attendance Model - Schema definitions for attendance collection
"""

from datetime import datetime, timezone, date
from bson import ObjectId


def create_attendance_doc(
    student_id: str,
    user_id: str,
    student_name: str,
    department: str = None,
    confidence: float = 0.0,
    location: dict = None,
    device_info: str = None,
) -> dict:
    """Create a new attendance document for MongoDB."""
    now = datetime.now(timezone.utc)
    today = now.date().isoformat()

    return {
        "_id": ObjectId(),
        "student_id": student_id,
        "user_id": user_id,
        "student_name": student_name,
        "department": department,
        "date": today,
        "time": now.strftime("%H:%M:%S"),
        "status": "present",
        "confidence": confidence,
        "location": location,
        "device_info": device_info,
        "verified_by": "face_recognition",
        "created_at": now,
    }


def serialize_attendance(record: dict) -> dict:
    """Serialize attendance document for API response."""
    if not record:
        return None

    return {
        "id": str(record["_id"]),
        "student_id": record.get("student_id"),
        "user_id": record.get("user_id"),
        "student_name": record.get("student_name", ""),
        "department": record.get("department"),
        "date": record.get("date"),
        "time": record.get("time"),
        "status": record.get("status", "present"),
        "confidence": record.get("confidence", 0.0),
        "verified_by": record.get("verified_by", "face_recognition"),
        "created_at": (
            record["created_at"].isoformat()
            if record.get("created_at")
            else None
        ),
    }
