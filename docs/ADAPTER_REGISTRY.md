# AI Native Lang (AINL) Adapter Registry (v0.9)

This document describes the **small‑model‑friendly adapter set** exposed by this implementation. It is a human + machine readable catalog for agents.

The machine-readable source of truth is:

- `tooling/adapter_manifest.json`

Tests enforce consistency between that manifest and effect analysis:

- `tests/test_adapter_manifest.py`

For each adapter we specify:

- **name**: canonical adapter name.
- **verbs**: supported operations.
- **effect**: `io-read`, `io-write`, or `io`.
- **inputs**: slots and expected types.
- **outputs**: variables populated in the frame.
- **examples**: canonical `R` statements.

The same information can be exported as JSON from this document if needed.

---

## 1. Database adapter – `db`

- **name**: `db`
- **verbs**: `F` (find), `C` (create), `U` (update), `D` (delete)
- **effect**: `io-read` for `F`, `io-write` for `C/U/D`

### 1.1 Slot schema

```text
R db.F Entity filter ->out
R db.C Entity payload ->out
R db.U Entity filter payload ->out
R db.D Entity filter ->out
```

- `Entity`: identifier (e.g. `User`, `Order`).
- `filter`: expression or `*` for all.
- `payload`: expression or `*` for passthrough.
- `out`: frame variable that will hold the result.

### 1.2 Examples

```text
# Find all users
R db.F User * ->users

# Create a user (payload usually expanded by the compiler)
R db.C User * ->created_user
```

---

## 2. HTTP adapter – `http`

- **name**: `http`
- **verbs**: `Get`, `Post`
- **effect**: `io-read` (GET), `io-write` (POST)

### 2.1 Slot schema

```text
R http.Get /path_or_url ->resp
R http.Post /path_or_url body_var ->resp
```

- `/path_or_url`: either an absolute URL or a service‑relative path.
- `body_var`: frame var containing JSON‑serializable body.
- `resp`: frame variable receiving the decoded response.

### 2.2 Examples

```text
# Fetch users from an external API
R http.Get "https://api.example.com/users" ->resp

# Post metrics to webhook
R http.Post "https://hook.example.com/metrics" metrics ->ack
```

### 2.3 Result envelope (monitoring contract)

For monitoring-oriented flows, the `http` adapter is described as returning a **result envelope** with these fields:

- `ok: bool` — true if the HTTP call completed and the status code is considered successful (e.g. 2xx).
- `status_code: int|null` — HTTP status code if a response was received; `null` on pure transport error.
- `error: str|null` — transport-level error description (DNS failure, timeout, TLS error, etc.); `null` if none.
- `body: any` — decoded response body (string/JSON/etc.), as today.
- `headers: dict|none` — optional response headers, when available.
- `url: str` — URL/path that was called (for correlation).

This envelope is **descriptive metadata only** in this pass; it does not change current adapter behavior. Future monitoring patterns and agents can treat these fields as the canonical monitoring contract once runtime normalization is implemented.

---

## 3. Cache adapter – `cache`

- **name**: `cache`
- **verbs**: `Get`, `Set`
- **effect**: `io-read` / `io-write`

### 3.1 Slot schema

```text
R cache.Get key ->value
R cache.Set key value ttl_s ->ok
```

- `key`: string key.
- `value`: any JSON‑serializable value.
- `ttl_s`: integer seconds.

### 3.2 Examples

```text
R cache.Get "users:all" ->users_cache
R cache.Set "users:all" users 60 ->ok
```

---

## 4. Queue adapter – `queue`

- **name**: `queue`
- **verbs**: `Put`
- **effect**: `io-write`

### 4.1 Slot schema

```text
R queue.Put queue_name payload ->msg_id
```

- `queue_name`: identifier or string.
- `payload`: frame var.

### 4.2 Example

```text
R queue.Put "emails" email_job ->msg_id
```

### 4.3 Result envelope (monitoring contract)

For monitoring, the `queue` adapter is described as returning a **result envelope** with these fields:

- `ok: bool` — true if the enqueue operation reached the underlying queue backend successfully.
- `message_id: str|null` — backend-assigned message identifier, if available.
- `queue_name: str` — queue name used for the call.
- `error: str|null` — error description if enqueue failed at the adapter/backend layer.

As with `http`, this envelope is **descriptive metadata only** for now and does not alter current adapter return behavior. Existing examples may continue to ignore the result (`->_`) safely.

---

## 5. Service health adapter – `svc` (extension / OpenClaw)

- **name**: `svc`
- **verbs**: `caddy`, `cloudflared`, `maddy`, `crm`
- **support_tier**: `extension_openclaw`
- **lane**: non-canonical; OpenClaw-only extension adapter

The `svc` adapter is used by OpenClaw examples to surface basic service health information.

### 5.1 Result envelope (health contract, extension-only)

For OpenClaw environments, the `svc` adapter is described as returning a **health envelope** with these fields:

- `ok: bool` — true if the service is considered healthy enough under its own policy.
- `status: str` — status string such as `"up"`, `"down"`, `"degraded"`, or `"unknown"`.
- `latency_ms: int|null` — optional latency measurement in milliseconds, when available.
- `error: str|null` — error description if probing the service fails (e.g. health endpoint unreachable).

This is an **extension/OpenClaw-only contract** and is **not** part of the canonical AINL core. It is intended for monitoring and agent reasoning in OpenClaw deployments and is documented here for clarity; current runtime behavior is unchanged in this pass.

---

## 6. Adapter manifest (machine‑readable sketch and tiers)

For small‑model training you can treat this as the canonical manifest:

```json
{
  "db": {
    "verbs": ["F", "C", "U", "D"],
    "effects": { "F": "io-read", "C": "io-write", "U": "io-write", "D": "io-write" }
  },
  "http": {
    "verbs": ["Get", "Post"],
    "effects": { "Get": "io-read", "Post": "io-write" }
  },
  "cache": {
    "verbs": ["Get", "Set"],
    "effects": { "Get": "io-read", "Set": "io-write" }
  },
  "queue": {
    "verbs": ["Put"],
    "effects": { "Put": "io-write" }
  }
}
```

This manifest matches the behavior enforced by `tooling/effect_analysis.py` and the runtime adapters.

In the full `tooling/adapter_manifest.json`, each adapter also carries lightweight
classification metadata:

- `support_tier`: `core` \| `extension_openclaw` \| `compatibility`
- `strict_contract`: `true` if the adapter/verbs are covered by the current strict
  adapter/effect validation (`ADAPTER_EFFECT`), `false` otherwise
- `recommended_lane`: `canonical` \| `noncanonical` to distinguish the preferred
  canonical lane from accepted-but-noncanonical surfaces

`ADAPTER_REGISTRY.json` is a richer OpenClaw/operator-facing view (descriptions,
targets, config, side-effect notes). The overlapping adapter names/verbs are
validated against `tooling/adapter_manifest.json` by
`tests/test_adapter_registry_alignment.py` so they cannot silently diverge.

