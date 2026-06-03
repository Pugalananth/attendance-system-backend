from deepface import DeepFace

import base64
import os
import uuid

from PIL import Image
from io import BytesIO

# ─────────────────────────────
# CREATE TEMP IMAGE
# ─────────────────────────────

def save_temp_image(base64_image):

    try:

        # Create temp folder
        os.makedirs(
            "temp_faces",
            exist_ok=True
        )

        # Decode image
        image_data = base64.b64decode(
            base64_image
        )

        # Open image
        image = Image.open(
            BytesIO(image_data)
        )

        # Generate filename
        filename = f"{uuid.uuid4()}.jpg"

        filepath = os.path.join(
            "temp_faces",
            filename
        )

        # Save image
        image.save(filepath)

        return filepath

    except Exception as e:

        print(e)

        return None


# ─────────────────────────────
# REGISTER FACE
# ─────────────────────────────

def register_face(base64_image):

    try:

        image_path = save_temp_image(
            base64_image
        )

        if image_path is None:

            return {
                "success": False,
                "message": "Image save failed",
            }

        # Analyze face
        analysis = DeepFace.analyze(

            img_path=image_path,

            actions=['age', 'gender'],

            enforce_detection=True
        )

        return {

            "success": True,

            "message": "Face registered successfully",

            "face_path": image_path,

            "analysis": analysis,
        }

    except Exception as e:

        print(e)

        return {

            "success": False,

            "message": str(e),
        }


# ─────────────────────────────
# VERIFY FACE
# ─────────────────────────────

def verify_face(

    registered_face,

    current_face

):

    try:

        registered_path = save_temp_image(
            registered_face
        )

        current_path = save_temp_image(
            current_face
        )

        if not registered_path \
            or not current_path:

            return {

                "success": False,

                "verified": False,

                "message": "Image processing failed",
            }

        # Compare faces
        result = DeepFace.verify(

            img1_path=registered_path,

            img2_path=current_path,

            enforce_detection=True
        )

        return {

            "success": True,

            "verified": result["verified"],

            "distance": result["distance"],
        }

    except Exception as e:

        print(e)

        return {

            "success": False,

            "verified": False,

            "message": str(e),
        }