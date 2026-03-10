# AI Native Lang (AINL) Open Core Charter (Draft)

This charter defines how AINL will balance ecosystem adoption with sustainable
commercial development.

> Draft policy document for maintainer alignment and legal review. Not legal advice.

## Mission

Grow AINL as a broadly usable language/runtime ecosystem while maintaining a
clear path to fund long-term maintenance, reliability, and enterprise features.

## Principles

1. **Open foundation first**
   - Core language and developer experience must remain accessible and useful.
2. **Clear boundaries**
   - Contributors and adopters should always know what is open vs commercial.
3. **No surprise relicensing**
   - Material license/policy changes should be announced and documented.
4. **Interoperability**
   - Open interfaces and conformance expectations stay public.
5. **Quality and trust**
   - Security, governance, and maintainability are treated as product features.

## Open Core Commitments

The following categories are intended to remain in the open layer:

- AINL language spec and grammar references
- parser/AST and canonical compiler pathways
- reference runtime behavior and core adapters
- CLI fundamentals and baseline developer workflows
- public docs, examples, and conformance tests
- baseline eval harness behavior and report schemas

## Commercial Layer Intent

Commercial offerings should focus on enterprise-grade operating needs, including:

- managed runtime/orchestration
- governance/compliance controls
- enterprise connectors/integrations
- advanced observability and eval dashboards
- proprietary deployment kits and premium support/SLA
- premium model packs/checkpoints and enterprise tuning workflows

## Compatibility and Ecosystem

- Public conformance docs remain open.
- Trademark and compatibility branding policies are enforced consistently.
- "Official" compatibility labels and certifications are maintainer-governed.

## Contributor Expectations

- Contributions to open-core components follow repository contribution policies.
- Maintainers preserve boundary clarity in docs and release notes.
- Any boundary changes must be reflected in:
  - `README.md`
  - `CONTRIBUTING.md`
  - `docs/DOCS_INDEX.md`
  - `docs/CHANGELOG.md`

## Governance Notes

- Human maintainers retain final decision authority.
- AI contributors are first-class implementation collaborators under maintainer review.
- Decision records should prioritize transparency for future maintainers.
