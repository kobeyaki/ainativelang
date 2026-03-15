# Implementation Review / Onboarding — Offer Draft

**Purpose:** Buyer-facing offer draft for the first Expert Services deliverable (structured onboarding / implementation review). Grounded in the locked open-core boundary and `docs/OPEN_CORE_FIRST_DELIVERABLES.md`. Not a contract; for website, sales, or proposal use after legal review.

---

## What the engagement is

A **structured implementation review** of your use of AINL: we review your repo (or described setup), conformance to the language and runtime contract, adapter and ops patterns, and alignment with recommended practices. You receive a **short written report** and a **success plan** with concrete next steps. The review uses the same discipline and checklists we use internally (e.g. `docs/BOT_ONBOARDING.md`, `docs/OPENCLAW_IMPLEMENTATION_PREFLIGHT.md`, `docs/CONFORMANCE.md`, `docs/RELEASE_READINESS.md`). The paid value is **our time**, **structured process**, and **deliverables**—not access to closed documentation.

---

## Who it is for

- Teams that have adopted or are adopting AINL and want an expert pass to reduce risk and time-to-value.
- Operators or developers who want to confirm their use of adapters, memory, or ops patterns matches the documented contracts and best practices.
- Organizations that want a clear “we’ve been reviewed” artifact for internal or governance purposes.

---

## Inputs required from the customer

- **Repo or description** — Access to the repository (or a representative slice) that uses AINL, or a written description of your setup, programs, and how you run them (e.g. which adapters, which monitors, deployment pattern).
- **Scope** — What you want reviewed (e.g. conformance only; conformance + adapter usage; conformance + ops/monitor patterns). We will confirm scope before the engagement.
- **Point of contact** — One or two people for intake, 1–2 calls if needed, and delivery of the report.

---

## Process

1. **Intake** — We agree scope, inputs (repo access or description), and timeline. We may use a short questionnaire or call to clarify your goals.
2. **Review** — We inspect your repo/setup against conformance, adapter semantics, and implementation discipline (as in our preflight and conformance docs). We note strengths, gaps, and risks.
3. **Deliverables** — We produce a short **report** (written) and a **success plan** (prioritized next steps). Format and length are agreed in scope (e.g. 2–4 pages plus checklist).
4. **Handoff** — We deliver the report and, if agreed, a brief follow-up (e.g. one call or email thread) to walk through findings and recommendations.

Exact number of calls and turnaround are defined in the engagement letter or SOW.

---

## Outputs / deliverables

- **Implementation review report** — Written summary of: conformance status (e.g. strict vs compatible, key contracts), adapter and ops usage (correct use vs risks), and alignment with recommended practices (e.g. preflight, health envelope, capability metadata). Clear “in good shape” vs “should address” items.
- **Success plan** — Prioritized list of next steps (e.g. fix conformance gaps, adjust adapter usage, add validation, update runbook). Actionable and scoped so you can execute or plan follow-on work.
- **Optional** — One follow-up call or thread to discuss the report and plan (if included in scope).

We do not deliver code, patches, or ongoing support as part of the base engagement unless agreed separately.

---

## Success criteria

- You receive the agreed report and success plan by the agreed date.
- The report is grounded in the actual repo or description you provided and references specific files, patterns, or contracts where relevant.
- The success plan is concrete enough that you can assign and track next steps.
- Any scope agreed upfront (e.g. “include ops/monitor review” or “focus on conformance only”) is clearly covered in the deliverables.

---

## What is not included

- **Ongoing support** — This is a one-time (or defined-scope) engagement. SLA-backed support, ongoing questions, or incident response are not part of this offer unless agreed separately (e.g. as a support plan).
- **Certification** — We do not issue formal certification or credentials as part of this engagement. Certification may be offered later as a separate product (per our product boundary).
- **Implementation work** — We review and recommend; we do not implement fixes, new features, or deployment for you as part of the base engagement. Custom implementation can be scoped separately (e.g. consulting).
- **Pricing** — Not specified in this draft; to be agreed in a commercial agreement or SOW.

---

## Why this is valuable

- **Reduces risk** — Catch conformance issues, adapter misuse, or missing discipline before they cause production or maintenance problems.
- **Faster path to good practice** — Our checklists and contracts are public; the review applies them to your case and gives you a prioritized plan.
- **Clear artifact** — A written report and success plan you can use internally or for governance (“we had an implementation review”).
- **No lock-in** — All referenced docs and practices are open; you keep full control of your repo and roadmap.

---

## Repo grounding (technical)

This offer is based on existing open assets:

- **Onboarding and discipline:** `docs/BOT_ONBOARDING.md`, `docs/OPENCLAW_IMPLEMENTATION_PREFLIGHT.md`, `tooling/bot_bootstrap.json`
- **Conformance and release:** `docs/CONFORMANCE.md`, `docs/RELEASE_READINESS.md`, `docs/DOCS_INDEX.md`
- **Contact:** `COMMERCIAL.md` — “Open a GitHub issue/discussion requesting commercial contact.”

We do not rely on proprietary checklists; the value is our time and structured application of these open references to your setup.

---

## Proposal-ready summary

The Implementation Review is a structured engagement: we review your use of AINL (repo or described setup) against conformance, adapter semantics, and recommended practices (using the same open checklists we use internally), and deliver a short written report plus a prioritized success plan. You get concrete “in good shape” vs “should address” items and actionable next steps, reducing risk and time-to-value. All referenced docs and practices remain open; there is no lock-in. The engagement is one-time or defined-scope; ongoing support, certification, and implementation work are not included unless agreed separately. Scope, terms, and pricing are agreed in a separate commercial agreement or SOW.

---

*Offer draft only. Terms, scope, and pricing are subject to a separate commercial agreement or SOW. Boundary: `docs/OPEN_CORE_DECISION_SHEET.md`; execution plan: `docs/OPEN_CORE_FIRST_DELIVERABLES.md`.*
