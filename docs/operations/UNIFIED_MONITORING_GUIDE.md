# Unified AINL + OpenClaw Monitoring Guide

**Audience:** operators running OpenClaw cron, AINL bridge wrappers, and daily markdown memory.

**Related:** [`openclaw/bridge/README.md`](../../openclaw/bridge/README.md) · [`docs/openclaw/BRIDGE_TOKEN_BUDGET_ALERT.md`](../openclaw/BRIDGE_TOKEN_BUDGET_ALERT.md) · [`docs/ainl_openclaw_unified_integration.md`](../ainl_openclaw_unified_integration.md) · [`docs/CRON_ORCHESTRATION.md`](../CRON_ORCHESTRATION.md) · [`docs/AINL_CANONICAL_CORE.md`](../AINL_CANONICAL_CORE.md) (bridge is *non-canonical* but production-critical)

---

## Architecture overview

```text
OpenClaw cron / manual shell
        │
        ▼
openclaw/bridge/run_wrapper_ainl.py  <─── registered wrapper name
        │
        ├─► RuntimeEngine (graph-preferred) + openclaw_monitor_registry()
        │
        ├─► openclaw_memory  ──►  ~/.openclaw/workspace/memory/YYYY-MM-DD.md
        ├─► bridge (BridgeTokenBudgetAdapter)  ──► token-usage JSON, cache stat/prune, notify queue
        ├─► queue (notify)     ──► Telegram / OpenClaw message (live only)
        └─► core (now, concat, X ops)  ──► timestamps, guards, math
```

- **Canonical AINL** (language, compiler, portable runtime) does **not** include this glue; see **`docs/AINL_CANONICAL_CORE.md`** § *OpenClaw Bridge Layer*.
- **All monitoring-specific file I/O for token reports** that must touch `/tmp` or arbitrary paths is implemented in **`openclaw/bridge/bridge_token_budget_adapter.py`**, not in the sandboxed `fs` adapter (which may not see `/tmp`).

---

## Memory file locations

| Artifact | Default path | Override |
|----------|--------------|----------|
| Daily OpenClaw markdown log | **`~/.openclaw/workspace/memory/YYYY-MM-DD.md`** | `OPENCLAW_MEMORY_DIR` or `OPENCLAW_DAILY_MEMORY_DIR` |
| Monitor / search cache JSON | `/tmp/monitor_state.json` | `MONITOR_CACHE_JSON` |

The `openclaw_memory` adapter appends under a dated filename; AINL bridge wrappers use the same resolution rules as `adapters/openclaw_memory.py`.

**Verify today’s file exists (live):**

```bash
ls -la ~/.openclaw/workspace/memory/$(date -u +%Y-%m-%d).md
```

---

## Daily token budget system

**Wrapper:** `openclaw/bridge/wrappers/token_budget_alert.ainl`  
**Runner name:** `token-budget-alert`  
**Declared schedule (documentation / drift):** `S core cron "0 23 * * *"` (23:00 UTC daily)

**What it does (high level):**

1. Resets an in-memory notify queue (`token_budget_notify_reset`).
2. Reads monitor cache size via **`R bridge monitor_cache_stat`** (file size of `MONITOR_CACHE_JSON`).
3. If cache **> 10 MB**: sets `cache_ok = 0`, appends a warning line to today’s memory, optionally queues a **critical cache** notify line (live).
4. Loads **`token_budget_report`** / **`token_budget_warn`** (subprocess `ainl_bridge_main.py token-usage --json-output`).
5. **Live only:** duplicate guard — if today’s sentinel says the main report was already appended, **skips** the main `## Token Usage Report` append (see **Sentinel duplicate guard**).
6. **Dry-run:** does **not** append the main token report and does **not** write the sentinel.
7. If cache **> 12 MB**: **`monitor_cache_prune auto`** (tunable `days_old` via env); appends prune markdown or error markdown; may queue prune-success notify (live, if count > 0).
8. **Consolidated notification (live):** one **`R queue Put "notify" …`** with header **`Daily AINL Status - <UTC timestamp from R core now>`** and joined lines (critical / prune / budget warning if eligible).

