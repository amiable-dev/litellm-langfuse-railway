#!/usr/bin/env python3
"""
Production Backup Service for LiteLLM + Langfuse Stack
Handles PostgreSQL, ClickHouse, and configuration backups to MinIO/S3
"""

import os
import sys
import json
import subprocess
import logging
from datetime import datetime, timedelta
from pathlib import Path
from threading import Thread
from http.server import HTTPServer, BaseHTTPRequestHandler
import schedule
import time

# Optional imports
try:
    from minio import Minio
    from minio.error import S3Error
    MINIO_AVAILABLE = True
except ImportError:
    MINIO_AVAILABLE = False

try:
    import clickhouse_connect
    CLICKHOUSE_AVAILABLE = True
except ImportError:
    CLICKHOUSE_AVAILABLE = False

# Configuration from environment
CONFIG = {
    # PostgreSQL
    "postgres_url": os.getenv("DATABASE_URL", ""),
    
    # ClickHouse
    "clickhouse_host": os.getenv("CLICKHOUSE_HOST", "clickhouse"),
    "clickhouse_port": int(os.getenv("CLICKHOUSE_PORT", "8123")),
    "clickhouse_user": os.getenv("CLICKHOUSE_USER", "clickhouse"),
    "clickhouse_password": os.getenv("CLICKHOUSE_PASSWORD", ""),
    "clickhouse_db": os.getenv("CLICKHOUSE_DB", "default"),
    
    # MinIO/S3
    "minio_endpoint": os.getenv("MINIO_ENDPOINT", "minio:9000").replace("http://", "").replace("https://", ""),
    "minio_access_key": os.getenv("MINIO_ACCESS_KEY", os.getenv("MINIO_ROOT_USER", "minioadmin")),
    "minio_secret_key": os.getenv("MINIO_SECRET_KEY", os.getenv("MINIO_ROOT_PASSWORD", "")),
    "minio_secure": os.getenv("MINIO_SECURE", "false").lower() == "true",
    "backup_bucket": os.getenv("BACKUP_BUCKET", "backups"),
    
    # Backup settings
    "retention_days": int(os.getenv("BACKUP_RETENTION_DAYS", "7")),
    "backup_schedule": os.getenv("BACKUP_SCHEDULE", "daily"),  # hourly, daily, weekly
    "backup_hour": int(os.getenv("BACKUP_HOUR", "3")),  # Hour of day for daily backups (UTC)
    
    # Alerting
    "alert_webhook_url": os.getenv("ALERT_WEBHOOK_URL", ""),
    "alert_on_success": os.getenv("ALERT_ON_SUCCESS", "false").lower() == "true",
}

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global state for health checks
backup_state = {
    "last_backup": None,
    "last_status": "pending",
    "last_error": None,
    "postgres_backups": 0,
    "clickhouse_backups": 0,
    "total_size_bytes": 0,
}


def send_alert(message: str, level: str = "info"):
    """Send alert to webhook (Slack, Discord, etc.)"""
    webhook_url = CONFIG["alert_webhook_url"]
    if not webhook_url:
        return
    
    try:
        import requests
        
        # Detect webhook type and format accordingly
        if "discord" in webhook_url:
            payload = {"content": f"[{level.upper()}] {message}"}
        elif "slack" in webhook_url:
            emoji = "✅" if level == "success" else "❌" if level == "error" else "ℹ️"
            payload = {"text": f"{emoji} {message}"}
        else:
            # Generic webhook
            payload = {
                "level": level,
                "message": message,
                "timestamp": datetime.utcnow().isoformat(),
                "service": "backup-service"
            }
        
        requests.post(webhook_url, json=payload, timeout=10)
    except Exception as e:
        logger.error(f"Failed to send alert: {e}")


def get_minio_client():
    """Get MinIO client instance"""
    if not MINIO_AVAILABLE:
        raise RuntimeError("minio package not installed")
    
    return Minio(
        CONFIG["minio_endpoint"],
        access_key=CONFIG["minio_access_key"],
        secret_key=CONFIG["minio_secret_key"],
        secure=CONFIG["minio_secure"]
    )


