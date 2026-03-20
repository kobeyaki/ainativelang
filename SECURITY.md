# Security Policy

Thank you for helping keep AI Native Lang (AINL) and its ecosystem safe.

## Supported Versions

Security fixes are generally prioritized for:

- The latest released version
- The current development branch, where applicable

Older versions may receive fixes at maintainer discretion depending on severity, impact, and available bandwidth.

## Scope

Security issues may include vulnerabilities affecting:

- The AINL compiler, interpreter, or runtime
- Core language tooling and adapters
- Packaging or dependency integrity
- Generated artifacts or execution surfaces created by official tooling
- Training, evaluation, or orchestration components that could introduce meaningful security risk
- Official project infrastructure, release pipelines, or distribution mechanisms

## Out of Scope

The following are usually **not** treated as security vulnerabilities by themselves, unless they create a concrete exploit path or materially increase security risk:

- Feature requests
- Performance issues
- Pure correctness bugs without security impact
- Unsafe deployment choices made outside official project defaults
- Risks caused solely by third-party infrastructure not maintained by the project
- Hypothetical issues without a reproducible scenario or clear impact

## Reporting a Vulnerability

Please report suspected vulnerabilities **privately**.

Preferred channel:

- GitHub Security Advisories ("Report a vulnerability" in the Security tab), when enabled for this repository.

If private vulnerability reporting is not available in the repository UI:

- Open a minimal public issue requesting a private security contact channel.
- Do not include exploit details, proof-of-concept payloads, or sensitive data in that public issue.

Please do **not** post full technical details publicly before coordinated triage.

## What to Include

When reporting, please include as much of the following as practical:

- Affected component, module, file, or release
- Description of the issue
- Reproduction steps or proof of concept
- Expected impact and severity estimate
- Environment details:
  - OS
  - language/runtime version
  - dependency versions
  - container/runtime details if relevant
- Any suggested mitigations or patches, if available

## Response Expectations

Targets, not guarantees:

- Initial acknowledgment: within **72 hours**
- Triage and severity assessment: after the issue is reproducible and understood
- Fix and disclosure timing: coordinated based on severity, exploitability, and user impact

## Disclosure Process

If a report is accepted as a vulnerability, maintainers will generally aim to:

1. Confirm and reproduce the issue
2. Assess severity and affected scope
3. Develop and validate a fix or mitigation
4. Coordinate release timing
5. Publish an advisory or release note when appropriate

We ask reporters to avoid public disclosure until maintainers have had a reasonable opportunity to investigate and ship a fix or mitigation.

## Hardening Guidance

Users deploying AINL in real systems should consider the following baseline practices:

- Run with least-privilege credentials
- Prefer sandboxed or isolated execution where practical
- Keep dependencies pinned and reviewed in CI/CD environments
- Review generated server, infrastructure, or deployment artifacts before production use
- Restrict secrets exposure in prompts, pipelines, adapters, and logs
- Apply standard supply-chain and artifact integrity controls for production environments

## No Warranty

Security review and remediation are provided on a best-effort basis unless separately agreed in writing.
