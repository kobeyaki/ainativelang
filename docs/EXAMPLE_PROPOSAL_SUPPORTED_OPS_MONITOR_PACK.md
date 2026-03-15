# Example Proposal — Supported Ops Monitor Pack

**Purpose:** Filled example of how we would present the Supported Ops Monitor Pack offer to a prospective client. Uses a generic scenario; replace [Client Name] and tailor context for real use. Not a contract. Source: [OFFER_SUPPORTED_OPS_MONITOR_PACK.md](OFFER_SUPPORTED_OPS_MONITOR_PACK.md) and [PROPOSAL_TEMPLATE_COMMERCIAL_OFFERS.md](PROPOSAL_TEMPLATE_COMMERCIAL_OFFERS.md).

---

## Client / project

- **Client:** [Client Name]
- **Project:** Supported Ops Monitor Pack — [Project Name or e.g. “Internal infrastructure / workflow visibility”]
- **Selected offer:** Supported Ops Monitor Pack

---

## Summary

We propose the **Supported Ops Monitor Pack**: a curated set of AINL autonomous ops monitors (e.g. infrastructure watchdog, meta monitor, token cost tracker) packaged with a runbook, guaranteed updates, and support. The monitor programs and runners are the same as in the open AINL repository—you pay for runbook, packaging, updates, and support, not for exclusive code. You run the monitors in your own environment; we do not host execution. The runbook covers install, environment variables, cron/scheduler setup, and how to consume the standardized health envelope. You get a single supported path, predictable updates, and documented behavior for governance and ops. Scope, terms, and pricing will be set out in a separate commercial agreement.

---

## Client goals

- Deploy a supported set of AINL/OpenClaw-style operational monitors for internal infrastructure and workflow visibility.
- Have one place for runbook, support, and updates instead of reverse-engineering from the open repo alone.
- Use a standardized health envelope and runner pattern so outputs are consistent and governance-ready.
- Stay on a known-good, tested combination of monitors with a clear upgrade path.

---

## Current situation / context

[Client Name] wants to use AINL-based monitors for internal infrastructure checks, token/cost visibility, or similar operational workflows. The team prefers a supported bundle—runbook, updates, and a defined support channel—rather than running the open programs ad hoc without documentation or support. They are prepared to run the monitors in their own environment (scheduler, runtime, adapters) and need clear guidance on deployment and health-envelope consumption.

---

## Scope of work

- **Supported monitor pack** — Designated AINL monitor programs and runner scripts (same as in the open repo), packaged as a versioned supported set. The first pack is expected to include a small set such as: infrastructure watchdog, meta monitor, and token cost tracker (exact set and schedules defined in the pack version and runbook).
- **Runbook** — Single runbook covering: install, environment variables, cron/scheduler setup, and how to consume the standardized health envelope (e.g. queue, webhook, or downstream dashboard). Enough for your team to deploy and operate the pack without reverse-engineering.
- **Updates** — Guaranteed updates for the pack (e.g. quarterly or as specified in the agreement) for compatibility and fixes within the supported set.
- **Support** — Designated channel and response targets for questions and issues related to the pack (per separate support terms).
- **Governance-ready documentation** — Documented behavior and envelope so you can align with internal ops and compliance expectations (what runs, what is emitted, where it goes).

---

## Customer responsibilities / inputs

- **Environment** — You have (or will set up) an environment where the AINL runtime and dependencies can run (Python, access to required adapters such as queue, memory, HTTP, or service checks as needed by the chosen monitors).
- **Scheduler** — You have (or will set up) a scheduler (e.g. cron, or equivalent) to run the monitor runners on the agreed schedule.
- **Secrets, network, and data** — You are responsible for securing secrets, network, and data in your environment; we do not operate your infrastructure.
- **Point of contact** — Designate a point of contact for support and pack updates as agreed.

---

## Deliverables

- **Supported monitor pack** — Versioned bundle of the designated monitor programs and runner scripts (same as open repo), plus runbook and support entitlement.
- **Runbook** — Install, config, cron/scheduler setup, and health-envelope consumption (format and delivery as agreed, e.g. PDF or repo path).
- **Governance-ready documentation** — Description of what runs, what is emitted, and how the standardized health envelope is used, for internal ops and compliance use.
- **Updates** — Guaranteed updates for the supported set at the agreed cadence (e.g. quarterly).
- **Support** — Access to the designated support channel and response targets for pack-related issues (per separate support terms).

---

## What remains open / repo-grounded

The **AINL monitor source** (e.g. `examples/autonomous_ops/*.lang`, `demo/*.lang`) and **runner scripts** (`scripts/run_*.py`) remain part of the open AINL project. You can run them yourself from the repo without buying the pack. The **Standardized Health Envelope** schema and monitor index docs (`docs/AUTONOMOUS_OPS_MONITORS.md`, `docs/STANDARDIZED_HEALTH_ENVELOPE.md`) also stay open. The paid value of this offer is **runbook**, **packaging**, **guaranteed updates**, and **support**—not exclusive access to code. There is no lock-in; you keep full visibility into the open programs and schema.

---

## Out of scope

- **Hosted execution** — We do not run the monitors in our cloud as part of this pack; you run them in your environment using the runbook.
- **Custom monitors** — The pack is a fixed supported set; custom or one-off monitors are not included unless agreed separately.
- **Premium connectors** — Deeper integrations (e.g. enterprise CRM, SSO, proprietary APIs) are not part of this offer; they may be offered later as separate, deep integrations.
- **Pricing** — Not specified in this proposal; to be agreed in a separate commercial agreement.

---

## Assumptions / dependencies

- [Client Name] will provide an environment (or use an existing one) where the AINL runtime and required adapters can run, and will operate a scheduler to run the monitor runners.
- [Client Name] is responsible for securing secrets, network, and data; we do not operate or have access to the client’s infrastructure.
- The exact set of monitors in the pack and the update cadence will be confirmed in the commercial agreement (e.g. infrastructure watchdog, meta monitor, token cost tracker; quarterly updates).

---

## Timeline / phases

- **Phase 1 — Agreement and pack delivery:** Sign commercial agreement; we deliver the supported pack (programs, runbook, governance-ready docs) and support entitlement. [e.g. Upon signature or TBD]
- **Phase 2 — Deployment (client-led):** [Client Name] deploys the pack in their environment using the runbook (install, config, cron, health envelope). We provide support per the agreed terms. [e.g. Ongoing]
- **Phase 3 — Updates:** We deliver pack updates at the agreed cadence (e.g. quarterly); [Client Name] applies them in their environment. [e.g. Per agreement]

Exact dates and cadences will be confirmed in the commercial agreement.

---

## Commercial terms

**[Commercial terms / pricing handled separately]**

Scope, pricing, and legal terms for this engagement will be set out in a separate commercial agreement. This document describes the proposed scope and deliverables only.

---

## Acceptance / next steps

- [Client Name] confirms that this scope and these deliverables align with their goals (supported set of monitors, runbook, updates, support; execution in their environment).
- [Client Name] contacts us to finalize commercial terms and, if applicable, sign an agreement.
- Upon signed agreement, we will deliver the pack and runbook and activate support per the agreement.

---

*Example only. Not a contract. For the full offer and boundaries, see [OFFER_SUPPORTED_OPS_MONITOR_PACK.md](OFFER_SUPPORTED_OPS_MONITOR_PACK.md). For a blank template, see [PROPOSAL_TEMPLATE_COMMERCIAL_OFFERS.md](PROPOSAL_TEMPLATE_COMMERCIAL_OFFERS.md).*
