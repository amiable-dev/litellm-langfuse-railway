# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Railway deployment templates for LiteLLM (LLM gateway) + Langfuse (observability platform). Two variants:
- **starter/** - 7 services, basic setup for development/POCs
- **production/** - 9 services, adds automated backups and health monitoring

## Repository Structure

```
├── starter/           # Starter template (7 services)
│   └── railway.toml   # Railway template definition
├── production/        # Production template (9 services)
│   ├── railway.toml   # Railway template with backup-service + health-monitor
│   ├── backup-service/    # Python service: PostgreSQL + ClickHouse backups to MinIO
│   ├── health-monitor/    # Python service: health checks + Slack/Discord/PagerDuty alerts
│   └── docs/              # RUNBOOK.md, UPGRADE.md, COMPARISON.md
└── shared/
    ├── litellm/config.yaml   # LiteLLM proxy config (Langfuse callbacks, Redis caching)
    ├── examples/             # Python integration examples
    └── scripts/              # test_setup.py, init-minio.sh
```

## Architecture

```
Apps (OpenAI SDK) → LiteLLM Gateway (port 4000) → 100+ LLM Providers
                           ↓
                    Langfuse Platform
                    ├── langfuse-web (port 3000) - UI/API
                    └── langfuse-worker (port 3030) - async processing
                           ↓
              PostgreSQL │ ClickHouse │ Redis │ MinIO
```

Production adds: `backup-service` (daily backups to MinIO) and `health-monitor` (60s checks + alerting)

## Services

| Service | Image | Purpose |
|---------|-------|---------|
| litellm | `ghcr.io/berriai/litellm-database:main-stable` | LLM gateway, virtual keys, cost tracking |
| langfuse-web | `langfuse/langfuse:3` | Observability UI, tracing |
| langfuse-worker | `langfuse/langfuse-worker:3` | Async trace processing |
| postgres | `ghcr.io/railwayapp-templates/postgres-ssl:16` | Transactional data |
| clickhouse | `clickhouse/clickhouse-server:24` | Analytics (traces, scores) |
| redis | `bitnami/redis:7.2` | Caching, queues (AOF enabled in prod) |
| minio | `minio/minio` | S3-compatible object storage |

## Key Configuration Files

- **railway.toml** - Defines all services, environment variables, and references between services
- **shared/litellm/config.yaml** - LiteLLM settings: Langfuse callbacks, Redis caching, retry policies

## Testing

```bash
# Run integration test (requires deployed services)
python shared/scripts/test_setup.py --litellm-url https://... --langfuse-url https://...
```

## Environment Variables

Critical variables that must be set after deployment:
- `LANGFUSE_PUBLIC_KEY` / `LANGFUSE_SECRET_KEY` - Get from Langfuse UI after first deploy
- LLM provider keys are added via LiteLLM UI or API, not environment variables

## Common Operations

```bash
# Manual backup trigger (production)
curl -X GET https://your-backup-service-url/backup

# Health check (production)
curl https://your-health-monitor-url/health

# Add model via LiteLLM API
curl -X POST 'https://your-litellm-url/model/new' \
  -H 'Authorization: Bearer $LITELLM_MASTER_KEY' \
  -H 'Content-Type: application/json' \
  -d '{"model_name": "gpt-4o", "litellm_params": {"model": "openai/gpt-4o", "api_key": "sk-..."}}'
```

## Security

- `LITELLM_SALT_KEY` is immutable after initial deployment - changing it breaks encrypted credentials
- `LITELLM_MASTER_KEY` must start with `sk-`
- All inter-service communication uses Railway's private network (`.railway.internal`)
