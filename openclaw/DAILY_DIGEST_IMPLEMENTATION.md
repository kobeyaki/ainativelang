# Daily Digest — AINL Implementation Report

## Program Purpose
The Daily Digest (`examples/openclaw/daily_digest.lang`) is a scheduled AINL agent that runs every morning at 08:00. It fetches unread emails, today’s calendar events, and recent social mentions; then it summarizes the results via a WASM module and delivers a friendly notification through the OpenClaw event bus. The program demonstrates how to combine multiple adapters (email, calendar, social, cache, queue, wasm, core) in a concise, time‑aware workflow.

## Why AINL Was Chosen
- **Deterministic scheduling**: AINL’s `S core cron` embeds the schedule directly in the source; no external cron definition needed.
- **Adapter composition**: One‑liner calls to `email G`, `calendar G`, `social G` fetch disparate data into a common shape.
- **State persistence**: `cache.get`/`set` maintains `last_digest` across runs, respecting a minimum interval (`digest_hours`).
- **WASM extension**: The `wasm.CALL summarize` hook allows swapping the summarization model without altering AINL code.
- **Compact representation**: The entire program is ~20 lines of AINL yet expresses a multi‑step ETL + notification pipeline.

## AINL Code Walkthrough

### Service Declaration
```ainl
S core cron "0 8 * * *"
```
Registers a cron service with the given schedule; OpenClaw’s cron runner will execute this program daily at 08:00.

### Types
```ainl
D Config digest_hours:N
D State last_digest:T
```
Declares configuration (`digest_hours`, minimum hours between digests) and persistent state (`last_digest`, timestamp of last run). Types: `N` for number, `T` for timestamp.

### Main Flow
```ainl
L0: R core now ->ts J L1
L1: R cache get "state" "last_digest" ->last_digest J L2
L2: X hours_diff (core.div (core.sub ts last_digest) 3600)
L3: X need_run (core.gt hours_diff Config.digest_hours)
L4: If need_run ->L5 ->L62
```
- `L0`: Get current timestamp (`core.now`) into `ts`; jump to `L1`.
- `L1`: Retrieve `last_digest` from the cache; jump to `L2`.
- `L2`: Compute `hours_diff` = `(ts - last_digest) / 3600`.
- `L3`: Compute `need_run` = `hours_diff > Config.digest_hours`.
- `L4`: If `need_run` → run digest; else → exit (`L62`). Strict mode would require `X need_run ...` and numeric labels; this version is non‑strict but illustrates the pattern.

### Data Gathering
```ainl
L5: R email G ->emails J L6
L6: R calendar G ->events J L7
L7: R social G ->mentions J L8
```
Calls to `email.G`, `calendar.G`, `social.G` return lists of items (unread emails, today’s events, recent mentions). Each call tail‑calls to the next label.

### Aggregation
```ainl
L8: X email_count (len emails)
L9: X event_count (len events)
L10: X mention_count (len mentions)
```
Compute counts from the lists using `len`.

### Payload Construction
```ainl
L11: X payload {"email_count":email_count,"event_count":event_count,"mention_count":mention_count,"ts":ts}
```
Builds a JSON object (AINL’s record literal) containing the counts and the timestamp.

### Summarization via WASM
```ainl
L12: X summary (wasm.CALL summarize payload)
```
Invokes a WASM module function `summarize` with the payload, producing a human‑readable summary string. This is a clean extension point; the WASM module can be swapped or tuned without touching the AINL.

### Notification
```ainl
L13: R queue Put notify {"summary":summary,"ts":ts} ->_ J L14
```
Enqueues a notification message (queue semantics). OpenClaw’s queue → Telegram emitter delivers it to the user.

### State Update
```ainl
L14: R cache set "state" "last_digest" ts ->_ J L62
```
Stores the current `ts` as `last_digest` to satisfy the cooldown interval.

### Exit
```ainl
L62: (implicit end)
```
The program ends; cron runner returns success.

## Key Language Features
- `S` with `cron` schedule embeds timing; no external configuration.
- `D` declares types; optional but good practice.
- `R group verb` adapter calls: `email G`, `calendar G`, `social G`, `core now`, `cache get/set`, `queue Put`, `wasm CALL`.
- `X` expressions: `core.div`, `core.sub`, `core.gt`, `len`, record construction, function application.
- Control flow: `If` (non‑strict here) and `J` tail‑calls.
- Cache persistence for cross‑run state (`last_digest`).
- WASM integration for pluggable computation.

## Why This Is a Strong Example
- **Real‑world utility**: Daily aggregation of multiple data sources is a common personal automation need.
- **Minimal code**: ~20 labels and a dozen adapter calls; easy to understand and modify.
- **Clear extension points**: Change schedule, add more adapters (e.g., `db` for custom stats), swap WASM summarizer for a fine‑tuned model.
- **Cross‑run state**: Demonstrates cache usage for idempotent scheduling.
- **Adapter diversity**: Shows `email`, `calendar`, `social`, `cache`, `queue`, `wasm`, and `core` together in one coherent graph.

## Lessons Learned
- The non‑strict `If` without precomputed variable can work but is fragile; strict mode would require computing `need_run` in a separate `X` and then using `If need_run ->...`. However, this program is simple enough that the current form remains readable.
- WASM module must be placed where the runtime can find it (project-local path or configured import). The `wasm.CALL` syntax requires the module to be pre‑loaded in the registry.
- The `cron` schedule in `S` is declarative; the OpenClaw cron runner parses it and triggers execution accordingly.
- Tail‑calls (`J`) keep the IR acyclic and the engine’s label execution linear; no return stack needed.

## Relationship to Other AINL Programs
- Smaller than the Proactive Monitor but uses similar patterns (cache state, adapter calls, queue notification).
- Serves as an accessible entry point for understanding AINL’s adapter model and graph flow.
- Could be extended to include `svc` checks; for example, skip digest if cloudflared tunnel is down.

## Conclusion
The Daily Digest example showcases AINL’s ability to concisely express multi‑adapter, time‑sensitive, stateful automations. It is an ideal “hello world” for OpenClaw agents that go beyond trivial transforms and interact with real user data (email, calendar, social). Its design highlights AINL’s strengths: adapter uniformity, WASM extensibility, and cron‑native scheduling.
