from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
MODEL_DIR = BASE_DIR / "models"
MODEL_PATH = MODEL_DIR / "face_landmarker.task"
SEGMENTATION_MODEL_PATH = BASE_DIR / "models" / "hair_segmentation.onnx"
SECRET_DIR = BASE_DIR / ".secrets"
KEY_PATH = SECRET_DIR / "master.key"
ENCRYPTED_DIR = BASE_DIR / "storage" / "encrypted"
MAX_IMAGE_BYTES = 10 * 1024 * 1024
ALLOWED_MIME_TYPES = {"image/jpeg", "image/png", "image/webp"}

for directory in (MODEL_DIR, SECRET_DIR, ENCRYPTED_DIR):
    directory.mkdir(parents=True, exist_ok=True)
