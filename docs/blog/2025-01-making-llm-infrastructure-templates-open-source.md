# Making LLM Infrastructure Templates Open Source

*January 2025*

The [amiable.dev](https://amiable.dev) team is opening up our LiteLLM + Langfuse Railway templates to the community. Here's what we did and why.

## The Problem

Every team deploying LLMs needs the same things: a unified gateway, cost tracking, and observability. We built Railway templates that deploy this stack in one click:

```
Your App (OpenAI SDK) → LiteLLM → 100+ Providers
                           ↓
                    Langfuse (traces, costs)
```

But templates sitting in a private repo don't help anyone.

## What We Added

Instead of dumping code and hoping for the best, we followed a structured approach (documented in [ADR-001](../adr/ADR-001-oss-project-structure.md)):

**Security first:**
- Gitleaks in CI to catch leaked secrets
- Dependabot for dependency updates
- Clear vulnerability reporting process

**Make contributing easy:**
- Issue templates with required fields
- PR template with a checklist
- CODEOWNERS so reviews don't sit

**Automate the boring stuff:**
- Template validation (taplo, yamllint)
- Pre-commit hooks for local checks
- GitHub Actions for CI/CD

## The Stack

Two templates, same core:

| | Starter | Production |
|---|---------|------------|
| Services | 7 | 9 |
| Backups | - | Daily to MinIO |
| Monitoring | - | Health checks + alerts |
| Railway Cost* | ~$35/mo | ~$45/mo |

*Infrastructure only, excludes LLM API usage.

Both give you:
- Virtual API keys with budgets
- Automatic failover between providers (when configured)
- Full request tracing
- Prompt versioning

## Quick Start

```python
from openai import OpenAI

# Point at your deployed LiteLLM gateway
client = OpenAI(
    api_key="sk-your-virtual-key",  # LiteLLM virtual key, not OpenAI
    base_url="https://your-litellm.railway.app/v1"
)

# Use any model through one API
response = client.chat.completions.create(
    model="gpt-4o",  # or claude-3-5-sonnet, gemini-pro, etc.
    messages=[{"role": "user", "content": "Hello!"}]
)
```

Tracing is captured at the gateway. No instrumentation needed in your app.

## Next Steps

1. **[Deploy Starter Template](https://railway.app/template/STARTER_ID)** - Get running in 5 minutes
2. Send a test request using the snippet above
3. Check traces and costs in your Langfuse dashboard
4. [File an issue](https://github.com/amiable-dev/litellm-langfuse-railway/issues) when something's missing

Ready for production? **[Deploy Production Template](https://railway.app/template/PRODUCTION_ID)** when you need backups and alerting.

## Contributing

We want contributions that make the templates more useful:

- **Starter issues**: Bug fixes, doc improvements
- **Bigger stuff**: New monitoring integrations, additional provider configs

Check out [good first issues](https://github.com/amiable-dev/litellm-langfuse-railway/labels/good%20first%20issue) if you want to help.

## What's Next

- More example configurations
- Additional alerting integrations
- Terraform modules (maybe)

---

*Questions? Open a [discussion](https://github.com/amiable-dev/litellm-langfuse-railway/discussions) or file an [issue](https://github.com/amiable-dev/litellm-langfuse-railway/issues).*
