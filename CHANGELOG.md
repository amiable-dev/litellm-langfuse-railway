# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- OSS project structure per ADR-001
- CODE_OF_CONDUCT.md (Contributor Covenant v2.1)
- CONTRIBUTING.md with cost awareness and testing guidelines
- SECURITY.md with upstream reporting links
- GitHub issue templates for bugs and features
- GitHub PR template with Railway-specific checklist
- CODEOWNERS for review routing
- Security workflow with Gitleaks secret scanning
- .editorconfig for consistent formatting

### Changed
- Enhanced .gitignore with Railway-specific entries

## [1.0.0] - 2026-01-03

### Added
- Initial release
- Starter template for quick LiteLLM + Langfuse deployment
- Production template with full configuration
- Shared LiteLLM configuration
- RUNBOOK.md for operational guidance
- UPGRADE.md for version upgrades
- COMPARISON.md for template selection

### Supported Versions
- LiteLLM: v1.56.0+
- Langfuse: v3.x
- PostgreSQL: 15+

[Unreleased]: https://github.com/amiable-dev/litellm-langfuse-railway/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/amiable-dev/litellm-langfuse-railway/releases/tag/v1.0.0
