#!/bin/bash
set -e

echo "Starting Backup Service..."
echo "Schedule: ${BACKUP_SCHEDULE:-daily}"
echo "Retention: ${BACKUP_RETENTION_DAYS:-7} days"

exec python3 /app/backup.py
