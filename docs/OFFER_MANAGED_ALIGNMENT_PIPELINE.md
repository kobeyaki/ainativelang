# Managed Alignment Pipeline — Offer Draft

**Purpose:** Buyer-facing offer draft for the first Managed Platform deliverable. Grounded in the locked open-core boundary and `docs/OPEN_CORE_FIRST_DELIVERABLES.md`. Not a contract; for website, sales, or proposal use after legal review.

---

## What it is

We run the **AINL model alignment pipeline** for you: supervision build, training (LoRA), checkpoint sweep, evaluation gate, and run-health reporting. You receive machine-readable run health and trend outcomes. The pipeline is the same one documented in the open repo (`scripts/run_alignment_cycle.sh`, `docs/TRAINING_ALIGNMENT_RUNBOOK.md`); the paid value is **we run it**, **we report outcomes**, and **we meet agreed response/SLA** for runs and results.

---

## Who it is for

- Teams that want to improve or maintain AINL generation quality (strict AINL rate, runtime compile rate, nonempty rate) without operating the full alignment cycle themselves.
- ML or platform teams that already use or plan to use the open AINL training/eval tooling and want a managed execution and reporting option.

---

## What the customer provides

- **Corpus and configuration:** Training/eval data (or access to it) and alignment parameters (e.g. epochs, gate thresholds, regression limits) as agreed in scope. May be supplied as repo reference, dataset path, or config file.
- **Execution environment (as applicable):** If runs are in the customer’s environment (e.g. VPC), access and permissions needed to run the pipeline; otherwise we define a single execution path (e.g. our environment with customer data under agreed terms).
- **Success criteria:** Definition of “pass” (e.g. minimum strict rate, runtime rate, nonempty rate; maximum regression vs prior run) so run health and deliverables are unambiguous.

---

## What we do

- Execute the alignment cycle using the open pipeline: supervision build, train, sweep checkpoints, run eval gate, compute trends and run health.
- Produce and deliver **run health** (machine-readable, e.g. `alignment_run_health.json`-style output) and a **trend summary** (e.g. strict/runtime/nonempty rates, regression vs previous run, pass/fail vs gates).
- Follow a documented runbook and handoff so runs are repeatable and supportable.
- Meet agreed **SLA** for run completion and delivery of outputs (exact targets to be defined in a separate agreement).

The underlying scripts and runbook are those in the open repository; we do not withhold the pipeline. The paid value is execution, reporting, and SLA.

---

## What outputs the customer receives

- **Run health report** — Machine-readable run health (pass/fail vs gates, key metrics).
- **Trend summary** — Rates and regression vs previous run (as produced by the open pipeline).
- **Deliverables package** — As agreed (e.g. run health JSON, trend summary, optional checkpoint/adapter artifacts per scope).
- **Runbook and handoff** — Documentation so the customer or their team can understand what was run and how to interpret results.

---

## In scope

- Running the alignment cycle (supervision build, train, sweep, eval gate, run health) as defined in the open runbook.
- Delivering run health and trend outputs in the agreed format and timeline.
- One execution path (customer VPC or our environment, as agreed).
- Documented process and runbook; SLA for run completion and delivery of outputs (per separate agreement).
- Support limited to run execution, runbook, and delivery of the above outputs.

---

## Out of scope (for this offer)

- **Custom pipeline logic** — We use the open pipeline; we do not build net-new alignment or training logic as part of this offering.
- **Full multi-tenant SaaS** — This is a defined “managed run” offering, not an open-ended platform.
- **Managed dashboard** — No aggregation UI, regression dashboard, or alerting product; only the run health and trend outputs as delivered. A dashboard may be offered later when we can deliver meaningful operational value (per our product boundary).
- **Data ownership / retention** — Governed by separate data and security terms.
- **Pricing** — Not specified in this draft; to be agreed in a commercial agreement.

---

## Why this is valuable

- **Reduces operator and ML ops load** — You get alignment quality signals and gate results without standing up and maintaining the full pipeline yourself.
- **Same pipeline as the open repo** — Transparent and auditable; no lock-in to proprietary training logic.
- **Clear outcomes** — Run health and trend summary give you a repeatable view of model quality and regression.
- **Defined SLA** — Agreed run completion and delivery so you can plan around results.

---

## Repo grounding (technical)

This offer is based on existing open assets:

- **Pipeline:** `scripts/run_alignment_cycle.sh`, `scripts/sweep_checkpoints.py`, `scripts/eval_finetuned_model.py`, `scripts/build_regression_supervision.py`
- **Runbook:** `docs/TRAINING_ALIGNMENT_RUNBOOK.md`, `docs/FINETUNE_GUIDE.md`
- **Run health:** `corpus/curated/alignment_run_health.json` (machine-readable gate output)
- **Trends:** Pipeline-produced trend and regression metrics (e.g. strict_ainl_rate, runtime_compile_rate, nonempty_rate; regression limits)

We do not claim to provide infrastructure or tooling that does not exist; the offer is execution, packaging, and SLA around this pipeline.

---

## Proposal-ready summary

We run the AINL model alignment pipeline for you—supervision build, training, checkpoint sweep, evaluation gate, and run-health reporting—using the same pipeline documented in the open repository. You provide corpus and configuration (and, if applicable, execution environment access); we execute the cycle and deliver machine-readable run health and trend outcomes (strict AINL rate, runtime compile rate, nonempty rate, regression vs prior run) with a documented runbook and agreed SLA for run completion and delivery. You get alignment quality signals and gate results without operating or maintaining the full pipeline yourself. The pipeline and runbook remain open; the paid value is execution, reporting, and SLA. Custom pipeline logic, full multi-tenant SaaS, and managed dashboard are out of scope. Scope, terms, and pricing are agreed in a separate commercial agreement.

---

*Offer draft only. Terms, scope, and pricing are subject to a separate commercial agreement. Boundary: `docs/OPEN_CORE_DECISION_SHEET.md`; execution plan: `docs/OPEN_CORE_FIRST_DELIVERABLES.md`.*
