"""
Face Model - Face Embeddings and Metadata
"""

from datetime import datetime
from bson import ObjectId

def create_face_doc(
    user_id,
    employee_id,
    name,
    face_embedding,
    image_path="",
    confidence=0.0,
):
    """Create face document for face recognition"""
    now = datetime.utcnow()
    
    return {
        "_id": ObjectId(),
        "user_id": user_id,
        "employee_id": employee_id,
        "name": name,
        "face_embedding": face_embedding,  # numpy array or list
        "image_path": image_path,
        "confidence": confidence,
        "registered_at": now,
        "updated_at": now,
    }

def serialize_face(doc):
    """Serialize face document"""
    if not doc:
        return None
    
    return {
        "id": str(doc["_id"]),
        "user_id": str(doc["user_id"]),
        "employee_id": doc.get("employee_id"),
        "name": doc.get("name"),
        "image_path": doc.get("image_path"),
        "confidence": doc.get("confidence", 0.0),
        "registered_at": str(doc.get("registered_at")),
        "updated_at": str(doc.get("updated_at")),
    }
