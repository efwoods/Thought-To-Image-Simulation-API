FROM python:3.11-slim

WORKDIR /app

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    git ffmpeg libsndfile1-dev build-essential \
    libsndfile1 \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY app/ .
COPY app/data/*.pkl ./data/

RUN if [ -d /app/data ]; then \
      echo "/app/data directory exists."; \
      echo "Listing .pkl files in /app/data:"; \
      ls -l /app/data/*.pkl; \
    else \
      echo "ERROR: /app/data directory does NOT exist!"; \
    fi

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
