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

---

## 5. Adapter manifest (machine‑readable sketch)

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

