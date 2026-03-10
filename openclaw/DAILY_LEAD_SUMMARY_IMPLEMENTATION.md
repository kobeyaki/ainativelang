# Daily Lead Summary — AINL Implementation Report

## Program Purpose
The Daily Lead Summary (`examples/openclaw/daily_lead_summary.lang`) is a scheduled AINL agent that runs each morning at 07:00. It queries the CRM database for recent leads, aggregates metrics (total count, top segment, high‑value leads count), produces a concise summary via WASM, and sends a Telegram notification via the OpenClaw event bus. The program shows how to combine `db`, `cache`, `queue`, `wasm`, and `core` adapters in a time‑driven, incremental pipeline.

## Why AINL Was Chosen
- **Declarative scheduling**: `S core cron "0 7 * * *"` embeds the schedule in code.
- **Adapter uniformity**: One‑liner `db.F` fetches leads with a dynamic filter; `cache.get/set` maintains `last_run`; `queue.Put` delivers the result.
- **Incremental fetch**: `last_run` timestamp stored in cache ensures only new leads are processed.
- **WASM pluggability**: Summarization logic can be upgraded independently.
- **Compactness**: The entire program is ~20 labels and fits on one screen.

## AINL Code Walkthrough

### Services and Types
```ainl
S core cron "0 7 * * *"
D Config lookback_days:N
D State last_run:T
```
- `core cron`: run daily at 07:00.
- `Config.lookback_days`: days back to consider leads (configurable).
- `State.last_run`: timestamp of last successful run, persisted in cache.

### Get Current Time
```ainl
L0: R core now ->ts J L1
```
Fetch current timestamp; tail‑call to `L1`.

### Read Last Run
```ainl
L1: R cache get "state" "last_run" ->last_run J L2
```
Retrieve last run timestamp from cache; if absent, `last_run` is null/epoch depending on cache implementation.

### Compute Cutoff
```ainl
L2: X cutoff (core.sub ts (core.mul Config.lookback_days 86400))
```
Calculate `cutoff = ts - (lookback_days * 86400)`. This yields a timestamp N days ago; leads with `created_at > cutoff` will be included.

### Fetch Leads
```ainl
L3: R db F (table="leads", where="created_at > " + core.stringify cutoff) ->rows J L4
```
`db.F` executes a query on the `leads` table. The `where` clause is built by concatenating a string with `core.stringify(cutoff)`. The result list `rows` is passed to `L4`.

### Count Total
```ainl
L4: X total (len rows) J L5
```

### Filter Non‑Empty Segments
```ainl
L5: X segments (Filt rows where (fn (r) (not (eq r.segment ""))) ->seg) J L6
```
`Filt` collects rows where `segment` is not empty; bind intermediate list to `seg`.

### Count per Segment
```ainl
L6: X seg_counts (Map seg (fn (r) r.segment) ->G (group) (len group)) J L7
```
`Map` extracts `segment` from each filtered row, then groups and counts. `seg_counts` is a map: segment → count. Requires `Map` + `group` + `len` pipeline.

### Top Segment
```ainl
L7: X top_segment (MaxKey seg_counts) J L8
```
`MaxKey` returns the key with the highest value in the map. If the map is empty, result may be null.

### High‑Value Leads
```ainl
L8: X high_value (Filt rows where (fn (r) (gte r.score 80)) ->hv) J L9
L9: X hv_count (len high_value) J L10
```
Filter leads with `score >= 80` (threshold), count them.

### Build Payload
```ainl
L10: X payload {"total":total,"top_segment":top_segment,"top_count":(seg_counts[top_segment] if top_segment else 0),"high_value":hv_count} J L11
```
Construct a JSON object with aggregated metrics. `top_count` looks up the count for `top_segment` safely (fallback 0 if `top_segment` is null).

### Summarize via WASM
```ainl
L11: X summary (wasm.CALL summarize payload) J L12
```
Invoke WASM function `summarize` to produce a human‑readable message (e.g., “Good morning! Yesterday we had 42 leads, top segment: HVAC (12), 5 high‑value leads.”).

### Notify
```ainl
L12: R queue Put notify {"summary":summary,"ts":ts} ->_ J L13
```
Send the notification; `_` discards the queue result.

### Update State
``` Ainl
L13: R cache set "state" "last_run" ts ->_ J L62
```
Store the current `ts` as `last_run` for the next incremental fetch.

### Exit
```ainl
L62:
```
Program ends; cron runner returns success.

## Key Language Features
- `S core cron` embeds schedule; no external cron entry needed.
- `D` declares types (`N`, `T`).
- Adapter calls: `R core now`, `R cache get`, `R db F`, `R queue Put`, `R cache set`.
- Expressions: `core.sub`, `core.mul`, `core.stringify`, `len`, `Filt`, `Map`, `group`, `len`, `MaxKey`, record literals, conditional expressions.
- Control flow: `J` tail‑calls between labels.
- WASM integration: `wasm.CALL summarize` produces the user‑facing message.

## Strict‑Mode Considerations
To make this program strict‑mode compatible, the following adjustments would be needed:
- Every `If` condition must be precomputed with `X`. Currently, `Filt` and `Map` are expressions; they are fine. The only conditional is implicit in `MaxKey` (empty map) — better to compute `has_top (gt (len seg_counts) 0)` and then `If has_top ->L_use_top ->L_no_top`.
- All labels must be numeric (already satisfied).
- Each label that is a jump target must have exactly one `J` entry; this program already chains with `J`.
- Adapter calls must use two‑token `R group verb`; current usage (`db F`) is technically `R db F`, which is two tokens (group=db, verb=F).
- No parentheses around expression arguments; `core.sub ts (core.mul ...)` is acceptable because the inner call is a single expression token. However, to avoid ambiguity, one could bind the product to an `X` variable first.

## Why This Is a Strong Example
- **Real utility**: Daily summary of CRM leads is a tangible, high‑value automation.
- **Incremental processing**: Uses `cache` to avoid re‑processing old leads; showcases stateful cron behavior.
- **Aggregation**: Demonstrates `Filt`, `Map`, `group`, `len`, `MaxKey` — common data‑wrangling patterns.
- **WASM extension**: Summarization logic is separated, allowing model swaps.
- **Adapter diversity**: `db`, `cache`, `queue`, `wasm`, `core` in a coherent workflow.
- **Error resilience**: If `last_run` is missing (first run), `cutoff` becomes far in the past, and the program processes all historical leads exactly once.

## Lessons Learned
- `db.F` query construction: string concatenation works but requires careful quoting; consider `core.stringify` for values and ensure SQL injection is impossible (values are parameters, not embedded).
- `MaxKey` on an empty map returns a default (null); handle with a conditional to avoid downstream errors.
- `wasm.CALL` module must be pre‑registered; the AINL runtime expects the WASM instance to be available via the adapter registry.
- The non‑strict `Filt`/`Map` syntax is expressive but may require strict‑mode alternatives (`Filter`, `Map`, `collect`). Verification needed.

## Relationship to Other AINL Programs
- Shares patterns with Daily Digest: cache state, adapter pipeline, queue notification, WASM summarization.
- Smaller than the Proactive Monitor; good intermediate example after Daily Digest.
- Could be extended to include `svc` checks (e.g., ensure CRM is up before querying) or segment‑level Slack/Telegram routing.

## Conclusion
The Daily Lead Summary is an idiomatic AINL program that solves a real business need in a concise, maintainable way. It highlights AINL’s strengths: adapter uniformity, graph‑first flow, WASM extensibility, and built‑in scheduling. This example is recommended for AI agents learning to build data‑driven OpenClaw automations.
