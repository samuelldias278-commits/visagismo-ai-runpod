import base64
from functools import lru_cache

import cv2
import numpy as np
import onnxruntime as ort

from VisagismoAI.config import SEGMENTATION_MODEL_PATH

# Este repositório enumera 18 atributos a partir de 1; "hair" ocupa o índice 17.
HAIR_CLASS = 17
MEAN = np.array([0.485, 0.456, 0.406], dtype=np.float32)
STD = np.array([0.229, 0.224, 0.225], dtype=np.float32)


@lru_cache(maxsize=1)
def _session():
    if not SEGMENTATION_MODEL_PATH.exists():
        raise FileNotFoundError("Modelo local de segmentação capilar não encontrado.")
    return ort.InferenceSession(str(SEGMENTATION_MODEL_PATH), providers=["CPUExecutionProvider"])


def _predict(image_bgr: np.ndarray) -> np.ndarray:
    rgb = cv2.cvtColor(cv2.resize(image_bgr, (512, 512)), cv2.COLOR_BGR2RGB)
    tensor = rgb.astype(np.float32) / 255.0
    tensor = ((tensor - MEAN) / STD).transpose(2, 0, 1)[None].astype(np.float32)
    session = _session()
    output = session.run(None, {session.get_inputs()[0].name: tensor})[0]
    labels = output.squeeze(0).argmax(0).astype(np.uint8)
    return cv2.resize(labels, (image_bgr.shape[1], image_bgr.shape[0]), interpolation=cv2.INTER_NEAREST)


def _data_url(mask: np.ndarray) -> str:
    rgba = np.dstack((np.full_like(mask, 255), np.full_like(mask, 255), np.full_like(mask, 255), mask))
    ok, encoded = cv2.imencode(".png", rgba)
    if not ok:
        raise ValueError("Não foi possível codificar a máscara capilar.")
    return "data:image/png;base64," + base64.b64encode(encoded.tobytes()).decode("ascii")


def _boundary(mask: np.ndarray, center_x: int, radius: int, max_y: int) -> int | None:
    x0, x1 = max(0, center_x - radius), min(mask.shape[1], center_x + radius + 1)
    ys = np.where(mask[:max_y, x0:x1] > 0)[0]
    return int(ys.max()) if ys.size else None


def analyze_hair(image_bgr: np.ndarray, geometry: dict) -> dict:
    labels = _predict(image_bgr)
    hair = (labels == HAIR_CLASS).astype(np.uint8) * 255
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
    hair = cv2.morphologyEx(hair, cv2.MORPH_CLOSE, kernel)
    anchors = geometry.get("filterAnchors") if geometry.get("detected") else None
    height, width = hair.shape
    if anchors:
        left_x = int(anchors["leftTemple"]["x"] * width)
        right_x = int(anchors["rightTemple"]["x"] * width)
        forehead_y = int(anchors["forehead"]["y"] * height)
        face_width_hint = max(1, abs(right_x - left_x))
        head_roi = np.zeros_like(hair)
        cv2.ellipse(head_roi, (int((left_x + right_x) / 2), int(forehead_y - face_width_hint * 0.12)), (int(face_width_hint * 0.88), int(face_width_hint * 0.78)), 0, 0, 360, 255, -1)
        hair = cv2.bitwise_and(hair, head_roi)
    pixels = np.argwhere(hair > 0)
    if not pixels.size:
        return {"detected": False, "reason": "Nenhuma região capilar foi segmentada."}

    y0, x0 = pixels.min(axis=0)
    y1, x1 = pixels.max(axis=0)
    center_x = width // 2
    if anchors:
        left_x = int(anchors["leftTemple"]["x"] * width)
        right_x = int(anchors["rightTemple"]["x"] * width)
        center_x = int((anchors["leftTemple"]["x"] + anchors["rightTemple"]["x"]) * width / 2)
        forehead_y = int(anchors["forehead"]["y"] * height)
        face_width = max(1, abs(right_x - left_x))
        max_y = min(height, forehead_y + int(face_width * 0.28))
        radius = max(3, int(face_width * 0.055))
        central = _boundary(hair, center_x, radius, max_y)
        left = _boundary(hair, int(left_x + face_width * 0.28), radius, max_y)
        right = _boundary(hair, int(right_x - face_width * 0.28), radius, max_y)
    else:
        face_width = max(1, int((x1 - x0) * 0.65))
        central = left = right = None

    def recession(corner):
        return round(max(0.0, ((central or 0) - (corner or central or 0)) / face_width), 4)

    left_recession, right_recession = recession(left), recession(right)
    maximum = max(left_recession, right_recession)
    category = "acentuadas" if maximum >= 0.12 else "moderadas" if maximum >= 0.07 else "leves" if maximum >= 0.025 else "nenhuma"
    left_area = int(np.count_nonzero(hair[:, :center_x]))
    right_area = int(np.count_nonzero(hair[:, center_x:]))
    asymmetry = abs(left_area - right_area) / max(1, left_area + right_area)
    coverage = np.count_nonzero(hair) / hair.size
    box_width = (x1 - x0 + 1) / width
    usable = bool(coverage >= 0.012 and box_width >= 0.16 and min(left_area, right_area) > 0)
    allowed = cv2.dilate(hair, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15)), iterations=1)

    return {
        "detected": True,
        "model": "bisenet-resnet18-onnx",
        "provider": "CPUExecutionProvider",
        "usableForFilter": usable,
        "confidence": "high" if usable and anchors else "medium" if usable else "low",
        "hairMaskDataUrl": _data_url(hair),
        "allowedHairMaskDataUrl": _data_url(allowed),
        "metrics": {
            "visibleHairCoverage": round(coverage, 4),
            "visibleLeftRightAsymmetry": round(asymmetry, 4),
            "boundingBox": {"x": round(x0 / width, 4), "y": round(y0 / height, 4), "width": round((x1 - x0 + 1) / width, 4), "height": round((y1 - y0 + 1) / height, 4)},
        },
        "hairline": {
            "category": category,
            "leftRecession": left_recession,
            "rightRecession": right_recession,
            "apparentDifference": round(abs(left_recession - right_recession), 4),
            "confidence": "medium" if anchors else "low",
        },
        "limitations": "Cobertura e implantação aparentes na imagem; não mede folículos, densidade clínica ou estrutura óssea.",
        "warnings": [] if usable else ["Máscara insuficiente para limitar o filtro; refaça a foto frontal com o cabelo inteiro visível."],
    }
