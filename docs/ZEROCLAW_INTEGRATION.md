# ZeroClaw integration

AINL ships a **ZeroClaw skill** (deterministic graphs, Markdown importer, **`ainl-mcp`**) and **`ainl install-zeroclaw`**, a user-side bootstrap that wires PyPI, **`~/.zeroclaw/mcp.json`**, and **`~/.zeroclaw/bin/ainl-run`** without changing the ZeroClaw application itself.

**Why this matters:** AINL is **compile-once, run-many**—you pay authoring or import cost once, then execute a validated graph repeatedly. Size economics use **tiktoken cl100k_base**; on the **viable subset** of representative workloads, **minimal_emit** lands near **~1.02×** leverage vs unstructured baselines (see **[`BENCHMARK.md`](../BENCHMARK.md)** and **[`benchmarks.md`](benchmarks.md)** for methodology and legacy-inclusive transparency).

### Install AINL as a ZeroClaw skill

```bash
zeroclaw skills install https://github.com/sbhooley/ainativelang/tree/main/skills/ainl
```

This installs the AINL importer, runtime shim, and MCP tools directly into ZeroClaw.

[![ZeroClaw Skill](https://img.shields.io/badge/ZeroClaw%20Skill-AINL-blue)](https://github.com/sbhooley/ainativelang/tree/main/skills/ainl)

## Quickstart

1. **Install the skill** from the **main repo path** (above) or, when published separately, the standalone repo:

   ```bash
   zeroclaw skills install https://github.com/sbhooley/ainl-zeroclaw-skill
   cd <skill-checkout> && ./install.sh
   ```

   Or **from a local clone of this monorepo**:

   ```bash
   cd skills/ainl && ./install.sh
   ```

2. **Or run the bootstrap directly**:

   ```bash
   pip install 'ainl-lang[benchmark,mcp]'
   ainl install-zeroclaw
   ```

   Preview only: `ainl install-zeroclaw --dry-run` · noisy logs: `--verbose`.

## Chat example

After a successful install, try:

> Import the morning briefing using AINL.

Then use **`ainl import markdown …`**, ecosystem shortcuts (**`ainl import clawflows`** / **`ainl import agency-agents`**), or MCP tools (**`ainl_list_ecosystem`**, **`ainl_import_clawflow`**, **`ainl_import_agency_agent`**, **`ainl_import_markdown`**) so the agent produces compiling **`.ainl`** source, followed by **`ainl compile`** / **`ainl run`** or **`~/.zeroclaw/bin/ainl-run my.ainl`**.

## What gets installed

| Artifact | Purpose |
|----------|---------|
| `pip install --upgrade 'ainl-lang[benchmark,mcp]'` | Latest compiler, importer extras, MCP dependencies |
| `~/.zeroclaw/mcp.json` | Merges an **`ainl`** stdio server entry pointing at **`ainl-mcp`** (skipped if already present with the same command) |
| `~/.zeroclaw/bin/ainl-run` | Shell wrapper: **`ainl compile "$1" && ainl run "$1"`** (plus extra args forwarded to **`ainl run`**) |
| `~/.bashrc` / `~/.zshrc` | Appends **`export PATH="$HOME/.zeroclaw/bin:$PATH"`** when those files exist and do not already mention **`~/.zeroclaw/bin`** |

If no shell rc file is updated, the command prints a one-line **`PATH`** tip you can paste manually.

## Ecosystem transparency (honest story)

- **Importer:** CLI **`ainl import markdown`**, **`ainl import clawflows`**, **`ainl import agency-agents`** share the same Markdown → graph path as the MCP tools above. When structure cannot be parsed, a **minimal_emit fallback stub** still yields compiling **`.ainl`** for review.
- **Checked-in samples:** **[`examples/ecosystem/`](../examples/ecosystem/)** holds **`original.md`**, **`converted.ainl`**, and per-folder READMEs; **weekly auto-sync** ( **[`.github/workflows/sync-ecosystem.yml`](../.github/workflows/sync-ecosystem.yml)** ) keeps them aligned with upstream public Markdown—see **[`ECOSYSTEM_OPENCLAW.md`](ECOSYSTEM_OPENCLAW.md)**.
- **Contributions:** submit new workflows or agents via **[`.github/PULL_REQUEST_TEMPLATE/`](../.github/PULL_REQUEST_TEMPLATE/)** (Clawflows-style workflow or Agency-Agents-style agent templates).

## Benefits (summary)

| Benefit | Notes |
|---------|--------|
| Deterministic graphs | Compile-time validation; explicit cron, steps, and branches vs prose-only prompts |
| One-command skill path | **ZeroClaw skill** + **`install.sh`** or **`ainl install-zeroclaw`** |
| MCP parity | Same import semantics as CLI; exposure profiles in **`tooling/mcp_exposure_profiles.json`** |
| Fresh ecosystem examples | Auto-sync + PR templates for community extensions |

## See also

- **OpenClaw parallel (skill + `ainl install-openclaw`):** **[`docs/OPENCLAW_INTEGRATION.md`](OPENCLAW_INTEGRATION.md)** · **[`skills/openclaw/README.md`](../skills/openclaw/README.md)**
- Skill manifest & usage: **[`skills/ainl/README.md`](../skills/ainl/README.md)**
- MCP operator guide: **[`docs/operations/EXTERNAL_ORCHESTRATION_GUIDE.md`](operations/EXTERNAL_ORCHESTRATION_GUIDE.md)** §9 (stdio **`ainl-mcp`**)
- Integration narrative: **[`docs/INTEGRATION_STORY.md`](INTEGRATION_STORY.md)**
- Ecosystem sync & OpenClaw- / ZeroClaw-oriented examples: **[`docs/ECOSYSTEM_OPENCLAW.md`](ECOSYSTEM_OPENCLAW.md)**
- Compile-once framing: **[`docs/architecture/COMPILE_ONCE_RUN_MANY.md`](architecture/COMPILE_ONCE_RUN_MANY.md)**
