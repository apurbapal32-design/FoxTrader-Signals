FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source trees and config files
COPY backend ./backend
COPY frontend ./frontend
COPY main.py .
COPY render.yaml* .
COPY Procfile* .
COPY README.md* .
# Copy APK optionally (wildcard prevents build failure if APK is excluded from git)
COPY FoxTrader-Pro-v1.0.0.apk* ./

ENV PORT=8088
ENV RENDER=true

EXPOSE 8088

CMD uvicorn main:app --host 0.0.0.0 --port ${PORT:-8088}
