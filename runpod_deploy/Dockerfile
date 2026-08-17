FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    OMP_NUM_THREADS=2 \
    ORT_NUM_THREADS=2

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends libglib2.0-0 libgl1 \
    && rm -rf /var/lib/apt/lists/*

COPY runpod_deploy/requirements.txt /app/runpod_deploy/requirements.txt
RUN pip install --no-cache-dir -r /app/runpod_deploy/requirements.txt

COPY VisagismoAI /app/VisagismoAI
COPY runpod_deploy/handler.py /app/runpod_deploy/handler.py

CMD ["python", "-m", "runpod_deploy.handler"]
