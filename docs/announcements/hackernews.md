# Hacker News Post

## Title
```
Show HN: Open-source Railway templates for LiteLLM + Langfuse (LLM gateway + observability)
```

## Text Post
```
We've open-sourced our Railway templates for deploying LiteLLM and Langfuse together.

What it does:
- LiteLLM: Unified API gateway for 100+ LLM providers (OpenAI, Anthropic, Gemini, Bedrock, etc.)
- Langfuse: Tracing, cost tracking, prompt management, evaluations
- One-click deploy to Railway

Two templates:
- Starter (7 services, ~$35/mo): For development and POCs
- Production (9 services, ~$45/mo): Adds automated backups and health monitoring with alerts

The value: You get virtual API keys with budgets, per-request cost tracking, automatic failover, and full tracing—without building it yourself.

Technical details:
- PostgreSQL for transactional data
- ClickHouse for analytics
- Redis for caching
- MinIO for backups (production)
- All services communicate over Railway's private network

Code: https://github.com/amiable-dev/litellm-langfuse-railway

We're looking for feedback and contributions. The "good first issue" label has some starter tasks.
```

## Posting Notes

- Submit as text post, not link (better engagement)
- Be online for the first 2 hours to respond to comments
- Common questions to prepare for:
  - "Why Railway vs. k8s/Docker Compose?" → Simplicity, managed infra, easy scaling
  - "What about self-hosted alternatives?" → This IS self-hosted, just on Railway
  - "Cost breakdown?" → Link to detailed comparison doc
- Don't ask for upvotes or shares
