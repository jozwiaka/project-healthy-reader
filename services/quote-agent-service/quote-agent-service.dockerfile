FROM python:3.12-slim

# Set environment variables to avoid Python buffering and set OpenBLAS thread control
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    OPENBLAS_NUM_THREADS=1 \
    RUNNING_IN_DOCKER=true

WORKDIR /app/services/quote-agent-service

# System dependencies for implicit + psycopg2
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libopenblas-dev \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY ./services/quote-agent-service/requirements.txt /app/services/quote-agent-service/requirements.txt
COPY ./common/python_common/requirements.txt /app/common/python_common/requirements.txt

RUN pip install --no-cache-dir -r /app/common/python_common/requirements.txt \
    && pip install --no-cache-dir -r /app/services/quote-agent-service/requirements.txt

COPY ./services/quote-agent-service /app/services/quote-agent-service
COPY ./common/python_common /app/common/python_common

# CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

# CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port 8000"]
CMD ["sh", "-c", "python -m run"]