def ensure_bucket_exists(client, bucket_name: str):
    """Ensure backup bucket exists"""
    try:
        if not client.bucket_exists(bucket_name):
            client.make_bucket(bucket_name)
            logger.info(f"Created bucket: {bucket_name}")
    except S3Error as e:
        logger.error(f"Failed to create bucket: {e}")
        raise


def backup_postgres():
    """Backup PostgreSQL database using pg_dump"""
    if not CONFIG["postgres_url"]:
        logger.warning("PostgreSQL URL not configured, skipping backup")
        return None
    
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    backup_file = f"/tmp/postgres_backup_{timestamp}.sql.gz"
    
    try:
        # Run pg_dump with compression
        cmd = f'pg_dump "{CONFIG["postgres_url"]}" | gzip > {backup_file}'
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        if result.returncode != 0:
            raise RuntimeError(f"pg_dump failed: {result.stderr}")
        
        file_size = os.path.getsize(backup_file)
        logger.info(f"PostgreSQL backup created: {backup_file} ({file_size} bytes)")
        
        return backup_file
    except Exception as e:
        logger.error(f"PostgreSQL backup failed: {e}")
        raise


def backup_clickhouse():
    """Backup ClickHouse database"""
    if not CLICKHOUSE_AVAILABLE:
        logger.warning("clickhouse-connect not installed, skipping ClickHouse backup")
        return None
    
    if not CONFIG["clickhouse_password"]:
        logger.warning("ClickHouse password not configured, skipping backup")
        return None
    
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    backup_dir = f"/tmp/clickhouse_backup_{timestamp}"
    backup_file = f"{backup_dir}.tar.gz"
    
    try:
        os.makedirs(backup_dir, exist_ok=True)
        
        # Connect to ClickHouse
        client = clickhouse_connect.get_client(
            host=CONFIG["clickhouse_host"],
            port=CONFIG["clickhouse_port"],
            username=CONFIG["clickhouse_user"],
            password=CONFIG["clickhouse_password"],
            database=CONFIG["clickhouse_db"]
        )
        
        # Get list of tables
        tables = client.query("SHOW TABLES").result_rows
        
        for (table_name,) in tables:
            # Export each table to TSV
            table_file = f"{backup_dir}/{table_name}.tsv"
            result = client.query(f"SELECT * FROM {table_name}")
            
            with open(table_file, 'w') as f:
                # Write header
                f.write('\t'.join(result.column_names) + '\n')
                # Write data
                for row in result.result_rows:
                    f.write('\t'.join(str(v) for v in row) + '\n')
            
            logger.info(f"Exported table: {table_name}")
        
        # Create tarball
        subprocess.run(
            f"tar -czf {backup_file} -C /tmp clickhouse_backup_{timestamp}",
            shell=True, check=True
        )
        
        # Cleanup temp dir
        subprocess.run(f"rm -rf {backup_dir}", shell=True)
        
        file_size = os.path.getsize(backup_file)
        logger.info(f"ClickHouse backup created: {backup_file} ({file_size} bytes)")
        
        return backup_file
    except Exception as e:
        logger.error(f"ClickHouse backup failed: {e}")
        raise


def upload_to_minio(local_file: str, prefix: str = ""):
    """Upload backup file to MinIO/S3"""
    if not MINIO_AVAILABLE:
        logger.warning("MinIO not available, backup saved locally only")
        return
    
    try:
        client = get_minio_client()
        bucket = CONFIG["backup_bucket"]
        ensure_bucket_exists(client, bucket)
        
        filename = os.path.basename(local_file)
        object_name = f"{prefix}/{filename}" if prefix else filename
        
        client.fput_object(bucket, object_name, local_file)
        logger.info(f"Uploaded to MinIO: {bucket}/{object_name}")
        
        # Update stats
        backup_state["total_size_bytes"] += os.path.getsize(local_file)
        
        # Cleanup local file
        os.remove(local_file)
        
    except Exception as e:
        logger.error(f"Upload to MinIO failed: {e}")
        raise


