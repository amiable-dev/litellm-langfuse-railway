# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| main    | :white_check_mark: |

We recommend always using the latest version from the `main` branch.

## Scope

This repository provides **deployment templates** for Railway. Security issues should be reported to the appropriate project:

| Issue Type | Report To |
|------------|-----------|
| Template security (insecure defaults, exposed ports, missing auth) | **This repository** (see below) |
| LiteLLM runtime vulnerabilities | [LiteLLM Security](https://github.com/BerriAI/litellm/security) |
| Langfuse runtime vulnerabilities | [Langfuse Security](https://github.com/langfuse/langfuse/security) |
| Railway platform issues | [Railway Support](https://railway.app/help) |

## Reporting a Vulnerability

**Please do not report security vulnerabilities through public GitHub issues.**

### For Template Security Issues

If you discover a security vulnerability in our deployment templates (e.g., insecure default configurations, exposed secrets in examples, missing authentication requirements), please report it by emailing:

**security@amiable.dev**

Please include:

1. **Description** of the vulnerability
2. **Steps to reproduce** or proof of concept
3. **Affected files** (e.g., `starter/railway.toml`, `shared/litellm/config.yaml`)
4. **Potential impact** on deployments using this template
5. **Suggested fix** (if any)

### Response Timeline

| Stage | Timeframe |
|-------|-----------|
| Initial response | 48 hours |
| Triage and assessment | 7 days |
| Fix for critical issues | Best effort |

We will acknowledge receipt of your report and provide an estimated timeline for a fix.

## Security Best Practices for Users

### Before Deploying

1. **Never commit secrets** to your forked repository
2. **Review all environment variables** before deploying
3. **Use Railway's secret management** for sensitive values
4. **Enable authentication** on all exposed endpoints

### If You Accidentally Expose Secrets

1. **Rotate immediately** in Railway dashboard (Settings > Variables)
2. **Revoke API keys** at the provider (OpenAI, Anthropic, etc.)
3. **Check Railway audit logs** for unauthorized access
4. **Force-push** to remove secrets from git history (if committed)

You do not need to report accidental secret exposure to maintainers unless it reveals a template-related vulnerability.

### Recommended Security Configuration

```yaml
# In your LiteLLM config, always set:
general_settings:
  master_key: ${LITELLM_MASTER_KEY}  # Never hardcode

# Langfuse should use:
LANGFUSE_SECRET_KEY: <generated-in-railway>
NEXTAUTH_SECRET: <generated-in-railway>
```

## Security Scanning

This repository uses automated security scanning:

- **Gitleaks**: Scans for accidentally committed secrets
- **Dependabot**: Monitors GitHub Actions for vulnerabilities
- **Branch Protection**: Requires PR reviews for changes

## Acknowledgments

We appreciate security researchers who help keep this project and its users safe. Contributors who report valid security issues will be acknowledged in release notes (unless they prefer to remain anonymous).

## Contact

For security inquiries: security@amiable.dev

For general questions: See [SUPPORT.md](SUPPORT.md)
