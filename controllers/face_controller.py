"""
Face Recognition Controller
Handles face registration and verification using DeepFace
Professional Corporate Edition
"""

import os
import uuid
from datetime import datetime, timezone
from flask import request, jsonify
from bson import ObjectId
import logging
import numpy as np
import traceback

from utils.db import get_db
from utils.face_utils import (
    base64_to_image,
    validate_face_image,
    preprocess_image,
    generate_embedding,
    compute_average_embedding,
    verify_face,
    anti_spoof_check,
    save_image,
)
from models.face_model import create_face_doc, serialize_face

logger = logging.getLogger(__name__)

MAX_REGISTRATION_IMAGES = 5

def register_face():
    """
    POST /api/face/register
    Register face for an employee.
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "message": "Request body required"}), 400

        employee_id = str(data.get("employee_id", "")).strip()
        images_b64 = data.get("images", [])

        if not images_b64 and data.get("image"):
            images_b64 = [data.get("image")]

        if not employee_id:
            return jsonify({"success": False, "message": "Employee ID required"}), 400

        if not images_b64:
            return jsonify({"success": False, "message": "Face images required"}), 400

        db = get_db()
        user = db["users"].find_one({"employee_id": employee_id})
        if not user:
            return jsonify({"success": False, "message": f"Employee {employee_id} not found"}), 404

        user_id = str(user["_id"])
        employee_name = user.get("name", "Unknown")

        images_b64 = images_b64[:MAX_REGISTRATION_IMAGES]
        embeddings = []
        saved_paths = []

        for idx, img_b64 in enumerate(images_b64):
            try:
                image = base64_to_image(img_b64)
                validation = validate_face_image(image)
                if not validation["valid"]:
                    logger.warning(f"Registration image {idx} invalid: {validation['error']}")
                    continue

                liveness = anti_spoof_check(image)
                if not liveness["is_live"]:
                    logger.warning(f"Registration image {idx} failed liveness")
                    continue

                processed = preprocess_image(image)
                embedding = generate_embedding(processed)
                embeddings.append(embedding)

                filename = f"{employee_id}_{idx}_{uuid.uuid4().hex[:5]}.jpg"
                path = save_image(processed, filename)
                saved_paths.append(path)
            except Exception as e:
                logger.error(f"Image processing error at index {idx}: {str(e)}")
                continue

        if not embeddings:
            return jsonify({"success": False, "message": "Face not detected clearly. Ensure good lighting and look directly at camera."}), 400

        avg_embedding = compute_average_embedding(embeddings)

        # Cleanup existing records
        db["faces"].delete_many({"$or": [
            {"employee_id": employee_id},
            {"user_id": user_id},
            {"student_id": employee_id} # Legacy support
        ]})

        face_doc = create_face_doc(
            user_id=user_id,
            employee_id=employee_id,
            employee_name=employee_name,
            embeddings=embeddings,
            image_paths=saved_paths,
        )
        face_doc["avg_embedding"] = avg_embedding

        db["faces"].insert_one(face_doc)

        db["users"].update_one(
            {"_id": user["_id"]},
            {"$set": {
                "face_registered": True,
                "face_registered_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc)
            }},
        )

        return jsonify({
            "success": True,
            "message": f"Biometric profile secured for {employee_name}",
            "data": {"employee_id": employee_id}
        }), 201

    except Exception as e:
        logger.error(f"Face registration critical error: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({"success": False, "message": f"Server Error: {str(e)}"}), 500


def verify_face_endpoint():
    """
    POST /api/face/verify
    Verify face image against registered data.
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "message": "Request body required"}), 400

        image_b64 = data.get("image", "")
        employee_id = data.get("employee_id", "").strip()

        if not image_b64:
            return jsonify({"success": False, "message": "Capture required"}), 400

        # Process image
        try:
            image = base64_to_image(image_b64)
            processed = preprocess_image(image)
            probe_embedding = generate_embedding(processed)
        except Exception as e:
            logger.error(f"Preprocessing/Embedding error: {str(e)}")
            return jsonify({"success": False, "message": str(e)}), 400

        db = get_db()

        # Comprehensive lookup: Search by employee_id, student_id, user_id, or name
        face_doc = None
        if employee_id:
            # 1. Try direct employee_id
            face_doc = db["faces"].find_one({"employee_id": employee_id, "is_active": True})

            # 2. Try legacy student_id
            if not face_doc:
                face_doc = db["faces"].find_one({"student_id": employee_id, "is_active": True})

            # 3. Try lookup via user object
            if not face_doc:
                user = db["users"].find_one({"employee_id": employee_id})
                if user:
                    face_doc = db["faces"].find_one({
                        "$or": [
                            {"user_id": str(user["_id"])},
                            {"employee_name": user.get("name")},
                            {"student_id": user.get("employee_id")}
                        ],
                        "is_active": True
                    })

        if not face_doc:
            return jsonify({"success": False, "message": "No registered biometric profile found"}), 404

        # Verify
        try:
            # Use avg_embedding if available, otherwise embeddings list
            stored_data = face_doc.get("embeddings", [])
            if not stored_data:
                return jsonify({"success": False, "message": "Biometric record is empty"}), 500

            result = verify_face(probe_embedding, stored_data)
        except Exception as e:
            logger.error(f"Verification engine error: {str(e)}")
            return jsonify({"success": False, "message": "Recognition engine failure"}), 500

        if result["verified"]:
            return jsonify({
                "success": True,
                "verified": True,
                "message": "Identity confirmed",
                "data": {"confidence": result["confidence"]}
            }), 200
        else:
            return jsonify({
                "success": True,
                "verified": False,
                "message": "Face match failed",
                "confidence": result["confidence"]
            }), 200

    except Exception as e:
        logger.error(f"Verification critical failure: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({"success": False, "message": f"Biometric Error: {str(e)}"}), 500

def get_face_status(employee_id):
    try:
        db = get_db()
        face_doc = db["faces"].find_one({
            "$or": [{"employee_id": employee_id}, {"student_id": employee_id}],
            "is_active": True
        })
        return jsonify({"success": True, "data": {"registered": face_doc is not None}}), 200
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

def delete_face(employee_id):
    try:
        db = get_db()
        db["faces"].delete_many({"$or": [{"employee_id": employee_id}, {"student_id": employee_id}]})
        db["users"].update_one({"employee_id": employee_id}, {"$set": {"face_registered": False}})
        return jsonify({"success": True, "message": "Biometric data cleared"}), 200
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
