# LiteLLM + Langfuse Railway Templates

Production-ready LLM gateway with full observability on Railway.

[![Deploy Starter](https://railway.app/button.svg)](https://railway.app/template/STARTER_ID)
[![Deploy Production](https://railway.app/button.svg)](https://railway.app/template/PRODUCTION_ID)

## What Is This?

A unified API gateway for 100+ LLM providers (OpenAI, Anthropic, Gemini, Bedrock, etc.) with complete observability, cost tracking, and prompt management via Langfuse.

```
Your App (OpenAI SDK) → LiteLLM Gateway → 100+ LLM Providers
                              ↓
                      Langfuse Observability
                    (traces, costs, prompts)
```

## Choose Your Template

| | **Starter** | **Production** |
|---|-------------|----------------|
| **Best For** | Development, POCs, side projects | Customer-facing APIs, enterprise |
| **Services** | 7 | 9 |
| **Automated Backups** | ❌ | ✅ Daily to MinIO |
| **Health Monitoring** | ❌ | ✅ All services |
| **Alerting** | ❌ | ✅ Slack/Discord/PagerDuty |
| **Redis Persistence** | Basic | ✅ AOF enabled |
| **Operations Runbook** | ❌ | ✅ Included |
| **Est. Cost** | $29-68/mo | $33-78/mo |
| **Deploy** | [Deploy Starter →](https://railway.app/template/STARTER_ID) | [Deploy Production →](https://railway.app/template/PRODUCTION_ID) |

### Quick Decision

- **"I'm evaluating/prototyping"** → Starter
- **"Users will pay for this"** → Production
- **"I need uptime guarantees"** → Production

## Features

### Core (Both Templates)

- ✅ **Unified LLM API** - OpenAI-compatible endpoint for 100+ providers
- ✅ **Virtual Keys** - Per-user/team API keys with budgets and rate limits
- ✅ **Cost Tracking** - Real-time spend per key, model, and team
- ✅ **Load Balancing** - Distribute requests across providers
- ✅ **Fallbacks** - Automatic failover when providers error
- ✅ **Full Tracing** - Every request traced in Langfuse
- ✅ **Prompt Management** - Version and manage prompts centrally
- ✅ **Evaluations** - Score and evaluate LLM outputs

### Production Additions

- ✅ **Automated Backups** - PostgreSQL + ClickHouse daily backups
- ✅ **Health Monitoring** - 60-second checks on all services
- ✅ **Alert Integration** - Slack, Discord, PagerDuty webhooks
- ✅ **Prometheus Metrics** - `/metrics` endpoint for observability
- ✅ **Operations Runbook** - Documented restore and upgrade procedures

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Your Applications                       │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                     LiteLLM Gateway                          │
│         Unified API • Rate Limits • Cost Tracking            │
└─────────────────────────────────────────────────────────────┘
         │              │              │              │
         ▼              ▼              ▼              ▼
    ┌────────┐    ┌──────────┐   ┌────────┐    ┌─────────┐
    │ OpenAI │    │ Anthropic │   │ Gemini │    │  100+   │
    └────────┘    └──────────┘   └────────┘    └─────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────┐
│                   Langfuse Platform                          │
│        Tracing • Prompts • Evaluations • Analytics           │
└─────────────────────────────────────────────────────────────┘
         │              │              │
         ▼              ▼              ▼
   ┌──────────┐  ┌────────────┐  ┌─────────┐
   │ Postgres │  │ ClickHouse │  │  Redis  │
   └──────────┘  └────────────┘  └─────────┘
```

## Quick Start

### 1. Deploy

Click the deploy button for your chosen template above.

### 2. Get Langfuse Keys

1. Open Langfuse UI (public URL from Railway)
2. Create account
3. Settings → API Keys → Create
4. Copy Public Key and Secret Key

### 3. Configure LiteLLM

Update LiteLLM service variables in Railway:
- `LANGFUSE_PUBLIC_KEY` = your public key
- `LANGFUSE_SECRET_KEY` = your secret key

### 4. Add LLM Providers

Via LiteLLM UI or API:

```python
import requests

requests.post(
    "https://your-litellm-url/model/new",
    headers={"Authorization": "Bearer YOUR_MASTER_KEY"},
    json={
        "model_name": "gpt-4o",
        "litellm_params": {
            "model": "gpt-4o",
            "api_key": "sk-..."
        }
    }
)
```

### 5. Use It

```python
from openai import OpenAI

client = OpenAI(
    api_key="your-litellm-key",
    base_url="https://your-litellm-url"
)

response = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "Hello!"}]
)
```

## Documentation

| Document | Description |
|----------|-------------|
| [Starter README](./starter/README.md) | Starter template setup |
| [Production README](./production/README.md) | Production template setup |
| [Operations Runbook](./production/docs/RUNBOOK.md) | Backup, restore, incident response |
| [Upgrade Guide](./production/docs/UPGRADE.md) | HA PostgreSQL migration |
| [Template Comparison](./production/docs/COMPARISON.md) | Detailed feature comparison |

## Repository Structure

```
├── starter/                 # Starter template (7 services)
│   ├── railway.toml
│   ├── README.md
│   └── SETUP.md
├── production/              # Production template (9 services)
│   ├── railway.toml
│   ├── README.md
│   ├── backup-service/
│   ├── health-monitor/
│   └── docs/
└── shared/                  # Shared resources
    ├── examples/
    ├── litellm/
    └── scripts/
```

## Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

MIT License - see [LICENSE](./LICENSE)

---

**Built with ❤️ for the LLM community**
