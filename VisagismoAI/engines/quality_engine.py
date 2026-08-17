from dataclasses import asdict, dataclass

import cv2
import numpy as np


@dataclass(frozen=True)
class ImageQuality:
    width: int
    height: int
    brightness: float
    contrast: float
    sharpness: float
    acceptable: bool
    warnings: list[str]


def decode_and_sanitize(data: bytes) -> tuple[np.ndarray, bytes]:
    array = np.frombuffer(data, dtype=np.uint8)
    image = cv2.imdecode(array, cv2.IMREAD_COLOR)
    if image is None:
        raise ValueError("O arquivo não contém uma imagem decodificável.")

    height, width = image.shape[:2]
    if width < 256 or height < 256:
        raise ValueError("A imagem deve possuir pelo menos 256 × 256 pixels.")

    longest = max(width, height)
    if longest > 1600:
        scale = 1600 / longest
        image = cv2.resize(image, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA)

    ok, encoded = cv2.imencode(".jpg", image, [cv2.IMWRITE_JPEG_QUALITY, 88])
    if not ok:
        raise ValueError("Não foi possível normalizar a imagem.")
    return image, encoded.tobytes()


def assess_quality(image: np.ndarray) -> dict:
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    brightness = float(np.mean(gray))
    contrast = float(np.std(gray))
    sharpness = float(cv2.Laplacian(gray, cv2.CV_64F).var())
    warnings: list[str] = []
    if brightness < 45:
        warnings.append("imagem escura")
    elif brightness > 220:
        warnings.append("imagem muito clara")
    if contrast < 18:
        warnings.append("baixo contraste")
    if sharpness < 45:
        warnings.append("possível desfoque ou movimento")

    height, width = gray.shape
    quality = ImageQuality(
        width=width,
        height=height,
        brightness=round(brightness, 2),
        contrast=round(contrast, 2),
        sharpness=round(sharpness, 2),
        acceptable=not warnings,
        warnings=warnings,
    )
    return asdict(quality)
