"""
Face Model - Schema definitions for faces collection
Stores face embeddings and metadata for recognition
"""

from datetime import datetime, timezone
from bson import ObjectId


def create_face_doc(
    user_id: str,
    employee_id: str,
    employee_name: str,
    embeddings: list,
    image_paths: list = None,
) -> dict:
    """Create a new face document for MongoDB."""
    return {
        "_id": ObjectId(),
        "user_id": user_id,
        "employee_id": employee_id,
        "employee_name": employee_name,
        "embeddings": embeddings,          # List of embedding vectors (one per captured image)
        "avg_embedding": None,             # Averaged embedding for fast comparison
        "image_count": len(embeddings),
        "image_paths": image_paths or [],  # Paths to stored face images
        "model_name": "Facenet512",
        "is_active": True,
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
    }


def serialize_face(face: dict) -> dict:
    """Serialize face document for API response (exclude embedding vectors)."""
    if not face:
        return None

    return {
        "id": str(face["_id"]),
        "user_id": face.get("user_id"),
        "employee_id": face.get("employee_id"),
        "image_count": face.get("image_count", 0),
        "model_name": face.get("model_name", "Facenet512"),
        "is_active": face.get("is_active", True),
        "created_at": (
            face["created_at"].isoformat()
            if face.get("created_at")
            else None
        ),
        "updated_at": (
            face["updated_at"].isoformat()
            if face.get("updated_at")
            else None
        ),
    }
