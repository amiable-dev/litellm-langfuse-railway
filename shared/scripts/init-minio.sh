#!/bin/bash
# MinIO bucket initialization script
# This runs once to create the required buckets for Langfuse

set -e

echo "Waiting for MinIO to be ready..."
until curl -sf http://minio:9000/minio/health/live > /dev/null 2>&1; do
    echo "MinIO not ready, waiting..."
    sleep 2
done

echo "MinIO is ready. Creating buckets..."

# Install mc (MinIO Client) if not present
if ! command -v mc &> /dev/null; then
    curl -O https://dl.min.io/client/mc/release/linux-amd64/mc
    chmod +x mc
    mv mc /usr/local/bin/
fi

# Configure mc
mc alias set myminio http://minio:9000 ${MINIO_ROOT_USER:-minioadmin} ${MINIO_ROOT_PASSWORD:-minioadmin}

# Create langfuse bucket if it doesn't exist
if ! mc ls myminio/langfuse > /dev/null 2>&1; then
    mc mb myminio/langfuse
    echo "Created bucket: langfuse"
else
    echo "Bucket 'langfuse' already exists"
fi

# Set bucket policy to allow read/write
mc anonymous set download myminio/langfuse

echo "MinIO initialization complete!"
