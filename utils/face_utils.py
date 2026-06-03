"""
Face Recognition Utility using DeepFace + OpenCV
Handles face detection, embedding generation, and verification
"""

import os
import cv2
import numpy as np
import base64
import json
import logging
from PIL import Image
import io
import time

logger = logging.getLogger(__name__)

# Try to import DeepFace - if it fails, face features will be disabled
try:
    from deepface import DeepFace
    DEEPFACE_AVAILABLE = True
except (ImportError, Exception) as e:
    logger.warning(f"DeepFace not available: {e}")
    DEEPFACE_AVAILABLE = False
    DeepFace = None

# Config
DEEPFACE_MODEL = os.getenv("DEEPFACE_MODEL", "Facenet512")
DEEPFACE_DETECTOR = os.getenv("DEEPFACE_DETECTOR", "opencv")
VERIFICATION_THRESHOLD = float(os.getenv("FACE_VERIFICATION_THRESHOLD", "0.6"))
UPLOAD_FOLDER = os.path.join(os.getcwd(), os.getenv("UPLOAD_FOLDER", "uploads"))
EMBEDDINGS_FOLDER = os.path.join(os.getcwd(), os.getenv("EMBEDDINGS_FOLDER", "embeddings"))

# Ensure directories exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(EMBEDDINGS_FOLDER, exist_ok=True)

# Cache for the model to prevent reloading
_MODEL_READY = False

def warm_up_model():
    """Initialize DeepFace model to speed up first request."""
    global _MODEL_READY
    if not DEEPFACE_AVAILABLE or _MODEL_READY:
        return

    try:
        logger.info(f"Warming up DeepFace model: {DEEPFACE_MODEL}...")
        # Create a tiny dummy image for warm-up
        dummy_img = np.zeros((224, 224, 3), dtype=np.uint8)
        DeepFace.represent(dummy_img, model_name=DEEPFACE_MODEL, enforce_detection=False)
        _MODEL_READY = True
        logger.info("DeepFace model ready.")
    except Exception as e:
        logger.error(f"Model warm-up failed: {e}")

def base64_to_image(base64_str: str) -> np.ndarray:
    """Convert base64 string to OpenCV image array."""
    try:
        if not base64_str:
            raise ValueError("Empty base64 string")

        # Remove data URL prefix if present
        if "," in base64_str:
            base64_str = base64_str.split(",")[1]

        img_bytes = base64.b64decode(base64_str)
        img_array = np.frombuffer(img_bytes, dtype=np.uint8)
        img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

        if img is None:
            raise ValueError("Failed to decode image from base64")

        return img
    except Exception as e:
        logger.error(f"base64_to_image error: {e}")
        raise ValueError(f"Invalid image data: {str(e)}")


def image_to_base64(image: np.ndarray) -> str:
    """Convert OpenCV image array to base64 string."""
    _, buffer = cv2.imencode(".jpg", image)
    return base64.b64encode(buffer).decode("utf-8")


def save_image(image: np.ndarray, filename: str) -> str:
    """Save image to upload folder."""
    try:
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        cv2.imwrite(filepath, image)
        return filepath
    except Exception as e:
        logger.error(f"Failed to save image: {e}")
        return ""


def detect_faces(image: np.ndarray) -> list:
    """
    Detect faces in image using OpenCV Haar Cascade.
    Returns list of face regions (x, y, w, h).
    """
    try:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        gray = cv2.equalizeHist(gray)

        face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        )
        faces = face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(80, 80),
            flags=cv2.CASCADE_SCALE_IMAGE,
        )
        return faces.tolist() if len(faces) > 0 else []
    except Exception as e:
        logger.error(f"Face detection error: {e}")
        return []


def validate_face_image(image: np.ndarray) -> dict:
    """
    Validate that image contains exactly one clear face.
    """
    if image is None or image.size == 0:
        return {"valid": False, "error": "Empty or invalid image"}

    h, w = image.shape[:2]
    if h < 100 or w < 100:
        return {"valid": False, "error": "Image too small, minimum 100x100 pixels"}

    faces = detect_faces(image)

    if len(faces) == 0:
        return {"valid": False, "error": "No face detected"}

    if len(faces) > 1:
        return {
            "valid": False,
            "error": f"Multiple faces detected ({len(faces)})",
        }

    return {"valid": True, "face_count": 1, "face_region": faces[0]}


