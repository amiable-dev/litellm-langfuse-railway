FROM python:3.12-slim

# Install dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    postgresql-client \
    curl \
    cron \
    && rm -rf /var/lib/apt/lists/*

# Install Python packages
RUN pip install --no-cache-dir \
    minio \
    clickhouse-connect \
    schedule \
    requests

WORKDIR /app

COPY backup.py .
COPY entrypoint.sh .
RUN chmod +x entrypoint.sh

# Health check endpoint
EXPOSE 8080

ENTRYPOINT ["./entrypoint.sh"]