def cleanup_old_backups():
    """Remove backups older than retention period"""
    if not MINIO_AVAILABLE:
        return
    
    try:
        client = get_minio_client()
        bucket = CONFIG["backup_bucket"]
        
        if not client.bucket_exists(bucket):
            return
        
        cutoff_date = datetime.utcnow() - timedelta(days=CONFIG["retention_days"])
        deleted_count = 0
        
        objects = client.list_objects(bucket, recursive=True)
        for obj in objects:
            if obj.last_modified.replace(tzinfo=None) < cutoff_date:
                client.remove_object(bucket, obj.object_name)
                logger.info(f"Deleted old backup: {obj.object_name}")
                deleted_count += 1
        
        if deleted_count > 0:
            logger.info(f"Cleaned up {deleted_count} old backups")
            
    except Exception as e:
        logger.error(f"Cleanup failed: {e}")


def run_backup():
    """Execute full backup routine"""
    logger.info("Starting backup routine...")
    backup_state["last_backup"] = datetime.utcnow().isoformat()
    
    errors = []
    
    # PostgreSQL backup
    try:
        pg_backup = backup_postgres()
        if pg_backup:
            upload_to_minio(pg_backup, "postgres")
            backup_state["postgres_backups"] += 1
    except Exception as e:
        errors.append(f"PostgreSQL: {e}")
    
    # ClickHouse backup
    try:
        ch_backup = backup_clickhouse()
        if ch_backup:
            upload_to_minio(ch_backup, "clickhouse")
            backup_state["clickhouse_backups"] += 1
    except Exception as e:
        errors.append(f"ClickHouse: {e}")
    
    # Cleanup old backups
    try:
        cleanup_old_backups()
    except Exception as e:
        errors.append(f"Cleanup: {e}")
    
    # Update state and send alerts
    if errors:
        backup_state["last_status"] = "error"
        backup_state["last_error"] = "; ".join(errors)
        send_alert(f"Backup completed with errors: {backup_state['last_error']}", "error")
    else:
        backup_state["last_status"] = "success"
        backup_state["last_error"] = None
        if CONFIG["alert_on_success"]:
            send_alert("Backup completed successfully", "success")
    
    logger.info(f"Backup routine completed. Status: {backup_state['last_status']}")


class HealthHandler(BaseHTTPRequestHandler):
    """HTTP handler for health checks"""
    
    def do_GET(self):
        if self.path == "/health":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            
            response = {
                "status": "healthy",
                "service": "backup-service",
                "backup_state": backup_state
            }
            self.wfile.write(json.dumps(response).encode())
            
        elif self.path == "/backup":
            # Trigger manual backup
            Thread(target=run_backup).start()
            self.send_response(202)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "backup_started"}).encode())
            
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        # Suppress access logs
        pass


def run_health_server():
    """Run health check HTTP server"""
    port = int(os.getenv("PORT", "8080"))
    server = HTTPServer(("0.0.0.0", port), HealthHandler)
    logger.info(f"Health server running on port {port}")
    server.serve_forever()


def setup_schedule():
    """Setup backup schedule based on configuration"""
    schedule_type = CONFIG["backup_schedule"]
    
    if schedule_type == "hourly":
        schedule.every().hour.do(run_backup)
        logger.info("Scheduled hourly backups")
    elif schedule_type == "weekly":
        schedule.every().sunday.at(f"{CONFIG['backup_hour']:02d}:00").do(run_backup)
        logger.info(f"Scheduled weekly backups on Sunday at {CONFIG['backup_hour']:02d}:00 UTC")
    else:  # daily (default)
        schedule.every().day.at(f"{CONFIG['backup_hour']:02d}:00").do(run_backup)
        logger.info(f"Scheduled daily backups at {CONFIG['backup_hour']:02d}:00 UTC")


def main():
    """Main entry point"""
    logger.info("Backup service starting...")
    logger.info(f"Configuration: schedule={CONFIG['backup_schedule']}, retention={CONFIG['retention_days']} days")
    
    # Start health server in background
    Thread(target=run_health_server, daemon=True).start()
    
    # Setup schedule
    setup_schedule()
    
    # Run initial backup on startup if configured
    if os.getenv("BACKUP_ON_STARTUP", "false").lower() == "true":
        logger.info("Running initial backup on startup...")
        run_backup()
    
    # Run scheduler
    while True:
        schedule.run_pending()
        time.sleep(60)


if __name__ == "__main__":
    main()
