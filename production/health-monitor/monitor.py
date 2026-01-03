#!/usr/bin/env python3
"""
Production Health Monitor for LiteLLM + Langfuse Stack
Monitors all services and sends alerts on failures
"""

import os
import sys
import json
import time
import logging
from datetime import datetime, timedelta
from threading import Thread
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import Dict, Optional
from dataclasses import dataclass, asdict
from enum import Enum

import requests
import schedule

# Optional imports with fallbacks
try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

try:
    import psycopg2
    POSTGRES_AVAILABLE = True
except ImportError:
    POSTGRES_AVAILABLE = False


# Configuration
CONFIG = {
    # Service endpoints (internal Railway network)
    "litellm_url": os.getenv("LITELLM_URL", "http://litellm.railway.internal:4000"),
    "langfuse_url": os.getenv("LANGFUSE_URL", "http://langfuse-web.railway.internal:3000"),
    "langfuse_worker_url": os.getenv("LANGFUSE_WORKER_URL", "http://langfuse-worker.railway.internal:3030"),
    
    # Database connections
    "postgres_url": os.getenv("DATABASE_URL", ""),
    "redis_host": os.getenv("REDIS_HOST", "redis.railway.internal"),
    "redis_port": int(os.getenv("REDIS_PORT", "6379")),
    "redis_password": os.getenv("REDIS_PASSWORD", ""),
    
    # ClickHouse
    "clickhouse_url": os.getenv("CLICKHOUSE_URL", "http://clickhouse.railway.internal:8123"),
    "clickhouse_user": os.getenv("CLICKHOUSE_USER", "clickhouse"),
    "clickhouse_password": os.getenv("CLICKHOUSE_PASSWORD", ""),
    
    # Monitoring settings
    "check_interval_seconds": int(os.getenv("CHECK_INTERVAL", "60")),
    "alert_cooldown_minutes": int(os.getenv("ALERT_COOLDOWN", "15")),
    "consecutive_failures_threshold": int(os.getenv("FAILURE_THRESHOLD", "3")),
    
    # Alerting
    "alert_webhook_url": os.getenv("ALERT_WEBHOOK_URL", ""),
    "pagerduty_routing_key": os.getenv("PAGERDUTY_ROUTING_KEY", ""),
}


# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ServiceStatus(Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


@dataclass
class ServiceHealth:
    name: str
    status: ServiceStatus
    response_time_ms: Optional[float] = None
    last_check: Optional[str] = None
    error: Optional[str] = None
    consecutive_failures: int = 0
    last_alert_time: Optional[str] = None


# Global health state
health_state: Dict[str, ServiceHealth] = {}


def send_alert(service: str, status: ServiceStatus, error: Optional[str] = None):
    """Send alert via webhook or PagerDuty"""
    
    # Check cooldown
    if service in health_state:
        last_alert = health_state[service].last_alert_time
        if last_alert:
            cooldown = timedelta(minutes=CONFIG["alert_cooldown_minutes"])
            if datetime.utcnow() - datetime.fromisoformat(last_alert) < cooldown:
                logger.debug(f"Skipping alert for {service} (cooldown)")
                return
    
    message = f"🚨 Service Alert: {service} is {status.value}"
    if error:
        message += f"\nError: {error}"
    
    # Slack/Discord webhook
    webhook_url = CONFIG["alert_webhook_url"]
    if webhook_url:
        try:
            if "discord" in webhook_url:
                payload = {
                    "embeds": [{
                        "title": f"Service Alert: {service}",
                        "description": error or f"Status changed to {status.value}",
                        "color": 15158332 if status == ServiceStatus.UNHEALTHY else 16776960,
                        "timestamp": datetime.utcnow().isoformat()
                    }]
                }
            else:
                # Slack format
                color = "danger" if status == ServiceStatus.UNHEALTHY else "warning"
                payload = {
                    "attachments": [{
                        "color": color,
                        "title": f"Service Alert: {service}",
                        "text": error or f"Status: {status.value}",
                        "ts": int(time.time())
                    }]
                }
            
            requests.post(webhook_url, json=payload, timeout=10)
            logger.info(f"Sent webhook alert for {service}")
        except Exception as e:
            logger.error(f"Failed to send webhook alert: {e}")
    
    # PagerDuty
    pd_key = CONFIG["pagerduty_routing_key"]
    if pd_key and status == ServiceStatus.UNHEALTHY:
        try:
            payload = {
                "routing_key": pd_key,
                "event_action": "trigger",
                "dedup_key": f"litellm-langfuse-{service}",
                "payload": {
                    "summary": f"{service} is unhealthy: {error or 'Unknown error'}",
                    "severity": "critical",
                    "source": "litellm-langfuse-monitor",
                    "component": service,
                }
            }
            requests.post(
                "https://events.pagerduty.com/v2/enqueue",
                json=payload,
                timeout=10
            )
            logger.info(f"Sent PagerDuty alert for {service}")
        except Exception as e:
            logger.error(f"Failed to send PagerDuty alert: {e}")
    
    # Update last alert time
    if service in health_state:
        health_state[service].last_alert_time = datetime.utcnow().isoformat()


