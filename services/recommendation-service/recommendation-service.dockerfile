FROM python:3.12-slim

# Set environment variables to avoid Python buffering and set OpenBLAS thread control
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    OPENBLAS_NUM_THREADS=1

WORKDIR /app

# System dependencies for implicit + psycopg2
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libopenblas-dev \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .


ENV RUNNING_IN_DOCKER true

# CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]

# CMD ["sh", "-c", "python -m scripts.init_db	&& uvicorn api.main:app --host 0.0.0.0 --port 8000"]
CMD ["sh", "-c", "python -m scripts.init_db && python -m scripts.train_model && python -m api.main"]
