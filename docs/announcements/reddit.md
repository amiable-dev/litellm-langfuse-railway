# Reddit Posts

## r/MachineLearning

### Title
```
[P] Open-source Railway templates for LLM gateway (LiteLLM) + observability (Langfuse)
```

### Body
```
We've released open-source Railway templates that deploy a complete LLM infrastructure stack:

**What's included:**
- **LiteLLM**: Unified gateway to 100+ LLM providers with a single OpenAI-compatible API
- **Langfuse**: Full observability—tracing, cost tracking, prompt management, evals
- **Supporting infrastructure**: PostgreSQL, ClickHouse, Redis, MinIO

**Two variants:**
- Starter (~$35/mo): 7 services, good for development
- Production (~$45/mo): Adds automated backups and health monitoring

**Why we built it:**
Every team deploying LLMs ends up building the same infrastructure: API gateway, cost tracking, request tracing. This packages that stack into a one-click deploy.

**Architecture:**
```
App (OpenAI SDK) → LiteLLM Gateway → 100+ Providers
                         ↓
                  Langfuse (traces, costs)
```

GitHub: https://github.com/amiable-dev/litellm-langfuse-railway

Happy to answer questions. Looking for contributors if anyone wants to help improve the templates.
```

---

## r/LLMOps

### Title
```
Open-sourced our LiteLLM + Langfuse Railway templates
```

### Body
```
Just open-sourced the Railway templates we use for LLM infrastructure.

**Stack:**
- LiteLLM for unified API gateway (virtual keys, budgets, failover)
- Langfuse for observability (traces, costs, prompts)
- PostgreSQL + ClickHouse + Redis + MinIO

**Deploys in one click:**
- Starter template: 7 services, ~$35/mo
- Production template: 9 services, adds backups + health monitoring, ~$45/mo

We documented everything including an operations runbook for the production template.

Repo: https://github.com/amiable-dev/litellm-langfuse-railway

Contributions welcome—check the "good first issue" label if interested.
```

---

## r/selfhosted

### Title
```
One-click Railway templates for self-hosted LLM gateway + observability
```

### Body
```
For those running LLM workloads: we open-sourced Railway templates that deploy LiteLLM (API gateway) and Langfuse (observability) together.

**What you get:**
- Single API endpoint for OpenAI, Anthropic, Gemini, Bedrock, etc.
- Virtual API keys with budgets and rate limits
- Full request tracing and cost tracking
- Prompt versioning

**Self-hosted benefits:**
- Your data stays in your Railway project
- Full control over configuration
- No vendor lock-in (all open-source components)

**Templates:**
- Starter: 7 services, ~$35/mo
- Production: 9 services with automated backups, ~$45/mo

GitHub: https://github.com/amiable-dev/litellm-langfuse-railway

It's not truly "self-hosted" in the bare-metal sense, but Railway gives you dedicated instances with full control. Happy to answer questions about the architecture.
```

## Posting Notes

- Check each subreddit's self-promotion rules before posting
- r/MachineLearning requires [P] tag for projects
- Space posts out by at least a few hours
- Be genuine in responses, don't just link back to the repo
