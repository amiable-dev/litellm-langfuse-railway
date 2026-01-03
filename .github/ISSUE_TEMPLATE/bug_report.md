---
name: Bug Report
about: Report a deployment or template issue
title: '[BUG] '
labels: bug, needs-triage
assignees: ''
---

## Description

A clear and concise description of the bug.

## Template Used

- [ ] Starter (`starter/`)
- [ ] Production (`production/`)

## Steps to Reproduce

1. Deploy template with '...'
2. Configure '...'
3. See error

## Expected Behavior

What you expected to happen.

## Actual Behavior

What actually happened.

## Environment

- **Railway Project ID**: [e.g., abc123 - find in Railway dashboard URL]
- **Template Version/Commit**: [e.g., main, v1.0.0, or commit SHA]
- **LiteLLM Version**: [from Railway service logs]
- **Langfuse Version**: [from Railway service logs]

## Logs/Output

```
Paste any relevant logs from Railway dashboard here
```

## Is this a template issue or upstream issue?

- [ ] **Template issue** - Problem with our Railway configuration
- [ ] **Upstream issue** - Problem with LiteLLM/Langfuse themselves
- [ ] **Unsure** - I need help determining this

> **Note:** For LiteLLM bugs, report to [BerriAI/litellm](https://github.com/BerriAI/litellm/issues).
> For Langfuse bugs, report to [langfuse/langfuse](https://github.com/langfuse/langfuse/issues).

## Additional Context

Add any other context about the problem here.

## Checklist

- [ ] I have searched existing issues for duplicates
- [ ] I have included the template version above
- [ ] I have checked Railway service logs
- [ ] I can reproduce this issue consistently
