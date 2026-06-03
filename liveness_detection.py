import cv2
import mediapipe as mp
import numpy as np

# ==========================================
# MEDIAPIPE SETUP
# ==========================================

mp_face_mesh = mp.solutions.face_mesh


face_mesh = mp_face_mesh.FaceMesh(
    refine_landmarks=True
)

# ==========================================
# EYE LANDMARKS
# ==========================================

LEFT_EYE = [
    33, 160, 158, 133, 153, 144
]

RIGHT_EYE = [
    362, 385, 387, 263, 373, 380
]

# ==========================================
# EAR CALCULATION
# ==========================================

def calculate_ear(eye):

    vertical_1 = np.linalg.norm(
        np.array(eye[1]) -
        np.array(eye[5])
    )

    vertical_2 = np.linalg.norm(
        np.array(eye[2]) -
        np.array(eye[4])
    )

    horizontal = np.linalg.norm(
        np.array(eye[0]) -
        np.array(eye[3])
    )

    ear = (
        vertical_1 +
        vertical_2
    ) / (2.0 * horizontal)

    return ear

# ==========================================
# BLINK DETECTION
# ==========================================

def detect_blink(frame):

    rgb = cv2.cvtColor(
        frame,
        cv2.COLOR_BGR2RGB
    )

    results = face_mesh.process(rgb)

    if not results.multi_face_landmarks:
        return False

    landmarks = results.multi_face_landmarks[0]

    h, w, _ = frame.shape

    left_eye = []
    right_eye = []

    # LEFT EYE

    for idx in LEFT_EYE:

        point = landmarks.landmark[idx]

        left_eye.append(
            (
                int(point.x * w),
                int(point.y * h)
            )
        )

    # RIGHT EYE

    for idx in RIGHT_EYE:

        point = landmarks.landmark[idx]

        right_eye.append(
            (
                int(point.x * w),
                int(point.y * h)
            )
        )

    left_ear = calculate_ear(left_eye)

    right_ear = calculate_ear(right_eye)

    avg_ear = (
        left_ear + right_ear
    ) / 2

    # ======================================
    # BLINK THRESHOLD
    # ======================================

    if avg_ear < 0.21:
        return True

    return False