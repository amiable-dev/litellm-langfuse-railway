# Governance

This document describes the governance structure and decision-making process for the litellm-langfuse-railway project.

## Project Structure

### Roles

#### Maintainers

Maintainers have full commit access and are responsible for:

- Reviewing and merging pull requests
- Triaging issues
- Making template architecture decisions
- Releasing new versions
- Enforcing the code of conduct

**Current Maintainers:**
- @amiable-dev/maintainers

#### Contributors

Anyone who contributes to the project through:

- Template improvements (pull requests)
- Documentation improvements
- Bug reports and feature requests
- Helping others in discussions
- Reviewing pull requests

All contributors are listed in the commit history and release notes.

## Decision Making

### Architecture Decision Records (ADRs)

Significant technical decisions are documented as ADRs in `docs/adr/`. We follow the Michael Nygard format.

**Process:**

1. **Draft**: Create an ADR using the [template](docs/adr/ADR-000-template.md)
2. **Propose**: Open a PR for discussion
3. **Review**: Request LLM Council feedback if applicable
4. **Decide**: Maintainers review and merge (Status: Accepted)

### Template Changes

| Change Type | Required Reviewers | Discussion Period |
|-------------|-------------------|-------------------|
| Bug fixes | 1 maintainer | None |
| New environment variable | 1 maintainer | None |
| New service added | 1 maintainer | 3 days |
| Breaking changes (env var rename, service removal) | 2 maintainers | 7 days |
| Major version release | 2 maintainers | 14 days |

### Breaking Changes

A change is considered "breaking" if users must modify their Railway configuration after upgrading. Examples:

- Environment variable renamed or removed
- Service name changed
- Required new dependency
- Port number changed

Breaking changes require:

- ADR documenting the change
- Migration guide in the PR
- Minimum 7-day discussion period
- CHANGELOG.md entry with migration steps
- MAJOR version bump

## Versioning

We follow [Semantic Versioning](https://semver.org/):

- **MAJOR**: Breaking changes to template configuration
- **MINOR**: New features (new services, new config options)
- **PATCH**: Bug fixes, documentation updates

### Release Process

1. Update CHANGELOG.md
2. Create release PR
3. After merge, create Git tag (e.g., `v1.1.0`)
4. Create GitHub Release with notes

## Scope

### In Scope

- Railway template configurations
- LiteLLM/Langfuse deployment best practices
- Documentation for template usage
- CI/CD for template validation

### Out of Scope

- LiteLLM/Langfuse runtime bugs (report upstream)
- Railway platform issues (contact Railway)
- Multi-cloud deployment (Railway-only)
- Custom features not part of standard deployment

## Succession

If maintainers become inactive:

1. **30 days**: Community may open issue requesting status update
2. **60 days**: GitHub org admins may add new maintainers from active contributors
3. **90 days**: Project may be archived or transferred

## Code of Conduct

All participants must follow our [Code of Conduct](CODE_OF_CONDUCT.md). Violations can be reported to conduct@amiable.dev.

## Amendments

This governance document can be amended by:

1. Opening a PR with proposed changes
2. 7-day discussion period
3. Approval by majority of maintainers
4. Changes take effect upon merge

## Contact

- **General**: Open a GitHub Discussion
- **Security**: security@amiable.dev
- **Conduct**: conduct@amiable.dev
