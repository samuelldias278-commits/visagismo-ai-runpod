import math
import os
from functools import lru_cache
from pathlib import Path

import cv2

os.environ.setdefault("MPLCONFIGDIR", str(Path(__file__).resolve().parents[2] / ".matplotlib-cache"))
import mediapipe as mp

from VisagismoAI.config import MODEL_PATH


def _distance(a, b) -> float:
    return math.hypot(a.x - b.x, a.y - b.y)


@lru_cache(maxsize=1)
def _landmarker():
    if not MODEL_PATH.exists():
        raise FileNotFoundError("Modelo Face Landmarker ainda não foi instalado.")
    options = mp.tasks.vision.FaceLandmarkerOptions(
        base_options=mp.tasks.BaseOptions(model_asset_path=str(MODEL_PATH)),
        running_mode=mp.tasks.vision.RunningMode.IMAGE,
        num_faces=1,
        min_face_detection_confidence=0.65,
        min_face_presence_confidence=0.65,
        output_facial_transformation_matrixes=True,
    )
    return mp.tasks.vision.FaceLandmarker.create_from_options(options)


def analyze_face(image_bgr) -> dict:
    image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=image_rgb)
    result = _landmarker().detect(mp_image)
    if not result.face_landmarks:
        return {"detected": False, "reason": "Nenhum rosto foi localizado."}

    points = result.face_landmarks[0]
    face_width = _distance(points[234], points[454])
    face_height = _distance(points[10], points[152])
    jaw_width = _distance(points[172], points[397])
    eye_distance = _distance(points[33], points[263])
    mouth_width = _distance(points[61], points[291])
    if face_width <= 0:
        return {"detected": False, "reason": "Geometria facial inválida."}

    center_x = (points[10].x + points[152].x) / 2
    symmetry_pairs = [(33, 263), (61, 291), (234, 454), (172, 397)]
    deltas = [abs(abs(points[left].x - center_x) - abs(points[right].x - center_x)) for left, right in symmetry_pairs]
    asymmetry = sum(deltas) / len(deltas) / face_width
    surface_indices = [10, 338, 297, 332, 284, 251, 389, 356, 454, 323, 361, 288, 397, 365, 379, 378, 400, 377, 152, 148, 176, 149, 150, 136, 172, 58, 132, 93, 234, 127, 162, 21, 54, 103, 67, 109, 1, 4, 33, 263, 61, 291]
    surface_3d = [
        {"i": index, "x": round((points[index].x - center_x) / face_width, 5),
         "y": round((points[index].y - points[10].y) / face_width, 5),
         "z": round(points[index].z / face_width, 5)}
        for index in surface_indices
    ]
    depth_values = [point["z"] for point in surface_3d]

    return {
        "detected": True,
        "landmarkCount": len(points),
        "filterAnchors": {
            "forehead": {"x": round(points[10].x, 6), "y": round(points[10].y, 6)},
            "leftTemple": {"x": round(points[234].x, 6), "y": round(points[234].y, 6)},
            "rightTemple": {"x": round(points[454].x, 6), "y": round(points[454].y, 6)},
            "chin": {"x": round(points[152].x, 6), "y": round(points[152].y, 6)},
        },
        "measurements": {
            "faceHeightWidthRatio": round(face_height / face_width, 4),
            "jawFaceRatio": round(jaw_width / face_width, 4),
            "eyeFaceRatio": round(eye_distance / face_width, 4),
            "mouthFaceRatio": round(mouth_width / face_width, 4),
            "apparentAsymmetry": round(asymmetry, 4),
        },
        "evaluation2D": {
            "status": "available", "method": "normalized-landmark-proportions",
            "dimensions": ["height", "width"], "confidence": "high",
        },
        "evaluation3D": {
            "status": "partial-surface", "method": "mediapipe-relative-depth",
            "surfacePoints": surface_3d,
            "apparentDepthFaceRatio": round(max(depth_values) - min(depth_values), 4),
            "confidence": "medium", "coverage": "visible facial surface only",
        },
        "source": "mediapipe-face-landmarker",
        "limitations": "Medições normalizadas de superfície aparente; não representam diagnóstico ou osso craniano.",
    }
