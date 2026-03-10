# AI Native Lang (AINL) IR Schema (overview)

This document gives a **small‑model‑oriented view** of the IR shape produced by `compiler_v2.py`. It is intentionally high level; the canonical source of truth remains `AINL_SPEC.md`.
Cross-reference map:

- Spec: `AINL_SPEC.md#3-execution-model`
- Graph schema details: `GRAPH_SCHEMA.md`
- Runtime/compiler ownership: `RUNTIME_COMPILER_CONTRACT.md#source-of-truth`
- Strict conformance snapshot: `CONFORMANCE.md#5-conformance`

All examples below omit fields that are not relevant to small models.

---

## 1. Top‑level IR object

```json
{
  "ir_version": "1.0.0",
  "graph_schema_version": "1.0",
  "source": { "text": "...", "lines": ["..."] },
  "labels": { "<label_id>": { ... } },
  "services": { "core": { "eps": { ... } } },
  "capabilities": { ... },
  "runtime_policy": { "execution_mode": "graph-preferred", "unknown_op_policy": "skip" },
  "meta": [ ... ],
  "errors": [ "..." ],
  "warnings": [ "..." ],
  "graph_semantic_checksum": "sha256:...",
  "stats": { "lines": 0, "ops": 0 }
}
```

The fields that most small‑model workflows care about are `labels`, `services.core.eps`, `errors`, `warnings`, and `graph_semantic_checksum`.

---

## 2. Labels and graphs

Each label is stored under `labels[label_id]`:

```json
{
  "entry": "n1",
  "nodes": [
    {
      "id": "n1",
      "op": "R",
      "effect": "io",
      "effect_tier": "io-read",
      "reads": [],
      "writes": ["users"],
      "data": {
        "adapter": "db.F",
        "entity": "User",
        "fields": "*",
        "lineno": 3,
        "op": "R",
        "out": "users"
      },
      "hash": "sha256:..."
    }
  ],
  "edges": [
    { "from": "n1", "to": "n2", "port": "next", "to_kind": "node" }
  ],
  "exits": [
    { "node": "n2", "var": "users" }
  ],
  "id_hash": "sha256:..."
}
```

### 2.1 Fields

- `entry`: node id where execution starts.
- `nodes`: list of nodes; each has:
  - `id`: stable node id (`n1`, `n2`, …).
  - `op`: core op (`R`, `J`, `If`, etc.).
  - `effect` / `effect_tier`: effect classification.
  - `reads` / `writes`: frame variables used/defined.
  - `data`: op‑specific payload (adapter, entity, target, lineno, slots).
  - `hash`: stable semantic hash (content‑addressable id).
- `edges`: control‑flow edges:
  - `from`: node id.
  - `to`: node id or label id (`to_kind = "node" | "label"`).
  - `port`: `"next"`, `"err"`, `"retry"`, `"then"`, `"else"`, `"body"`, `"after"`.
- `exits`: terminal points (`J` nodes) and their return vars.
- `id_hash`: stable semantic hash for the label body.
- `legacy.steps` (optional): compatibility serialization only; canonical semantics remain graph-based.

These fields are what `tooling/graph_api.py`, `graph_diff.py`, and `ir_compact.py` operate on.

---

## 3. Endpoints

Endpoints live under `services.core.eps`:

```json
{
  "services": {
    "core": {
      "eps": {
        "/users": {
          "G": {
            "label_id": "1",
            "return_var": "users"
          }
        }
      }
    }
  }
}
```

Small models can use this to map HTTP routes to labels and expected return vars.

---

## 4. Policy hooks

The IR deliberately exposes fields that **policy validators** can consume:

- `labels[*].nodes[*].effect` / `effect_tier`
- `labels[*].nodes[*].data.adapter` – e.g. `"http.Get"`, `"db.F"`
- `services.core.eps` – endpoint paths and labels
- `capabilities` – configured services and auth

`tooling/policy_validator.py` builds on this to implement workspace‑level policies like:

- “No `http.*` adapters allowed.”
- “No `queue.Put` from cron labels.”

This is how you enforce **“no network access in this workspace”** at compile time.

---

## 5. Strict-mode literal and dataflow contract

Strict validation keeps defined-before-use guarantees aligned with runtime semantics.
In strict mode, bare identifier-like tokens in read positions are interpreted as
variable references; if literal intent is required, values must be quoted.

Practical migration fields:

- `Set.ref`
- `Filt.value`
- `CacheGet.key`
- `CacheGet.fallback`
- `CacheSet.value`
- `QueuePut.value`

See:

- `RUNTIME_COMPILER_CONTRACT.md#source-of-truth`
- `CONFORMANCE.md#minimal-conformance-test-matrix-intended`