**Dry-run (safe):**

```bash
cd /path/to/AI_Native_Lang
python3 openclaw/bridge/run_wrapper_ainl.py token-budget-alert --dry-run
```

**JSON health check:** stdout includes `"ok": true`, `"wrapper": "token-budget-alert"`, and `"out"` with the markdown report (and prune section if branches ran). Stderr may show `[dry_run] openclaw_memory.append_today` for secondary appends still invoked on dry paths where the graph calls `append_today` (adapter no-ops the write).

Detail reference: **[`docs/openclaw/BRIDGE_TOKEN_BUDGET_ALERT.md`](../openclaw/BRIDGE_TOKEN_BUDGET_ALERT.md)**

---

## Weekly token trends

**Wrapper:** `openclaw/bridge/wrappers/weekly_token_trends.ainl`  
**Runner name:** `weekly-token-trends`  
**Declared schedule:** `S core cron "0 9 * * 0"` (Sunday 09:00 — self-documenting in source)

The **bridge** scans up to **14** recent `YYYY-MM-DD.md` files under the memory directory (newest first by filename), parses **`## Token Usage Report`** blocks for heuristic token totals / budget %, and emits a **`## Weekly Token Trends`** markdown block.

**Dry-run:**

```bash
python3 openclaw/bridge/run_wrapper_ainl.py weekly-token-trends --dry-run
```

**Live append** to today’s file: same command **without** `--dry-run`.

---

## Cron jobs (copy-paste)

Set `AINL_WORKSPACE` to your repo root (see [`openclaw/bridge/README.md`](../../openclaw/bridge/README.md)).

**Daily token budget (23:00 UTC):**

```bash
openclaw cron add \
  --name ainl-token-budget-alert \
  --cron "0 23 * * *" \
  --session-key "agent:default:ainl-advocate" \
  --message 'cd $AINL_WORKSPACE && python3 openclaw/bridge/run_wrapper_ainl.py token-budget-alert' \
  --description "AINL daily token usage, prune, consolidated notify"
```

**Weekly trends (Sunday 09:00):**

```bash
openclaw cron add \
  --name ainl-weekly-token-trends \
  --cron "0 9 * * 0" \
  --session-key "agent:default:ainl-advocate" \
  --message 'cd $AINL_WORKSPACE && python3 openclaw/bridge/run_wrapper_ainl.py weekly-token-trends' \
  --description "AINL weekly token trends markdown append"
```

Staging: add `--dry-run` **before** the wrapper name in the Python argv inside `--message` if you need zero writes (e.g. `'... run_wrapper_ainl.py token-budget-alert --dry-run'`).

Governance and drift: **`docs/CRON_ORCHESTRATION.md`**, **`python3 openclaw/bridge/cron_drift_check.py`**.

---

## Sentinel duplicate guard

**Purpose:** prevent the **full** daily **`## Token Usage Report`** block from being appended twice on repeated **live** manual runs the same **UTC calendar day**.

**Mechanism:**

- Bridge verbs **`token_report_today_sent`** / **`token_report_today_touch`** read/write a small file (default **`/tmp/token_report_today_sent`**) containing a single **`YYYY-MM-DD`** line (UTC).
- After a successful main report append, the wrapper marks the sentinel.
- **Dry-run** never writes the sentinel and never appends the main report.

**Override path:** `AINL_TOKEN_REPORT_SENTINEL`

**Reset for testing:**

```bash
rm -f /tmp/token_report_today_sent
# or delete your custom AINL_TOKEN_REPORT_SENTINEL path
```

---

## Environment variables reference

