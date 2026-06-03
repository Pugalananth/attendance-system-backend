"""
Company Model - Company Information
"""

from datetime import datetime
from bson import ObjectId

def create_company_doc(
    name,
    email="",
    phone="",
    address="",
    city="",
    country="",
    working_hours_start="09:00",
    working_hours_end="18:00",
):
    """Create company document"""
    now = datetime.utcnow()
    
    return {
        "_id": ObjectId(),
        "name": name,
        "email": email,
        "phone": phone,
        "address": address,
        "city": city,
        "country": country,
        "logo_url": None,
        "working_hours_start": working_hours_start,
        "working_hours_end": working_hours_end,
        "timezone": "UTC",
        "created_at": now,
        "updated_at": now,
    }

def serialize_company(doc):
    """Serialize company document"""
    if not doc:
        return None
    
    return {
        "id": str(doc["_id"]),
        "name": doc.get("name"),
        "email": doc.get("email"),
        "phone": doc.get("phone"),
        "address": doc.get("address"),
        "city": doc.get("city"),
        "country": doc.get("country"),
        "logo_url": doc.get("logo_url"),
        "working_hours_start": doc.get("working_hours_start"),
        "working_hours_end": doc.get("working_hours_end"),
        "timezone": doc.get("timezone", "UTC"),
        "created_at": str(doc.get("created_at")),
        "updated_at": str(doc.get("updated_at")),
    }
