import base64
import json
import sys
from pathlib import Path

from handler import handler


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("Uso: smoke_test.py CAMINHO_DA_FOTO")
    photo_path = Path(sys.argv[1])
    encoded = base64.b64encode(photo_path.read_bytes()).decode("ascii")
    result = handler(
        {
            "input": {
                "photoBase64": encoded,
                "consentId": "local-smoke-test",
                "viewLabel": "Foto frontal",
            }
        }
    )
    summary = {
        "faceDetected": result["faceGeometry"].get("detected"),
        "hairDetected": result["hairAnalysis"].get("detected"),
        "hairUsableForFilter": result["hairAnalysis"].get("usableForFilter"),
        "storage": result["storage"],
        "execution": result["execution"],
    }
    print(json.dumps(summary, ensure_ascii=False))


if __name__ == "__main__":
    main()
