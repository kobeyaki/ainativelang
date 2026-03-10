# Open Core Boundary Map (Draft)

This map defines the intended boundary between open and commercial capabilities.

> Draft for product/legal alignment. Final scope may change before publication.

## Intended Open Layer

### Language and Compiler

- AINL syntax/spec and grammar references
- parser + canonical IR generation
- reference emitters for public developer workflows
- baseline validation and conformance tooling

### Runtime and Developer Tooling

- reference runtime engine
- core adapter interfaces + basic adapters
- CLI commands needed for local development and testing
- baseline trace/diagnostic output formats

### Docs and Examples

- architecture/spec/runtime docs
- contribution and continuity docs
- tutorial examples and reference fixtures

## Intended Commercial Layer

### Enterprise Runtime and Orchestration

- managed multi-tenant runtime operations
- enterprise scheduling/orchestration control plane
- advanced reliability policies and failover controls

### Governance and Compliance

- policy governance suites
- audit/compliance workflows and controls
- enterprise identity/role administration overlays

### Enterprise Integrations

- proprietary or premium connector packs
- enterprise-specific deployment templates and operations kits

### Advanced Quality and Model Operations

- premium evaluation dashboards
- managed regression/quality operations
- premium tuned checkpoints/model packs and support workflows

### Commercial Support

- SLA-backed support
- priority issue response
- enterprise onboarding and success plans

## Boundary Rules

- Open layer remains functional and useful without paid components.
- Paid components may depend on open interfaces but should not silently replace them.
- Public docs should clearly mark whether a feature is:
  - Open
  - Commercial
  - Planned

## Labeling Convention (Recommended)

Use doc labels for clarity:

- `Open Core`
- `Commercial`
- `Planned`

This minimizes confusion for developers, researchers, and AI contributors.
