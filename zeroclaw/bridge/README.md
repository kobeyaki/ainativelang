# ZeroClaw bridge (`zeroclaw/bridge/`)

Parallel to **`openclaw/bridge/`**, this directory holds **ZeroClaw-specific** helpers: wrapper runner, cron drift check, daily memory append, token budget adapter, and a dispatcher CLI. They are **not** part of AINL canonical core.

## Differences vs OpenClaw bridge

| Topic | OpenClaw | ZeroClaw |
|--------|-----------|----------|
| Dispatcher | `openclaw/bridge/ainl_bridge_main.py` | `zeroclaw/bridge/zeroclaw_bridge_main.py` |
| Daily memory dir | `OPENCLAW_WORKSPACE/memory/` (or `OPENCLAW_MEMORY_DIR`) | `ZEROCLAW_WORKSPACE/memory/` (default `~/.zeroclaw/workspace/memory/`) |
| Memory adapter | `OpenClawMemoryAdapter` (`adapters/openclaw_memory.py`) | `ZeroclawMemoryAdapter` (this dir) — also registered as **`openclaw_memory`** so shared `.ainl` wrappers append under ZeroClaw paths |
| Notify queue | `openclaw message send` | `zeroclaw message send` (`ZeroclawQueueAdapter`; env `ZEROCLAW_NOTIFY_CHANNEL`, `ZEROCLAW_TARGET`) |
| Cron drift | `openclaw cron list --json` | `zeroclaw cron list --json` (`cron_drift_check.py`) |
| Token subprocess | `ainl_bridge_main.py token-usage` | `zeroclaw_bridge_main.py token-usage` |
| FS sandbox default | `AINL_FS_ROOT` / `~/.openclaw/workspace` | `ZEROCLAW_WORKSPACE` / `~/.zeroclaw/workspace` |

## Install wiring (`ainl install-zeroclaw`)

When run from a git checkout that contains `zeroclaw/bridge/zeroclaw_bridge_main.py`, the installer also:

1. Appends **`[ainl_bridge]`** with **`repo_root`** to **`~/.zeroclaw/config.toml`** (skipped if `[ainl_bridge]` already exists).
2. Installs **`~/.zeroclaw/bin/zeroclaw-ainl-run`**, a shim that `cd`s to `repo_root` and runs **`python3 zeroclaw/bridge/run_wrapper_ainl.py`**.

`~/.zeroclaw/bin/ainl-run` (compile+run `.ainl`) is unchanged.

## Usage

```bash
cd /path/to/AI_Native_Lang
python3 zeroclaw/bridge/zeroclaw_bridge_main.py run-wrapper supervisor --dry-run
python3 zeroclaw/bridge/zeroclaw_bridge_main.py token-usage --dry-run --json-output
python3 zeroclaw/bridge/zeroclaw_bridge_main.py drift-check --json
```

Or after install:

```bash
zeroclaw-ainl-run token-budget-alert --dry-run
```

## Execution model

`run_wrapper_ainl.py` embeds **`RuntimeEngine`** with a ZeroClaw-tuned registry (same pattern as OpenClaw). Bare **`ainl run`** does not load this registry; use this script or **`zeroclaw-ainl-run`**.

Optional: **`AINL_ZC_COMPILE_SUBPROCESS=1`** runs **`ainl compile &lt;wrapper&gt;`** in a subprocess before in-process execution (toolchain check).

## Environment variables

| Variable | Role |
|----------|------|
| `ZEROCLAW_WORKSPACE` | Base for `memory/` and default FS sandbox |
| `ZEROCLAW_MEMORY_DIR` / `ZEROCLAW_DAILY_MEMORY_DIR` | Override daily markdown directory |
| `ZEROCLAW_BIN` | `zeroclaw` CLI path |
| `ZEROCLAW_NOTIFY_CHANNEL`, `ZEROCLAW_TARGET` | Queue / notify adapter (falls back to `OPENCLAW_*` for target/channel) |
| `MONITOR_CACHE_JSON`, `AINL_DRY_RUN`, `AINL_ADVOCATE_DAILY_TOKEN_BUDGET` | Same semantics as OpenClaw bridge |
| `AINL_REPO_ROOT` | Set by `zeroclaw-ainl-run` shim |

## See also

- `docs/ZEROCLAW_INTEGRATION.md` — skill + MCP + bridge overview  
- `docs/operations/EXTERNAL_ORCHESTRATION_GUIDE.md` — orchestration + bridge pointers  
- `openclaw/bridge/README.md` — OpenClaw reference  
