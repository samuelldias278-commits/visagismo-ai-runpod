import asyncio
import base64
import io
import os

import cv2
import numpy as np
from openai import OpenAI

from VisagismoAI.engines.face_geometry import analyze_face
from VisagismoAI.engines.hair_segmentation import analyze_hair
from VisagismoAI.engines.quality_engine import decode_and_sanitize


HAIRSTYLES = {
    "crew": "Crew Cut conservador, topo curto graduado e laterais naturalmente quadradas",
    "caesar": "Caesar conservador, franja curta texturizada adaptada à direção real dos fios",
    "low-taper": "Low Taper discreto, transição baixa somente nas têmporas e costeletas",
}


def is_configured() -> bool:
    return bool(os.getenv("OPENAI_API_KEY") and os.getenv("GENERATIVE_ACCESS_CODE"))


def _relative_change(before: float, after: float) -> float:
    return abs(after - before) / max(abs(before), 0.001)


def _validate_geometry(original: dict, generated: dict) -> dict:
    if not generated.get("detected"):
        raise ValueError("A geração foi rejeitada porque o rosto deixou de ser detectável.")
    original_measurements = original.get("measurements", {})
    generated_measurements = generated.get("measurements", {})
    checks = {
        "faceHeightWidthRatio": 0.08,
        "jawFaceRatio": 0.08,
    }
    drift = {
        key: round(_relative_change(float(original_measurements[key]), float(generated_measurements[key])), 4)
        for key in checks
        if key in original_measurements and key in generated_measurements
    }
    if any(drift[key] > checks[key] for key in drift):
        raise ValueError("A geração foi rejeitada porque alterou excessivamente a geometria facial.")
    return {"accepted": True, "measurementDrift": drift}


def _generate_sync(image_bytes: bytes, hairstyle_id: str, original_geometry: dict, hair: dict) -> dict:
    hairstyle = HAIRSTYLES[hairstyle_id]
    hairline = hair.get("hairline", {})
    metrics = hair.get("metrics", {})
    prompt = f"""
Edite esta fotografia frontal para uma simulação profissional e fotorealista de {hairstyle}.
Altere somente o cabelo. Preserve exatamente identidade, rosto, pele, barba, expressão, orelhas,
pescoço, roupa, iluminação, fundo, perspectiva, largura e altura cranianas, distância entre as
têmporas, testa, linha frontal e implantação biológica. Use a própria cor, textura e densidade
visível do cliente. Entradas observadas: {hairline.get('category', 'não determinadas')}.
Recuo esquerdo: {hairline.get('leftRecession', 'não determinado')}; recuo direito:
{hairline.get('rightRecession', 'não determinado')}; cobertura visível:
{metrics.get('visibleHairCoverage', 'não determinada')}. Não invente fios nem cubra entradas.
Mantenha o contorno lateral quadrado e natural, sem estreitar ou diminuir o crânio.
Não faça retoque de beleza, não altere a barba e não adicione texto ou marca d'água.
""".strip()
    image_file = io.BytesIO(image_bytes)
    image_file.name = "cliente-frontal.jpg"
    client = OpenAI(timeout=180.0, max_retries=1)
    result = client.images.edit(
        model="gpt-image-2",
        image=image_file,
        prompt=prompt,
        quality="medium",
        size="1024x1536",
    )
    if not result.data or not result.data[0].b64_json:
        raise RuntimeError("O provedor não retornou uma imagem.")
    generated_bytes = base64.b64decode(result.data[0].b64_json)
    generated_array = cv2.imdecode(np.frombuffer(generated_bytes, dtype=np.uint8), cv2.IMREAD_COLOR)
    if generated_array is None:
        raise RuntimeError("A imagem gerada não pôde ser validada.")
    generated_geometry = analyze_face(generated_array)
    validation = _validate_geometry(original_geometry, generated_geometry)
    return {
        "imageDataUrl": f"data:image/png;base64,{base64.b64encode(generated_bytes).decode('ascii')}",
        "model": "gpt-image-2",
        "hairstyleId": hairstyle_id,
        "validation": validation,
        "storage": {"stored": False},
    }


async def generate_hairstyle(image_bytes: bytes, hairstyle_id: str) -> dict:
    image, sanitized = decode_and_sanitize(image_bytes)
    geometry = analyze_face(image)
    if not geometry.get("detected"):
        raise ValueError("É necessário detectar claramente o rosto na fotografia frontal.")
    hair = analyze_hair(image, geometry)
    return await asyncio.to_thread(_generate_sync, sanitized, hairstyle_id, geometry, hair)
