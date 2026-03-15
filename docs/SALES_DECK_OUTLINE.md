# Sales Deck Outline — AINL Commercial Overview

**Purpose:** Concise deck outline for founder/client calls, lightweight sales presentations, investor or customer overviews, and future slide building. Based on the locked open-core boundary and the three current offers. **Markdown only for now; can be converted into slides later.** No pricing, no legal claims, no new strategy.

**Sources:** [SERVICES_PAGE_DRAFT.md](SERVICES_PAGE_DRAFT.md) · [OFFER_COMPARISON.md](OFFER_COMPARISON.md) · [DISCOVERY_CALL_CHECKLIST.md](DISCOVERY_CALL_CHECKLIST.md) · individual offer drafts.

---

## 1. Title slide

- **Headline:** AINL is the open language for agent workflows.
- **Subheadline:** We sell the operational layer: governance, visibility, managed execution, deployment help, and support. The language, compiler, runtime, and core tooling stay open.

---

## 2. Problem slide

- Agent workflows become **chaotic** — ad hoc prompts, one-off scripts, no single contract.
- **Hard to govern** — unclear what runs, what is emitted, who owns quality and safety.
- **Hard to validate** — no standard way to check conformance, regression, or gate results.
- **Hard to run repeatedly** without operational burden — alignment pipelines, monitors, and runbooks require someone to build and maintain them.

---

## 3. Open-core positioning slide

- **AINL** = open language and runtime for agent workflows (APIs, cron jobs, monitors, automations).
- **Core stays open:** language spec, compiler, runtime, and core tooling remain in the open repo; you can use and extend AINL without buying from us.
- **Commercial value** is in the **operational layer:** governance, visibility, managed execution, deployment help, and support. You pay for how we run it, package it, and help you adopt it—not for exclusive access to the code.

---

## 4. Offer slides

### Managed Alignment Pipeline

- **What it is:** We run the AINL alignment pipeline for you (supervision build, train, sweep, eval gate, run health) and deliver run health and trend outputs.
- **Who it’s for:** ML or platform teams that want generation quality (strict/runtime/nonempty rates) without operating the full pipeline themselves.
- **What the customer gets:** Run health report, trend summary, deliverables package, runbook and handoff; agreed SLA for run completion and delivery.
- **Why it matters:** Reduces operator and ML ops load; clear gate results and regression signals; pipeline and runbook stay open—paid value is execution, reporting, and SLA.

---

### Supported Ops Monitor Pack

- **What it is:** Curated set of AINL ops monitors (e.g. infrastructure watchdog, meta monitor, token cost tracker) packaged with runbook, guaranteed updates, and support. Customer runs them in their environment.
- **Who it’s for:** Operators or platform teams running (or planning) AINL-based monitors and wanting a supported, governance-ready option.
- **What the customer gets:** Supported pack (programs + runbook + updates + support); governance-ready docs; runbook covers install, config, cron, health envelope consumption.
- **Why it matters:** Single place for runbook and support; no reverse-engineering; monitor source and runners stay open—paid value is runbook, packaging, updates, support.

---

### Implementation Review / Onboarding

- **What it is:** Structured review of your AINL use (conformance, adapter usage, ops patterns); written report and success plan with concrete next steps.
- **Who it’s for:** Teams adopting AINL that want an expert pass to reduce risk and time-to-value, or a “we’ve been reviewed” artifact for governance.
- **What the customer gets:** Implementation review report and success plan; optional follow-up call as agreed in scope.
- **Why it matters:** Catches conformance issues and adapter misuse before production; clear artifact and prioritized next steps; all checklists and conformance docs stay open—paid value is our time and structured application.

---

## 5. Why us / why now slide

- **Compile-once, run-many** — AINL programs compile to a portable IR; same program can run in different environments with clear contracts.
- **Deterministic execution** — Runtime and adapter contracts support repeatable, auditable behavior.
- **Governance and safety surfaces** — Conformance, capability metadata, policy validation, and health envelope are designed in; docs and tooling support adoption.
- **Monitor and reference assets exist** — Ops monitors, alignment pipeline, runbooks, and health envelope are implemented in the repo; commercial offers package and support them.
- **Docs and process support adoption** — Preflight checklists, conformance docs, training runbook, and release readiness give teams a path from evaluation to production.

---

## 6. Engagement model slide

- **Start with Implementation Review** when scope is unclear or the prospect is new to AINL—defined scope, report + success plan, no long-term commitment.
- **Move into Supported Ops Monitor Pack** when they want supported monitors and will run them in their own environment.
- **Move into Managed Alignment Pipeline** when they want us to run the alignment cycle and deliver run health and trend outputs.
- **Proposals, pricing, and terms** are handled in a separate commercial agreement; this deck describes what we offer, not legal or pricing terms.

---

## 7. Close / CTA slide

- **How to engage:** Contact for a scoping conversation—GitHub issue/discussion requesting commercial contact, or existing channel.
- **First conversation:** Clarify goals, current situation, and which offer (or sequence) fits; use discovery checklist to triage and capture inputs.
- **What happens next:** Proposal and commercial terms in a separate agreement; kickoff per agreed scope (e.g. Implementation Review first, then pack or pipeline as needed).

---

*Deck outline only. For full offer details and boundaries, see [OFFER_COMPARISON.md](OFFER_COMPARISON.md) and the individual offer drafts. For discovery and triage, see [DISCOVERY_CALL_CHECKLIST.md](DISCOVERY_CALL_CHECKLIST.md).*
