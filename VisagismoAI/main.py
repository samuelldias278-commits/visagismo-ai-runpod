import uuid

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from VisagismoAI.config import ALLOWED_MIME_TYPES, MAX_IMAGE_BYTES, MODEL_PATH, SEGMENTATION_MODEL_PATH
from VisagismoAI.engines.face_geometry import analyze_face
from VisagismoAI.engines.hair_segmentation import analyze_hair
from VisagismoAI.engines.quality_engine import assess_quality, decode_and_sanitize
from VisagismoAI.security.encryption import delete_encrypted_image, encrypt_and_store

app = FastAPI(title="Visagismo AI", version="2.0.0-dev")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000", "http://127.0.0.1:8000"],
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["Content-Type"],
)


@app.get("/health")
def health() -> dict:
    return {
        "status": "ok",
        "version": app.version,
        "faceLandmarkerModel": MODEL_PATH.exists(),
        "hairSegmentationModel": SEGMENTATION_MODEL_PATH.exists(),
    }


@app.post("/api/v2/analyze/front")
async def analyze_front_photo(
    photo: UploadFile = File(...),
    consent_id: str = Form(...),
    store_history: bool = Form(False),
    view_label: str = Form("Foto frontal"),
) -> dict:
    if photo.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(415, "Formato não permitido. Use JPEG, PNG ou WebP.")
    data = await photo.read(MAX_IMAGE_BYTES + 1)
    if len(data) > MAX_IMAGE_BYTES:
        raise HTTPException(413, "A imagem excede o limite de 10 MB.")
    if not consent_id.strip():
        raise HTTPException(400, "O identificador de consentimento é obrigatório.")

    try:
        image, sanitized = decode_and_sanitize(data)
        quality = assess_quality(image)
        geometry = analyze_face(image)
        hair_analysis = analyze_hair(image, geometry)
    except FileNotFoundError as exc:
        raise HTTPException(503, str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc

    analysis_id = uuid.uuid4()
    stored = False
    if store_history:
        encrypt_and_store(sanitized, analysis_id)
        stored = True

    return {
        "analysisId": str(analysis_id),
        "consentId": consent_id,
        "viewLabel": view_label,
        "quality": quality,
        "faceGeometry": geometry,
        "hairAnalysis": hair_analysis,
        "storage": {"encrypted": stored, "format": "AES-256-GCM" if stored else None},
    }


@app.delete("/api/v2/analyses/{analysis_id}")
def delete_analysis(analysis_id: uuid.UUID) -> dict:
    return {"analysisId": str(analysis_id), "deleted": delete_encrypted_image(analysis_id)}
