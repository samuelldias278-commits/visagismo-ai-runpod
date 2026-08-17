FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    OMP_NUM_THREADS=1 \
    ORT_NUM_THREADS=1 \
    PORT=10000

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends libglib2.0-0 libgl1 \
    && rm -rf /var/lib/apt/lists/*

COPY render-requirements.txt /app/render-requirements.txt
RUN pip install --no-cache-dir -r /app/render-requirements.txt

COPY VisagismoAI /app/VisagismoAI
COPY VisagismoBarber /app/VisagismoBarber

CMD ["sh", "-c", "uvicorn VisagismoAI.main:app --host 0.0.0.0 --port ${PORT}"]