def check_http_endpoint(name: str, url: str, path: str = "/health") -> ServiceHealth:
    """Check HTTP endpoint health"""
    full_url = f"{url}{path}"
    start_time = time.time()
    
    try:
        response = requests.get(full_url, timeout=10)
        response_time = (time.time() - start_time) * 1000
        
        if response.status_code == 200:
            status = ServiceStatus.HEALTHY
            error = None
        elif response.status_code < 500:
            status = ServiceStatus.DEGRADED
            error = f"Status code: {response.status_code}"
        else:
            status = ServiceStatus.UNHEALTHY
            error = f"Status code: {response.status_code}"
        
        return ServiceHealth(
            name=name,
            status=status,
            response_time_ms=round(response_time, 2),
            last_check=datetime.utcnow().isoformat(),
            error=error
        )
    except requests.exceptions.Timeout:
        return ServiceHealth(
            name=name,
            status=ServiceStatus.UNHEALTHY,
            last_check=datetime.utcnow().isoformat(),
            error="Request timeout"
        )
    except requests.exceptions.ConnectionError as e:
        return ServiceHealth(
            name=name,
            status=ServiceStatus.UNHEALTHY,
            last_check=datetime.utcnow().isoformat(),
            error=f"Connection error: {str(e)[:100]}"
        )
    except Exception as e:
        return ServiceHealth(
            name=name,
            status=ServiceStatus.UNKNOWN,
            last_check=datetime.utcnow().isoformat(),
            error=str(e)[:200]
        )


def check_postgres() -> ServiceHealth:
    """Check PostgreSQL connectivity"""
    if not POSTGRES_AVAILABLE or not CONFIG["postgres_url"]:
        return ServiceHealth(
            name="postgres",
            status=ServiceStatus.UNKNOWN,
            last_check=datetime.utcnow().isoformat(),
            error="PostgreSQL check not configured"
        )
    
    start_time = time.time()
    try:
        conn = psycopg2.connect(CONFIG["postgres_url"], connect_timeout=10)
        cur = conn.cursor()
        cur.execute("SELECT 1")
        cur.close()
        conn.close()
        
        response_time = (time.time() - start_time) * 1000
        return ServiceHealth(
            name="postgres",
            status=ServiceStatus.HEALTHY,
            response_time_ms=round(response_time, 2),
            last_check=datetime.utcnow().isoformat()
        )
    except Exception as e:
        return ServiceHealth(
            name="postgres",
            status=ServiceStatus.UNHEALTHY,
            last_check=datetime.utcnow().isoformat(),
            error=str(e)[:200]
        )


def check_redis() -> ServiceHealth:
    """Check Redis connectivity"""
    if not REDIS_AVAILABLE:
        return ServiceHealth(
            name="redis",
            status=ServiceStatus.UNKNOWN,
            last_check=datetime.utcnow().isoformat(),
            error="Redis check not configured"
        )
    
    start_time = time.time()
    try:
        r = redis.Redis(
            host=CONFIG["redis_host"],
            port=CONFIG["redis_port"],
            password=CONFIG["redis_password"] or None,
            socket_timeout=10
        )
        r.ping()
        
        response_time = (time.time() - start_time) * 1000
        return ServiceHealth(
            name="redis",
            status=ServiceStatus.HEALTHY,
            response_time_ms=round(response_time, 2),
            last_check=datetime.utcnow().isoformat()
        )
    except Exception as e:
        return ServiceHealth(
            name="redis",
            status=ServiceStatus.UNHEALTHY,
            last_check=datetime.utcnow().isoformat(),
            error=str(e)[:200]
        )


def check_clickhouse() -> ServiceHealth:
    """Check ClickHouse connectivity"""
    url = CONFIG["clickhouse_url"]
    if not url:
        return ServiceHealth(
            name="clickhouse",
            status=ServiceStatus.UNKNOWN,
            last_check=datetime.utcnow().isoformat(),
            error="ClickHouse check not configured"
        )
    
    start_time = time.time()
    try:
        response = requests.get(
            f"{url}/ping",
            timeout=10
        )
        response_time = (time.time() - start_time) * 1000
        
        if response.status_code == 200:
            return ServiceHealth(
                name="clickhouse",
                status=ServiceStatus.HEALTHY,
                response_time_ms=round(response_time, 2),
                last_check=datetime.utcnow().isoformat()
            )
        else:
            return ServiceHealth(
                name="clickhouse",
                status=ServiceStatus.UNHEALTHY,
                last_check=datetime.utcnow().isoformat(),
                error=f"Status code: {response.status_code}"
            )
    except Exception as e:
        return ServiceHealth(
            name="clickhouse",
            status=ServiceStatus.UNHEALTHY,
            last_check=datetime.utcnow().isoformat(),
            error=str(e)[:200]
        )


