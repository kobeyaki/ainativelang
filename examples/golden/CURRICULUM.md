# AI Native Lang (AINL) Learning Curriculum for Small Offline Models

Goal: Teach a 3B–7B parameter model to write correct, production-ready AINL programs for common automation tasks (web servers, dashboards, scrapers, system scripts) without requiring deep knowledge of Rust/Python.

## Phase 1: Core Constructs (1–2 hours of fine-tuning or few-shot)

Learn the absolute minimum — 5 constructs that cover 80% of programs.

1. **S core cron "schedule"** — schedule a program
   - Pattern: `S core cron "*/5 * * * *"`
   - What it means: run every 5 minutes

2. **D Config var:type** — declare a configuration variable
   - Examples: `D Config threshold:N`, `D Config url:S`
   - What it means: these are overridable by environment or runtime

3. **D State var:type** — declare persistent state
   - Examples: `D State last_run:T`, `D State counter:N`
   - What it means: survives across runs via cache

4. **Lx: ... J ly** — label definition and jump
   - Example: `L0: ... J L1`
   - What it means: create a block and go to another block

5. **R adapter.target args ->var** — call an adapter and bind result
   - Example: `R http.GET url ->resp`
   - What it means: invoke a function and store its return value

6. **X var expr** — assign expression to variable
   - Example: `X next (core.add i 1)`
   - What it means: compute and store

7. **If (...) ->La ->Lb** — conditional branch
   - Example: `If (core.gt count threshold) ->L2 ->L3`
   - What it means: if true go to La else Lb

8. **J Lx** — unconditional jump
   - Example: `J L1`

9. **Set var expr** — mutation (for maps/arrays)
   - Example: `Set totals[category] (core.add totals[category] 1)`

**Deliverable:** Write a program that fetches a URL every 5 minutes and logs the status code to a state variable.

## Phase 2: Core Adapter palette (another 1–2 hours)

Learn the built-in operations via the core adapter:

- Arithmetic: `core.add`, `core.sub`, `core.mul`, `core.div`, `core.min`, `core.max`, `core.clamp`
- Strings: `core.concat`, `core.split`, `core.join`, `core.lower`, `core.upper`, `core.replace`
- JSON: `core.parse`, `core.stringify`
- Time: `core.now` (unix ts), `core.iso` (ISO string), `core.sleep(ms)`

Training tip: Provide 20 (prompt, correct call) pairs for each operation, plus 10 common mistakes (e.g., wrong arg count, type errors) with corrections.

**Deliverable:** Extend the fetcher to compute rolling average response time over last 10 runs (store array in state).

## Phase 3: The Four Essential Adapters

For real applications, models need these four adapters. Teach them one at a time.

### Adapter 1: HTTP
- `http.GET url [headers]` → `{status, headers, body}`
- `http.POST url body [headers] [timeout]`
- Common patterns: check `status`, parse JSON with `core.parse`, respect rate limits using state/cache.

### Adapter 2: SQLite
- `sqlite.query "SELECT ..." [params]` → `[row]`
- `sqlite.execute "INSERT ..." [params]`
- Safety: only SELECT for queries; table allowlists; parameterized queries.

### Adapter 3: FileSystem (sandboxed)
- `fs.read path` → string
- `fs.write path content` → `{ok, bytes}`
- `fs.list path` → `[filename]`
- Rules: paths must be inside sandbox_root; max sizes enforced.

### Adapter 4: Cache
- `cache.get namespace key` → value or null
- `cache.set namespace key value`
- Use for cross-run state, rate limiting, deduplication.

**Training patterns:**
- Read config from a JSON file on startup (fs.read + core.parse).
- Persist a counter across runs (cache.get/set).
- Paginate through a large dataset using state offsets.

**Deliverable:** Build a simple API server that reads a JSON data file, serves it at `/data`, and caches it for 60 seconds.

## Phase 4: Error Handling & Idempotency

AINL programs should be robust. Teach patterns:

- Check status codes before using response body.
- Use `Try` blocks if supported, or guard with `If` + `has?` checks.
- Make writes idempotent: write to temp then rename, or use `cache.set` as single source of truth.
- Throttle repeated alerts using `core.now` and `last_alert_time`.

**Deliverable:** Add retry with backoff to the fetcher (3 attempts, 1s/2s/4s delays).

## Phase 5: OpenClaw Integration Adapters (specialized)

These connect AINL to OpenClaw's capabilities:

- `email G` → list of unread emails
- `calendar G` → upcoming events
- `social G` → web search mentions
- `db F` → leads CSV rows
- `svc caddy|cloudflared|maddy` → "up"/"down"
- `queue.Put "notify" payload` → send message
- `cache` already covered

**Pattern:** Use these to build the AINL monitor system (provided as reference).

**Deliverable:** Write a monitor that checks email count, calendar events, and service status; sends a summary notification if thresholds exceeded.

## Phase 6: Composition & Real Projects

Combine all pieces into end-to-end applications:

1. **Web dashboard** (example 02) — serves HTML, auto-refreshes, admin route.
2. **Scraper** (example 03) — scheduled, rate-limited, appends to CSV.
3. **Log processor** (example 05) — batch file ops, aggregates stats.
4. **Alerting monitor** (example 04) — dedup, throttling, WASM health score.

Each should be:
- <300 lines of AINL
- Self-contained with comments
- Runnable with the provided adapter registry

## Training Data Outline

For fine-tuning a small model, prepare ~1k examples:

- 200 basic (phase 1–2): arithmetic, string ops, state mutations
- 300 adapter usage (phase 3): HTTP fetches, SQLite queries, file ops, cache patterns
- 200 error handling: try/except patterns, retry loops, validation
- 200 OpenClaw integrations: email/calendar/social queries, notifications
- 100 full programs: the 5 golden examples plus variations

Each example: `{ "prompt": "...", "program": "...", "explanation": "..." }`
Include negative examples: `{ "prompt": "...", "invalid_program": "...", "error": "...", "fix": "..." }`

## Tooling & Validation

- **Adapter manifest**: ADAPTER_REGISTRY.json (machine-readable spec)
- **Schema validation**: Create an AINL JSON schema to catch structural errors before compile.
- **Policy validator**: Walk IR and reject disallowed adapters/targets based on a policy file.
- **Fuzzy corrections**: Common model mistakes and tolerant compiler fixes (e.g., misspelled target → suggest closest).

## Next Steps

1. Generate the training set (I can help draft pairs).
2. Fine-tune a 3B model (e.g., Phi-3 mini) on the dataset.
3. Build an AINL language server with autocomplete and quick-fixes — this alone gives huge leverage to small models.
4. Package the adapter registry and examples as a model-readable knowledge base (e.g., markdown with code fences, or a vector DB).

You've already got a working compiler and runtime. The missing piece is the learning on-ramp for small models — that's what this curriculum provides.
