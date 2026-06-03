"""
Team Model - Team Management
"""

from datetime import datetime
from bson import ObjectId

def create_team_doc(
    name,
    team_leader_id,
    department="",
    description="",
):
    """Create team document"""
    now = datetime.utcnow()
    
    return {
        "_id": ObjectId(),
        "name": name,
        "team_leader_id": team_leader_id,
        "department": department,
        "description": description,
        "members": [],  # list of employee_ids
        "created_at": now,
        "updated_at": now,
    }

def serialize_team(doc):
    """Serialize team document"""
    if not doc:
        return None
    
    return {
        "id": str(doc["_id"]),
        "name": doc.get("name"),
        "team_leader_id": str(doc.get("team_leader_id")) if doc.get("team_leader_id") else None,
        "department": doc.get("department"),
        "description": doc.get("description"),
        "members": doc.get("members", []),
        "created_at": str(doc.get("created_at")),
        "updated_at": str(doc.get("updated_at")),
    }
