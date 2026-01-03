# Twitter/X Thread

## Thread

**Tweet 1 (Hook)**
```
We open-sourced our LLM infrastructure stack.

One-click Railway templates for:
- LiteLLM (unified gateway to 100+ providers)
- Langfuse (tracing, costs, prompts)
- Full observability out of the box

Thread on what's included 🧵
```

**Tweet 2 (Problem)**
```
Every team building with LLMs needs:

✓ Single API for OpenAI/Anthropic/Gemini/etc
✓ Per-user API keys with budgets
✓ Cost tracking per request
✓ Request tracing
✓ Prompt versioning

Building this from scratch = weeks of work.
```

**Tweet 3 (Solution)**
```
Our templates deploy in 5 minutes:

Starter (~$35/mo):
- 7 services, everything you need to start

Production (~$45/mo):
- Adds daily backups to MinIO
- Health monitoring + Slack/Discord alerts
- Operations runbook included
```

**Tweet 4 (Code)**
```
Works with the OpenAI SDK you already use:

client = OpenAI(
    api_key="sk-virtual-key",
    base_url="https://your-gateway.railway.app/v1"
)

Every request automatically traced in Langfuse.
No instrumentation code needed.
```

**Tweet 5 (CTA)**
```
Links:

🔗 Starter template: [link]
🔗 Production template: [link]
📖 GitHub: github.com/amiable-dev/litellm-langfuse-railway

Looking for contributors! Check the "good first issue" label.
```

## Posting Notes

- Post as a thread, not individual tweets over time
- Include architecture diagram image with Tweet 1 if possible
- Tag @LiteLLM and @Langfuse
- Suggested hashtags (use sparingly): #LLM #OpenSource #DevTools