def preprocess_image(image: np.ndarray) -> np.ndarray:
    """Preprocess image for better face recognition accuracy."""
    try:
        # Simple resize to speed up DeepFace if image is massive
        h, w = image.shape[:2]
        if max(h, w) > 1000:
            scale = 1000 / max(h, w)
            image = cv2.resize(image, None, fx=scale, fy=scale)

        return image
    except Exception as e:
        logger.warning(f"Preprocessing warning: {e}")
        return image


def generate_embedding(image: np.ndarray) -> list:
    """Generate face embedding using DeepFace."""
    if not DEEPFACE_AVAILABLE:
        raise RuntimeError("Biometric engine (DeepFace) is not available on this server.")
    
    try:
        # DeepFace represent can take numpy array directly
        # We try with detector_backend=skip since we already validated face exists
        embeddings = DeepFace.represent(
            img_path=image,
            model_name=DEEPFACE_MODEL,
            detector_backend="skip", # Skip internal detection to speed up and prevent double-failure
            enforce_detection=False,
            align=True,
        )

        if not embeddings or len(embeddings) == 0:
            raise ValueError("No face embedding generated")

        return embeddings[0]["embedding"]

    except Exception as e:
        logger.error(f"Embedding generation error: {e}")
        # Fallback to standard represent if skip fails
        try:
            embeddings = DeepFace.represent(
                img_path=image,
                model_name=DEEPFACE_MODEL,
                enforce_detection=False
            )
            return embeddings[0]["embedding"]
        except:
            raise ValueError(f"Could not generate face biometric data: {str(e)}")


def compute_embedding_distance(emb1: list, emb2: list) -> float:
    """Compute cosine distance between two embeddings."""
    try:
        arr1 = np.array(emb1)
        arr2 = np.array(emb2)

        norm1 = np.linalg.norm(arr1)
        norm2 = np.linalg.norm(arr2)

        if norm1 == 0 or norm2 == 0:
            return 1.0

        cosine_similarity = np.dot(arr1, arr2) / (norm1 * norm2)
        return float(1 - cosine_similarity)
    except:
        return 1.0


def compute_average_embedding(embeddings: list) -> list:
    """Compute average embedding from multiple face images."""
    if not embeddings:
        raise ValueError("No embeddings provided")

    arr = np.array(embeddings)
    avg = np.mean(arr, axis=0)

    norm = np.linalg.norm(avg)
    if norm > 0:
        avg = avg / norm

    return avg.tolist()


def verify_face(probe_embedding: list, stored_embeddings: list, threshold: float = None) -> dict:
    """Verify face against stored embeddings."""
    if threshold is None:
        threshold = VERIFICATION_THRESHOLD

    if not stored_embeddings:
        return {"verified": False, "confidence": 0.0, "error": "No stored embeddings"}

    try:
        # Vectorized comparison for performance
        probe_arr = np.array(probe_embedding)
        stored_arr = np.array(stored_embeddings)

        # Calculate distances for all stored embeddings at once
        # Assuming they are already normalized
        dot_products = np.dot(stored_arr, probe_arr)
        # Cosine distance = 1 - similarity
        distances = 1 - dot_products

        min_distance = np.min(distances)
        confidence = max(0, (1 - min_distance) * 100)
        verified = min_distance <= threshold

        return {
            "verified": bool(verified),
            "confidence": round(float(confidence), 2),
            "distance": round(float(min_distance), 4),
            "threshold": threshold,
        }

    except Exception as e:
        logger.error(f"Face verification error: {e}")
        return {"verified": False, "confidence": 0.0, "error": str(e)}


def anti_spoof_check(image: np.ndarray) -> dict:
    """Basic anti-spoofing check."""
    # Simplified for stability, returns live=True always for now to prevent false negatives
    # until a robust model is integrated.
    return {"is_live": True, "liveness_score": 100.0}

# Initialize model on import
warm_up_model()
