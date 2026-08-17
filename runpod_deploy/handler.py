"""Worker Runpod Serverless para a análise geométrica e capilar do Visagismo."""

import base64
import binascii
import uuid

from VisagismoAI.engines.face_geometry import analyze_face
from VisagismoAI.engines.hair_segmentation import analyze_hair
from VisagismoAI.engines.quality_engine import assess_quality, decode_and_sanitize

MAX_RAW_IMAGE_BYTES = 7 * 1024 * 1024
ALLOWED_DATA_URL_PREFIXES = (
    "data:image/jpeg;base64,",
    "data:image/png;base64,",
    "data:image/webp;base64,",
)


def _decode_photo(value: str) -> bytes:
    if not isinstance(value, str) or not value.strip():
        raise ValueError("photoBase64 é obrigatório.")
    encoded = value.strip()
    for prefix in ALLOWED_DATA_URL_PREFIXES:
        if encoded.lower().startswith(prefix):
            encoded = encoded[len(prefix) :]
            break
    try:
        data = base64.b64decode(encoded, validate=True)
    except (ValueError, binascii.Error) as exc:
        raise ValueError("photoBase64 não contém uma imagem Base64 válida.") from exc
    if len(data) > MAX_RAW_IMAGE_BYTES:
        raise ValueError("A imagem excede o limite Serverless de 7 MB.")
    return data


def handler(event: dict) -> dict:
    payload = event.get("input") if isinstance(event, dict) else None
    if not isinstance(payload, dict):
        raise ValueError("O corpo deve conter um objeto input.")

    image, _sanitized = decode_and_sanitize(_decode_photo(payload.get("photoBase64")))
    quality = assess_quality(image)
    geometry = analyze_face(image)
    hair_analysis = analyze_hair(image, geometry)

    return {
        "analysisId": str(uuid.uuid4()),
        "consentId": str(payload.get("consentId") or "runpod-session"),
        "viewLabel": str(payload.get("viewLabel") or "Foto frontal"),
        "quality": quality,
        "faceGeometry": geometry,
        "hairAnalysis": hair_analysis,
        "storage": {"encrypted": False, "format": None},
        "execution": {
            "provider": "runpod-serverless",
            "compute": "CPU",
            "imagePersisted": False,
        },
    }


if __name__ == "__main__":
    import runpod

    runpod.serverless.start({"handler": handler})