| Variable | Role |
|----------|------|
| `OPENCLAW_MEMORY_DIR` / `OPENCLAW_DAILY_MEMORY_DIR` | Daily markdown directory (default under `~/.openclaw/workspace/memory/`) |
| `OPENCLAW_WORKSPACE` | Default parent for `memory/` if memory dir not set |
| `MONITOR_CACHE_JSON` | Token monitor cache file path |
| `AINL_TOKEN_PRUNE_DAYS` | Prune age threshold when using `monitor_cache_prune auto` (else default **60** days) |
| `AINL_TOKEN_REPORT_SENTINEL` | Duplicate-guard file path |
| `AINL_DRY_RUN` / `--dry-run` on runner | Skip real `append_today` writes, queue sends, sentinel touch, live prune writes |
| `AINL_BRIDGE_FAKE_CACHE_MB` | **Test:** force reported cache size (MB) |
| `AINL_BRIDGE_PRUNE_FORCE_ERROR` | **Test:** simulate prune error |
| `OPENCLAW_TARGET`, `OPENCLAW_NOTIFY_CHANNEL` | Notify delivery (with `openclaw` CLI) |
| `AINL_ADVOCATE_DAILY_TOKEN_BUDGET` | Budget line in token-usage (see `token_usage_reporter.py` docs in bridge README) |

---

## Monitoring commands

```bash
# Daily wrapper — dry run (no writes / no queue)
python3 openclaw/bridge/run_wrapper_ainl.py token-budget-alert --dry-run

# Token usage only — JSON for scripts
python3 openclaw/bridge/ainl_bridge_main.py token-usage --dry-run --json-output

# Weekly trends — dry run
python3 openclaw/bridge/run_wrapper_ainl.py weekly-token-trends --dry-run

# Cron drift (read-only)
python3 openclaw/bridge/cron_drift_check.py
```

---

## Troubleshooting

| Symptom | Checks |
|---------|--------|
| No line in `~/.openclaw/workspace/memory/YYYY-MM-DD.md` | Run **without** `--dry-run`; confirm `OPENCLAW_MEMORY_DIR`; disk permissions. |
| Duplicate full reports same day | Expected **blocked** by sentinel; `rm` sentinel to force one more append; ensure cron uses same UTC day boundary. |
| No Telegram | `dry_run` must be false; `queue` Put only when notify queue non-empty; check `OPENCLAW_BIN` / env; oversized cache (>10 MB) drops **budget** line from notify but may still send critical/prune lines. |
| Prune never runs | Cache must be **> 12 MB** on `monitor_cache_stat`; check `MONITOR_CACHE_JSON` path and real file size. |
| `/tmp` issues | Bridge uses Python paths for sentinel and cache stat — not `R fs`. If `/tmp` is read-only, set `AINL_TOKEN_REPORT_SENTINEL` and `MONITOR_CACHE_JSON` to writable locations. |
| Weekly trends empty | Need `YYYY-MM-DD.md` files with `## Token Usage Report` in the memory dir. |

---

## Tuning thresholds

| Threshold | Where | Default / note |
|-----------|--------|----------------|
| Cache “too big” for budget notify | `token_budget_alert.ainl` | **> 10 MB** → `cache_ok = 0` |
| Critical cache notify | same | **> 15 MB** → extra notify line (live) |
| Auto prune | same | **> 12 MB** → `monitor_cache_prune auto` |
| Prune age | `AINL_TOKEN_PRUNE_DAYS` or bridge default | **60** days if env unset |

To change MB thresholds or cron times, edit **`openclaw/bridge/wrappers/token_budget_alert.ainl`** and keep **`tooling/cron_registry.json`** / OpenClaw jobs in sync (`docs/CRON_ORCHESTRATION.md`).

---

## Confirmation checklist

- [ ] Memory path understood: **`~/.openclaw/workspace/memory/YYYY-MM-DD.md`**
- [ ] Dry-run validated before enabling live cron
- [ ] Sentinel behavior understood for manual re-runs
- [ ] `cron_drift_check.py` run after schedule or payload changes

*End of Unified AINL + OpenClaw Monitoring Guide.*
