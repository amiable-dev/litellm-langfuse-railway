# Contributing to litellm-langfuse-railway

Thank you for your interest in contributing to this project! This document provides guidelines for contributing to our Railway deployment templates.

## Code of Conduct

This project adheres to the [Contributor Covenant Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.

## Important: Cost Awareness

> **Warning**: Testing these templates creates real resources on Railway which may incur costs. Contributors are responsible for their own Railway credits and LLM API usage.

Before testing:
1. Review Railway's [pricing](https://railway.app/pricing)
2. Set up spending limits in your Railway dashboard
3. Use test/development API keys with low limits
4. Delete test projects promptly after validation

## Getting Started

### Prerequisites

- [Railway CLI](https://docs.railway.app/guides/cli) installed
- Railway account with available credits
- Git
- Basic understanding of Docker, TOML, and YAML

### Development Setup

1. **Fork and clone the repository:**
   ```bash
   git clone https://github.com/YOUR-USERNAME/litellm-langfuse-railway.git
   cd litellm-langfuse-railway
   ```

2. **Review the template structure:**
   ```
   starter/          # Minimal setup for getting started
   production/       # Production-ready with all features
   shared/           # Common configurations
   ```

3. **Install pre-commit hooks (recommended):**
   ```bash
   pip install pre-commit
   pre-commit install
   ```

## Development Workflow

### Creating a Branch

Create a feature branch from `main`:

```bash
git checkout main
git pull origin main
git checkout -b feature/your-feature-name
```

Branch naming conventions:
- `feature/` - New features or template additions
- `fix/` - Bug fixes or configuration corrections
- `docs/` - Documentation changes
- `chore/` - Maintenance tasks

### Making Changes

1. **Edit template files** (railway.toml, config.yaml, docker-compose.yml)
2. **Validate locally** (see Testing section)
3. **Test deployment** if the change is significant
4. **Update documentation** as needed

### Testing Strategy

#### 1. Static Validation (Required)

```bash
# Validate TOML syntax
taplo check starter/railway.toml production/railway.toml

# Validate YAML syntax
yamllint shared/litellm/config.yaml

# Validate Docker Compose
docker compose -f starter/docker-compose.yml config

# Check for secrets (pre-commit hook does this)
gitleaks detect --source .
```

#### 2. Deploy Validation (For Significant Changes)

```bash
# Create a test Railway project
railway login
railway init

# Link and deploy
railway link
railway up --detach

# Verify health endpoints
curl https://your-project.up.railway.app/health
```

**Remember:** Delete test projects after validation!

#### 3. PR Submission

Include in your PR:
- Screenshot of passing static validation
- For deploy changes: evidence of successful deployment (health check output)

### Commit Messages

We follow conventional commit format:

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only
- `chore`: Maintenance tasks

**Examples:**
```
feat(production): add Redis caching for LiteLLM

fix(starter): correct Langfuse port configuration

docs: update RUNBOOK with troubleshooting steps
```

### Developer Certificate of Origin (DCO)

All commits must be signed off to certify you have the right to submit the code:

```bash
git commit -s -m "feat(production): add new feature"
```

This adds a `Signed-off-by` line to your commit message:
```
Signed-off-by: Your Name <your.email@example.com>
```

### Pull Requests

1. **Push your branch:**
   ```bash
   git push -u origin feature/your-feature-name
   ```

2. **Create a pull request** via GitHub

3. **Fill out the PR template** with:
   - Summary of changes
   - Template(s) affected
   - Test evidence
   - Checklist completion

4. **Address review feedback** promptly

5. **Ensure CI passes** before requesting merge

## What to Contribute

### Good First Issues

Look for issues labeled `good first issue`:
- Documentation improvements
- Error message clarifications
- Adding comments to configuration files

### Template Improvements

- New environment variable options
- Service configuration enhancements
- Performance optimizations
- Security hardening

### Not in Scope

- LiteLLM or Langfuse runtime bugs (report upstream)
- Railway platform issues (contact Railway support)
- Multi-cloud deployments (Railway-only project)

## Secrets Handling

**Critical rules:**

1. **Never commit `.env` files** - they're in `.gitignore`
2. **Use placeholders in examples:** `your-api-key-here`, `changeme`, `<YOUR_KEY>`
3. **Railway variables only** - all secrets go in Railway dashboard
4. **Forked repos don't inherit secrets** - contributors use their own

## Issue Labels

| Label | Description |
|-------|-------------|
| `bug` | Deployment or template issues |
| `enhancement` | Template improvements |
| `documentation` | README/docs updates |
| `good first issue` | Good for newcomers |
| `help wanted` | Extra attention needed |
| `starter-template` | Affects starter/ |
| `production-template` | Affects production/ |
| `upstream` | Issue belongs to LiteLLM/Langfuse |

## Questions?

- Check the [README](README.md) for usage documentation
- See [SUPPORT.md](SUPPORT.md) for support channels
- Open a [Discussion](https://github.com/amiable-dev/litellm-langfuse-railway/discussions) for questions

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
