# Bridge token budget alert

**Hub doc:** [`docs/operations/UNIFIED_MONITORING_GUIDE.md`](../operations/UNIFIED_MONITORING_GUIDE.md) — architecture, cron payloads, sentinel, env vars, troubleshooting, and weekly trends.

**Where it writes (live):** OpenClaw daily markdown at **`~/.openclaw/workspace/memory/YYYY-MM-DD.md`** (override directory with `OPENCLAW_MEMORY_DIR` / `OPENCLAW_DAILY_MEMORY_DIR`).

Scheduled workflow: [`openclaw/bridge/wrappers/token_budget_alert.ainl`](../../openclaw/bridge/wrappers/token_budget_alert.ainl).

- Invoked with `python3 openclaw/bridge/run_wrapper_ainl.py token-budget-alert` (add `--dry-run` while testing).
- Uses `R bridge monitor_cache_stat`, `token_budget_warn`, `token_budget_report`, `token_budget_notify_*`, `monitor_cache_prune` (with `auto` days), and optional markdown helpers — see [`bridge_token_budget_adapter.py`](../../openclaw/bridge/bridge_token_budget_adapter.py). This replaces `R fs stat` on `/tmp/...` because the sandboxed `fs` adapter cannot read arbitrary paths under `/tmp`.
- **Production behavior (current):**
  - Appends **`## Token Usage Report`** (and related blocks) to today’s file; **live** runs use a **sentinel** (`token_report_today_sent` / `token_report_today_touch`, default file `/tmp/token_report_today_sent`) so the **main** report is not duplicated on repeated runs the same UTC day. **`AINL_TOKEN_REPORT_SENTINEL`** overrides the path. Dry-run skips sentinel and main append.
  - **One consolidated** `R queue Put` at the end (live only) when any notify lines were queued — first line is **`Daily AINL Status - <UTC from R core now>`**; body can combine critical cache, prune success, and/or budget warning. Budget line is included only when **`budget_warning`** and **`cache_ok`** (monitor cache **≤ 10 MB** by `monitor_cache_stat`).
  - If cache **> 12 MB**, runs **`monitor_cache_prune auto`** after the report path; markdown from prune success/failure is appended separately.
- **Weekly trends** (separate wrapper): [`weekly_token_trends.ainl`](../../openclaw/bridge/wrappers/weekly_token_trends.ainl) — documented in the hub above.
- Cron example: [`openclaw/bridge/README.md`](../../openclaw/bridge/README.md) → **Scheduled reporting & alerting**; registry discipline: [`docs/CRON_ORCHESTRATION.md`](../CRON_ORCHESTRATION.md).

## Activating notifications

1. **Dry-run first:** `python3 openclaw/bridge/run_wrapper_ainl.py token-budget-alert --dry-run` — stdout JSON has `"ok": true` and `"wrapper": "token-budget-alert"`; stderr should show `[dry_run] openclaw_memory.append_today` (no Telegram / `[Notification]`). The graph still runs so you can validate compile and branch logic; `R queue Put` is skipped when `dry_run` is set.
2. **Live test (no `--dry-run`):** Run once from a shell with `OPENCLAW_BIN`, `OPENCLAW_TARGET` / `OPENCLAW_NOTIFY_CHANNEL` set as for your other monitors. **One** consolidated `R queue Put` runs at the end when any notify lines were queued (critical cache, prune success, and/or budget warning). Budget text is only added when **budget_warning** is true **and** monitor cache file is **≤ 10 MB** (`cache_ok`). Oversized cache still appends a warning line to memory and skips the budget line in the consolidated message.
3. **Telegram verified:** After a controlled live run, add OpenClaw cron (see README) **without** `--dry-run` in the payload so `openclaw_memory.append_today` and `R queue Put` execute on schedule.

## Self-healing: cache pruning

When `MONITOR_CACHE_JSON` is larger than **12 MB** (by file size via `monitor_cache_stat`), the wrapper calls `R bridge monitor_cache_prune auto` after the token report is appended. **`auto`** resolves `days_old` from **`AINL_TOKEN_PRUNE_DAYS`** if set, otherwise **60** (see **Tuning** below).

- On success: entries with parseable timestamps older than `days_old` are removed; **markdown** from `monitor_cache_prune_markdown` is appended (not raw JSON).
- On failure: the adapter returns a dict with an **`error`** string (no exception); the wrapper appends `monitor_cache_prune_error_markdown` (includes **Would prune** in dry-run) and **does not** enqueue the prune-success notify line.

### Example: formatted prune block in memory (and in JSON `out` after a run)

Happy dry-run with a large cache (`AINL_BRIDGE_FAKE_CACHE_MB=16`):

```markdown
## Cache Prune
- Would prune stale entries (dry-run); no file changes
- Removed 0 old entries
- New size: 15.9520 MB
```

Simulated failure (`AINL_BRIDGE_PRUNE_FORCE_ERROR=1`):

```markdown
## Cache Prune
- Would prune stale entries (dry-run); no file changes
- Prune failed: simulated prune failure (AINL_BRIDGE_PRUNE_FORCE_ERROR)
```

After a **live** prune that removed 42 keys:

```markdown
## Cache Prune
- Removed 42 old entries
- New size: 3.2140 MB
```

## Tuning

| Variable | Purpose |
|----------|---------|
| `AINL_TOKEN_PRUNE_DAYS` | If set (integer ≥ 1), used as `days_old` for `monitor_cache_prune auto`. Otherwise the bridge default is **60**. |
| `AINL_BRIDGE_FAKE_CACHE_MB` | **Tests only:** float override for reported cache size (MB) so you can hit the >10 / >12 / >15 branches without a huge real file. |
| `AINL_BRIDGE_PRUNE_FORCE_ERROR` | **Tests only:** set to `1` / `true` / `yes` so `monitor_cache_prune` returns a synthetic **error** payload (no file I/O in dry-run). |
| `AINL_TOKEN_REPORT_SENTINEL` | Optional path for the duplicate-guard file (default `/tmp/token_report_today_sent`). |

### Example: consolidated live notify

If the cache is critically large, the prune removed keys, and the budget warns (with `cache_ok`), a single message might look like:

```text
Daily AINL Status - 2026-03-20 14:32:01 UTC
Cache critically large — consider manual prune
Pruned 12 old token-monitor cache entries — see today's memory for details.
Token budget warning: 85.0% used | Cache: 2.1 MB | See ~/.openclaw/workspace/memory/2026-03-20.md
```

The first line uses `R core now` (Unix seconds) formatted in UTC by `token_budget_notify_build`.

### Duplicate main report (live)

To avoid appending the full **Token Usage Report** twice on repeated manual runs the same UTC day, the bridge uses **`token_report_today_sent` / `token_report_today_touch`** on a small sentinel file (default `/tmp/token_report_today_sent` storing today’s `YYYY-MM-DD`). This is implemented in **`bridge_token_budget_adapter.py`** (not `R fs`) so `/tmp` works even when the sandboxed `fs` adapter cannot reach it. Override with **`AINL_TOKEN_REPORT_SENTINEL`**. Dry-run never writes the sentinel and never appends the main report.

Remove test env vars in production cron jobs.
