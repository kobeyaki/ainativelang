# Autonomous Ops Extension Examples

These examples live in `examples/autonomous_ops/` and are **extension/OpenClaw autonomous-ops examples**, not part of the canonical strict-valid lane.

They demonstrate small, auditable **snapshot → queue** patterns that are useful for long-running autonomous agents:

- sequential data gathering from existing adapters
- minimal derived values where semantics are already used elsewhere
- structured payload emission to a queue for downstream automation

## Examples in this pack

- `examples/autonomous_ops/status_snapshot_to_queue.lang`
  - **Purpose**: gather current service/dependency status (via `svc`) and emit a structured status snapshot to a queue.
  - **Adapters**: `svc`, `queue`, `core`.
  - **Classification**: `extension_openclaw`, non-canonical, profile `non-strict-only`.

- `examples/autonomous_ops/backup_freshness_to_queue.lang`
  - **Purpose**: read current time and last backup timestamp from cache, compute simple freshness (age in seconds/hours), and emit a backup freshness snapshot to a queue.
  - **Adapters**: `cache`, `queue`, `core`.
  - **Classification**: `extension_openclaw`, non-canonical, profile `non-strict-only`.

- `examples/autonomous_ops/pipeline_readiness_snapshot.lang`
  - **Purpose**: gather readiness/status signals for a multi-step pipeline from `svc` and emit a structured readiness snapshot to a queue.
  - **Adapters**: `svc`, `queue`, `core`.
  - **Classification**: `extension_openclaw`, non-canonical, profile `non-strict-only`.

Use these as **operational extension examples** for autonomous agents, not as core language conformance references.
