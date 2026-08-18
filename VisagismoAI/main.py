import secrets
import time
import uuid
from pathlib import Path
from threading import Lock

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from fastapi.staticfiles import StaticFiles

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

CAPTURE_POSITIONS = [
    "Foto frontal", "45° direita", "Lateral direita", "Traseira",
    "Lateral esquerda", "45° esquerda", "Topo da cabeça",
]
SESSION_TTL_SECONDS = 30 * 60
MAX_CAPTURE_SESSIONS = 4
MAX_SESSION_PHOTO_BYTES = 3 * 1024 * 1024
capture_sessions: dict[str, dict] = {}
capture_sessions_lock = Lock()


def _purge_expired_sessions() -> None:
    now = time.time()
    expired = [key for key, value in capture_sessions.items() if value["expiresAt"] <= now]
    for key in expired:
        del capture_sessions[key]


def _capture_session(session_id: str) -> dict:
    with capture_sessions_lock:
        _purge_expired_sessions()
        session = capture_sessions.get(session_id)
        if not session:
            raise HTTPException(404, "Sessão inexistente ou expirada.")
        return session


def _session_status(session_id: str, session: dict) -> dict:
    positions = sorted(session["photos"].keys())
    return {
        "sessionId": session_id,
        "createdAt": session["createdAt"],
        "expiresAt": session["expiresAt"],
        "photoCount": len(positions),
        "expectedPhotoCount": len(CAPTURE_POSITIONS),
        "positions": [CAPTURE_POSITIONS[index] for index in positions],
        "complete": len(positions) == len(CAPTURE_POSITIONS),
        "storage": "temporary-memory-only",
    }


@app.get("/health")
def health() -> dict:
    return {
        "status": "ok",
        "version": app.version,
        "faceLandmarkerModel": MODEL_PATH.exists(),
        "hairSegmentationModel": SEGMENTATION_MODEL_PATH.exists(),
    }


@app.post("/api/v2/capture-sessions")
def create_capture_session() -> dict:
    with capture_sessions_lock:
        _purge_expired_sessions()
        if len(capture_sessions) >= MAX_CAPTURE_SESSIONS:
            raise HTTPException(503, "Limite temporário de sessões atingido. Tente novamente mais tarde.")
        session_id = secrets.token_urlsafe(18)
        now = time.time()
        capture_sessions[session_id] = {
            "createdAt": now,
            "expiresAt": now + SESSION_TTL_SECONDS,
            "photos": {},
        }
        return _session_status(session_id, capture_sessions[session_id])


@app.get("/api/v2/capture-sessions/{session_id}")
def get_capture_session(session_id: str) -> dict:
    return _session_status(session_id, _capture_session(session_id))


@app.post("/api/v2/capture-sessions/{session_id}/photos")
async def upload_capture_photo(
    session_id: str,
    photo: UploadFile = File(...),
    position_index: int = Form(...),
    consent: bool = Form(...),
) -> dict:
    if not consent:
        raise HTTPException(400, "O consentimento para a sessão é obrigatório.")
    if position_index < 0 or position_index >= len(CAPTURE_POSITIONS):
        raise HTTPException(400, "Posição de captura inválida.")
    if photo.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(415, "Formato não permitido. Use JPEG, PNG ou WebP.")
    data = await photo.read(MAX_IMAGE_BYTES + 1)
    if len(data) > MAX_IMAGE_BYTES:
        raise HTTPException(413, "A imagem excede o limite de 10 MB.")
    try:
        _image, sanitized = decode_and_sanitize(data)
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc
    if len(sanitized) > MAX_SESSION_PHOTO_BYTES:
        raise HTTPException(413, "A fotografia normalizada excede o limite da sessão móvel.")
    session = _capture_session(session_id)
    with capture_sessions_lock:
        session["photos"][position_index] = sanitized
    return _session_status(session_id, session)


@app.get("/api/v2/capture-sessions/{session_id}/photos/{position_index}")
def get_capture_photo(session_id: str, position_index: int) -> Response:
    session = _capture_session(session_id)
    photo = session["photos"].get(position_index)
    if photo is None:
        raise HTTPException(404, "Fotografia ainda não recebida.")
    return Response(photo, media_type="image/jpeg", headers={"Cache-Control": "no-store"})


@app.delete("/api/v2/capture-sessions/{session_id}")
def delete_capture_session(session_id: str) -> dict:
    with capture_sessions_lock:
        deleted = capture_sessions.pop(session_id, None) is not None
    return {"sessionId": session_id, "deleted": deleted}


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


# No ambiente publicado, frontend e API compartilham a mesma origem HTTPS.
# O mount fica por ultimo para nao interceptar /health e /api/v2/*.
WEB_DIR = Path(__file__).resolve().parent.parent / "VisagismoBarber"
if WEB_DIR.exists():
    app.mount("/", StaticFiles(directory=WEB_DIR, html=True), name="web")
