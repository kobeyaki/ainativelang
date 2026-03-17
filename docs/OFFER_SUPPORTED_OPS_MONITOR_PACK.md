# Supported Ops Monitor Pack — Offer Draft

**Purpose:** Buyer-facing offer draft for the first Enterprise Governance deliverable (Supported ops monitor pack). Grounded in the locked open-core boundary and `docs/OPEN_CORE_FIRST_DELIVERABLES.md`. Not a contract; for website, sales, or proposal use after legal review.

---

## What the supported monitor pack is

A **curated set of AINL autonomous ops monitors** with a **supported bundle**: runbook, guaranteed updates, and support. The monitor programs themselves are the same AINL programs and runners available in the open repo (`examples/autonomous_ops/`, `demo/`, `scripts/run_*.py`). What you pay for is **packaging**, **runbook**, **updates**, and **support**—not the code. The pack is suitable for teams that want production-style monitoring (health checks, token/cost tracking, infrastructure watchdog, or meta-monitor) with a single place to get help and predictable updates.

---

## Who it is for

- Operators or platform teams running AINL-based monitors (or planning to) and wanting a supported, governance-ready option.
- Teams that want to consume the standardized health envelope and runner pattern with clear deployment and support expectations.

---

## Monitors likely in the first supported set

The first supported pack is expected to include a small set chosen from the monitors already implemented in the repo, for example:

- **Infrastructure watchdog** — Service health checks (e.g. caddy, cloudflared, maddy, CRM); auto-restart and alerts. Runner: `scripts/run_infrastructure_watchdog.py`.
- **Meta monitor** — Watchdog over the monitors themselves; alerts if any monitor is stale. Runner: `scripts/run_meta_monitor.py`.
- **Token cost tracker** — OpenRouter (or similar) token spending vs budget; daily/weekly view. Runner: `scripts/run_token_cost_tracker.py`.

Exact monitors and schedules are defined in the pack version and runbook. All use the **Standardized Health Envelope** (v1.0) for notifications and metrics. The full list of repo monitors is in `docs/operations/AUTONOMOUS_OPS_MONITORS.md`; the supported pack is a subset with runbook and support.

---

## What the customer gets

- **Supported monitor pack** — Designated AINL monitor programs and runner scripts (same as open repo), packaged with:
  - **Runbook** — Install, environment variables, cron/scheduler setup, how to consume the health envelope (e.g. queue, webhook, dashboard).
  - **Updates** — Guaranteed updates for the pack (e.g. quarterly or as specified) for compatibility and fixes within the supported set.
  - **Support** — Defined response times and channel for questions and issues related to the pack (per separate support terms).
- **Governance-ready usage** — Monitors and health envelope are documented so you can align with internal ops and compliance expectations (e.g. what runs, what is emitted, where it goes).

---

## What remains open

- The **AINL monitor source** (e.g. `examples/autonomous_ops/*.lang`, `demo/*.lang`) and **runner scripts** (`scripts/run_*.py`) remain part of the open project. You can run them yourself from the repo without buying the pack.
- The **Standardized Health Envelope** schema and monitor index docs (`docs/operations/AUTONOMOUS_OPS_MONITORS.md`, `docs/operations/STANDARDIZED_HEALTH_ENVELOPE.md`) stay open.
- The paid value is **runbook**, **packaging**, **updates**, and **support**—not exclusive access to the code.

---

## Paid value (what you are buying)

- **Runbook** — Single place for install, config, cron, and health-envelope consumption so your team can deploy and operate the pack without reverse-engineering.
- **Support** — Designated channel and response targets for pack-related issues (per agreement).
- **Updates** — Guaranteed updates for the supported set so you stay on a known-good, tested combination.
- **Packaging** — Versioned “supported pack” (programs + runbook + support) so you have a clear upgrade and support path.
- **Governance-ready** — Documented behavior and envelope so you can use the pack in environments that require clarity on what runs and what data is produced.

---

## Deployment assumptions

- You have (or will set up) an environment where the AINL runtime and dependencies can run (Python, access to required adapters, e.g. queue, memory, HTTP, or service checks as needed by the chosen monitors).
- You have (or will set up) a scheduler (e.g. cron, `openclaw cron add`, or similar) to run the monitor runners on the agreed schedule.
- You are responsible for securing secrets, network, and data in your environment; we do not operate your infrastructure.
- Exact requirements (e.g. memory backend, queue backend, env vars) are documented in the runbook for the pack.

---

## What is not included (yet)

- **Hosted execution** — We do not run the monitors in our cloud as part of this pack; you run them in your environment using the runbook.
- **Custom monitors** — The pack is a fixed supported set; custom or one-off monitors are out of scope unless agreed separately.
- **Premium connectors** — Deeper integrations (e.g. enterprise CRM, SSO, proprietary APIs) are not part of this offer; they may be offered later as separate, deep integrations (per our product boundary).
- **Pricing** — Not specified in this draft; to be agreed in a commercial agreement.

---

## Repo grounding (technical)

This offer is based on existing open assets:

- **Monitors:** `examples/autonomous_ops/*.lang`, `demo/*.lang`; `scripts/run_infrastructure_watchdog.py`, `scripts/run_meta_monitor.py`, `scripts/run_token_cost_tracker.py`, and other `scripts/run_*.py` runners
- **Docs:** `docs/operations/AUTONOMOUS_OPS_MONITORS.md`, `docs/operations/STANDARDIZED_HEALTH_ENVELOPE.md`, `openclaw/AUTONOMOUS_OPS_EXTENSION_IMPLEMENTATION.md`
- **Health envelope:** All monitors use the same queue payload shape (envelope version, module, status, ts, metrics, history_24h, meta)

We do not claim to provide monitors or infrastructure that do not exist; the offer is runbook, packaging, updates, and support around these programs.

---

## Proposal-ready summary

The Supported Ops Monitor Pack is a curated set of AINL autonomous ops monitors (e.g. infrastructure watchdog, meta monitor, token cost tracker) packaged with a runbook, guaranteed updates, and support. The monitor programs and runners are the same as in the open repo—you pay for runbook, packaging, updates, and support, not for exclusive code. You run the monitors in your environment (we do not host execution); the runbook covers install, environment variables, cron/scheduler setup, and how to consume the standardized health envelope. You get a single supported path, predictable updates, and documented behavior for governance and ops. Custom monitors and premium connectors are out of scope. Scope, terms, and pricing are agreed in a separate commercial agreement.

---

*Offer draft only. Terms, scope, and pricing are subject to a separate commercial agreement. Boundary: `docs/OPEN_CORE_DECISION_SHEET.md`; execution plan: `docs/OPEN_CORE_FIRST_DELIVERABLES.md`.*
