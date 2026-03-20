# Moved

This compatibility stub preserves old links for `docs/ADAPTER_REGISTRY.md`.

This document now lives at [`reference/ADAPTER_REGISTRY.md`](reference/ADAPTER_REGISTRY.md).

Use [`docs/README.md`](README.md) as the primary navigation hub and [`reference/README.md`](reference/README.md) for the reference section.

---

## 8. Agent coordination adapter – `agent` (extension / OpenClaw, advanced)

- **name**: `agent`
- **verbs**: `send_task`, `read_result`
- **support_tier**: `extension_openclaw`
- **lane**: non-canonical; OpenClaw-only extension adapter
- **intended audience**: advanced operators building local coordination loops;
  **not** a safe default for unsupervised agents.

The `agent` adapter provides a **minimal, local, file-backed** substrate for
exchanging `AgentTaskRequest` and `AgentTaskResult` envelopes as defined in
`docs/advanced/AGENT_COORDINATION_CONTRACT.md`. It does **not** implement a swarm engine
or remote federation, and it should be treated as an **advanced, opt-in**
coordination surface rather than a general-purpose production control plane.

### 8.1 `send_task` verb (append AgentTaskRequest to JSONL)

`agent.send_task` expects:

- first argument: a JSON object matching `AgentTaskRequest` (or a compatible
  subset).

Behavior:

- resolves the sandbox root from `AINL_AGENT_ROOT` (default:
  `/tmp/ainl_agents`),
- computes the target file path as `root / rel_path`,
- rejects any attempt to escape the root (e.g. `../..`) with an `AdapterError`,
- JSON-serializes the envelope and appends it as a single line to the target
  file (JSONL format).

Return value:

- `task_id: str` — copied from `envelope["task_id"]` when present, else empty string.

This verb is intended as a **thin bridge** between AINL-based monitors and an
external orchestrator that reads `AgentTaskRequest` lines from the JSONL file.

### 8.2 `read_result` verb (read AgentTaskResult JSON)

`agent.read_result` expects:

- first argument: a `task_id` string.

Behavior:

- resolves the sandbox root from `AINL_AGENT_ROOT` (default:
  `/tmp/ainl_agents`),
- computes the target file path as `root / rel_path`,
- rejects any attempt to escape the root with an `AdapterError`,
- reads the target file and parses it as JSON,
- requires the top-level JSON value to be an object.

Return value:

- the parsed JSON object (compatible with `AgentTaskResult`).

Failure modes:

- missing or non-file path → `AdapterError("agent.read_result target does not exist")`
- invalid JSON → `AdapterError("agent.read_result failed to parse JSON: ...")`
- top-level value not an object → `AdapterError("agent.read_result expects JSON object result")`

This verb is a **local-only, read-only helper** for consuming previously written
result artifacts (for example, results emitted by an external orchestrator). It
does not change core AINL semantics and should be treated as an OpenClaw-specific
extension surface.

For cross-tool (Cursor ↔ OpenClaw) coordination, the **only** shared protocol
surface in this adapter is the combination of `send_task` and `read_result`.
Any additional verbs present in a specific OpenClaw deployment (such as
discovery or task-reading helpers) are extension-specific and are **not** part
of the agreed shared protocol.
