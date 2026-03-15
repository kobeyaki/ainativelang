# Services Page Draft — AINL Commercial Offerings

**Purpose:** Public-facing, business-readable copy for a website services page or landing page. Based on the existing commercial offer docs and locked open-core boundary. Suitable for website use or for adapting into README/COMMERCIAL snippets. Not a contract; scope, terms, and pricing are defined in separate commercial agreements.

---

## 1. Headline / positioning

**AINL is the open language for agent workflows.**

We sell the **operational layer**: governance, visibility, managed execution, deployment help, and support. The language, compiler, runtime, and core tooling stay open; you pay for how we run it, package it, and help you adopt it.

---

## 2. Short intro

**Open core.**  
AINL (AI Native Lang) is an open language and runtime for describing agent workflows—APIs, cron jobs, monitors, and automations. The specification, compiler, runtime, and core tooling are open and available under the licenses declared in this repository. You can build, run, and extend AINL without buying anything from us.

**Commercial layer.**  
Separate from the open core, we offer **services and support**: we run the alignment pipeline for you, package supported ops monitors with runbooks and updates, and provide structured implementation reviews and onboarding. Scope, terms, and pricing for any of these are set out in a separate commercial agreement—not in the open licenses. You get defined deliverables, SLAs where applicable, and a single place to get help; the underlying code and docs stay open and auditable.

---

## 3. Services / offers

### Managed Alignment Pipeline

**Who it’s for:** ML or platform teams that want AINL generation quality (strict rate, runtime compile rate, nonempty rate) without operating the full alignment cycle themselves.

**What it helps with:** Reduces operator and ML ops load. You get alignment quality signals and gate results (run health, trend summary, regression vs prior run) without standing up and maintaining the pipeline.

**What you get:** We run the alignment cycle (supervision build, train, sweep, eval gate, run health) and deliver machine-readable run health and trend outputs with a documented runbook and agreed SLA for run completion and delivery.

**What stays open:** The alignment pipeline, scripts, and runbook remain in the open repo. The paid value is **execution**, **reporting**, and **SLA**—not exclusive access to the code.

---

### Supported Ops Monitor Pack

**Who it’s for:** Operators or platform teams running (or planning) AINL-based monitors and wanting a supported, governance-ready option.

**What it helps with:** One place for runbook, support, and updates. You can deploy and operate production-style monitors (e.g. infrastructure watchdog, meta monitor, token cost tracker) without reverse-engineering; you get governance-ready documentation for what runs and what is emitted.

**What you get:** A curated set of AINL monitors packaged with a runbook (install, config, cron, health envelope consumption), guaranteed updates, and support. You run the monitors in your environment; we do not host execution.

**What stays open:** Monitor source and runner scripts stay open. The health envelope schema and monitor docs stay open. The paid value is **runbook**, **packaging**, **updates**, and **support**—not exclusive access to the code.

---

### Implementation Review / Onboarding

**Who it’s for:** Teams adopting AINL that want an expert pass to reduce risk and time-to-value, or that want a clear “we’ve been reviewed” artifact for governance.

**What it helps with:** Catches conformance issues, adapter misuse, or missing discipline before production. Gives you a prioritized success plan and a written report you can use internally.

**What you get:** A structured review of your AINL use (conformance, adapter usage, ops patterns) and a short written report plus success plan with concrete next steps. Optional follow-up call as agreed in scope.

**What stays open:** All checklists and conformance docs we use are open. The paid value is **our time** and **structured application** to your setup—not access to closed documentation.

---

## 4. Why teams buy this

- **Less operator labor** — Get alignment signals, gate results, or supported monitors without building and maintaining everything yourself.
- **Governance and auditability** — Same pipeline, same monitors, same docs as the open repo; you get runbooks, deliverables, and documented behavior so you can show what runs and what is produced.
- **Faster adoption with less chaos** — Implementation review surfaces gaps early; supported pack and managed pipeline give you a clear path and one place for support.
- **Defined deliverables and support** — Run health and trend outputs, runbooks, reports, and success plans with agreed scope; support and SLA where applicable, per separate agreement.

---

## 5. Open core clarity

- **Spec, compiler, runtime, and core tooling remain open.** You can use, modify, and run AINL from the repository without any commercial relationship with us.
- **Paid value is in:** managed execution (we run the alignment cycle); governance packaging (supported monitor pack with runbook, updates, support); deployment and operations help (runbooks, handoffs); and expert support (implementation review, success plan, and—where agreed—support channel and SLA).
- We do not lock the pipeline, monitors, or documentation behind a paywall. You pay for how we run, package, and support them—not for exclusive access to the code.

---

## 6. Engagement / next steps

- **Contact for scoping** — If you’re interested in managed alignment, supported monitors, or an implementation review, get in touch so we can scope fit and deliverables. Open a GitHub issue or discussion requesting commercial contact, or use the channel you already have with us.
- **Proposals, terms, and pricing** are handled in a separate commercial agreement. This page and the offer drafts describe what we offer, not legal or pricing terms.
- **Implementation review** is often a good first engagement: defined scope, clear deliverables (report + success plan), and no long-term commitment. From there we can discuss supported monitors or managed alignment if they fit your needs.

---

*Draft for website/services use. For full offer details and boundaries, see [OFFER_COMPARISON.md](OFFER_COMPARISON.md) and the individual offer drafts. For commercial overview and contact, see [COMMERCIAL.md](../COMMERCIAL.md) in the repo root.*
