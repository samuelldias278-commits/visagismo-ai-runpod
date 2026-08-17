import os
import secrets
import uuid
from pathlib import Path

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from VisagismoAI.config import ENCRYPTED_DIR, KEY_PATH


def _load_or_create_key() -> bytes:
    """Carrega a chave local ou cria uma chave AES-256 para este computador."""
    if KEY_PATH.exists():
        key = KEY_PATH.read_bytes()
        if len(key) != 32:
            raise RuntimeError("A chave local de criptografia é inválida.")
        return key

    key = AESGCM.generate_key(bit_length=256)
    KEY_PATH.write_bytes(key)
    try:
        os.chmod(KEY_PATH, 0o600)
    except OSError:
        pass
    return key


def encrypt_and_store(image_bytes: bytes, analysis_id: uuid.UUID) -> Path:
    """Criptografa bytes sanitizados usando AES-256-GCM e um nonce único."""
    key = _load_or_create_key()
    nonce = secrets.token_bytes(12)
    aad = str(analysis_id).encode("utf-8")
    encrypted = AESGCM(key).encrypt(nonce, image_bytes, aad)
    destination = ENCRYPTED_DIR / f"{analysis_id}.vimg"
    destination.write_bytes(nonce + encrypted)
    return destination


def delete_encrypted_image(analysis_id: uuid.UUID) -> bool:
    destination = ENCRYPTED_DIR / f"{analysis_id}.vimg"
    if not destination.exists():
        return False
    destination.unlink()
    return True