def run_health_checks():
    """Run all health checks"""
    global health_state
    
    checks = [
        ("litellm", lambda: check_http_endpoint("litellm", CONFIG["litellm_url"], "/health")),
        ("langfuse-web", lambda: check_http_endpoint("langfuse-web", CONFIG["langfuse_url"], "/api/public/health")),
        ("langfuse-worker", lambda: check_http_endpoint("langfuse-worker", CONFIG["langfuse_worker_url"], "/api/health")),
        ("postgres", check_postgres),
        ("redis", check_redis),
        ("clickhouse", check_clickhouse),
    ]
    
    for name, check_func in checks:
        try:
            result = check_func()
            
            # Track consecutive failures
            previous = health_state.get(name)
            if previous:
                if result.status == ServiceStatus.UNHEALTHY:
                    result.consecutive_failures = previous.consecutive_failures + 1
                else:
                    result.consecutive_failures = 0
                result.last_alert_time = previous.last_alert_time
            
            # Send alert if threshold reached
            if result.consecutive_failures >= CONFIG["consecutive_failures_threshold"]:
                if previous and previous.status != ServiceStatus.UNHEALTHY:
                    send_alert(name, result.status, result.error)
            
            # Send recovery alert
            if previous and previous.status == ServiceStatus.UNHEALTHY and result.status == ServiceStatus.HEALTHY:
                if CONFIG["alert_webhook_url"]:
                    try:
                        message = f"✅ Service Recovered: {name} is now healthy"
                        requests.post(CONFIG["alert_webhook_url"], json={"text": message}, timeout=10)
                    except:
                        pass
            
            health_state[name] = result
            logger.debug(f"Health check {name}: {result.status.value}")
            
        except Exception as e:
            logger.error(f"Health check failed for {name}: {e}")
            health_state[name] = ServiceHealth(
                name=name,
                status=ServiceStatus.UNKNOWN,
                last_check=datetime.utcnow().isoformat(),
                error=str(e)[:200]
            )
    
    # Log summary
    healthy = sum(1 for h in health_state.values() if h.status == ServiceStatus.HEALTHY)
    total = len(health_state)
    logger.info(f"Health check complete: {healthy}/{total} services healthy")


def get_overall_status() -> ServiceStatus:
    """Calculate overall system status"""
    if not health_state:
        return ServiceStatus.UNKNOWN
    
    statuses = [h.status for h in health_state.values()]
    
    if all(s == ServiceStatus.HEALTHY for s in statuses):
        return ServiceStatus.HEALTHY
    elif any(s == ServiceStatus.UNHEALTHY for s in statuses):
        return ServiceStatus.UNHEALTHY
    elif any(s == ServiceStatus.DEGRADED for s in statuses):
        return ServiceStatus.DEGRADED
    else:
        return ServiceStatus.UNKNOWN


class HealthHandler(BaseHTTPRequestHandler):
    """HTTP handler for health check API"""
    
    def do_GET(self):
        if self.path == "/health" or self.path == "/":
            overall = get_overall_status()
            status_code = 200 if overall == ServiceStatus.HEALTHY else 503
            
            self.send_response(status_code)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            
            response = {
                "status": overall.value,
                "timestamp": datetime.utcnow().isoformat(),
                "services": {
                    name: {
                        "status": h.status.value,
                        "response_time_ms": h.response_time_ms,
                        "last_check": h.last_check,
                        "error": h.error,
                        "consecutive_failures": h.consecutive_failures
                    }
                    for name, h in health_state.items()
                }
            }
            self.wfile.write(json.dumps(response, indent=2).encode())
            
        elif self.path == "/metrics":
            # Prometheus-compatible metrics
            self.send_response(200)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            
            lines = []
            lines.append("# HELP service_health Service health status (1=healthy, 0=unhealthy)")
            lines.append("# TYPE service_health gauge")
            for name, h in health_state.items():
                value = 1 if h.status == ServiceStatus.HEALTHY else 0
                lines.append(f'service_health{{service="{name}"}} {value}')
            
            lines.append("# HELP service_response_time_ms Service response time in milliseconds")
            lines.append("# TYPE service_response_time_ms gauge")
            for name, h in health_state.items():
                if h.response_time_ms is not None:
                    lines.append(f'service_response_time_ms{{service="{name}"}} {h.response_time_ms}')
            
            self.wfile.write("\n".join(lines).encode())
            
        elif self.path == "/check":
            # Trigger immediate health check
            Thread(target=run_health_checks).start()
            self.send_response(202)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "check_triggered"}).encode())
            
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        pass


def run_http_server():
    """Run HTTP server for health API"""
    port = int(os.getenv("PORT", "8080"))
    server = HTTPServer(("0.0.0.0", port), HealthHandler)
    logger.info(f"Health monitor API running on port {port}")
    server.serve_forever()


def main():
    """Main entry point"""
    logger.info("Health monitor starting...")
    logger.info(f"Check interval: {CONFIG['check_interval_seconds']}s")
    logger.info(f"Alert cooldown: {CONFIG['alert_cooldown_minutes']}m")
    logger.info(f"Failure threshold: {CONFIG['consecutive_failures_threshold']}")
    
    # Start HTTP server in background
    Thread(target=run_http_server, daemon=True).start()
    
    # Run initial check
    run_health_checks()
    
    # Schedule periodic checks
    schedule.every(CONFIG["check_interval_seconds"]).seconds.do(run_health_checks)
    
    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    main()
