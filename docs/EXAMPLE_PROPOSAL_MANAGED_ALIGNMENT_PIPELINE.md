# Example Proposal — Managed Alignment Pipeline

**Purpose:** Filled example of how we would present the Managed Alignment Pipeline offer to a prospective client. Uses a generic scenario; replace [Client Name] and tailor context for real use. Not a contract. Source: [OFFER_MANAGED_ALIGNMENT_PIPELINE.md](OFFER_MANAGED_ALIGNMENT_PIPELINE.md) and [PROPOSAL_TEMPLATE_COMMERCIAL_OFFERS.md](PROPOSAL_TEMPLATE_COMMERCIAL_OFFERS.md).

---

## Client / project

- **Client:** [Client Name]
- **Project:** Managed Alignment Pipeline — [Project Name or e.g. “AINL model alignment and evaluation”]
- **Selected offer:** Managed Alignment Pipeline

---

## Summary

We propose to run the **AINL model alignment pipeline** for [Client Name]: supervision build, training (LoRA), checkpoint sweep, evaluation gate, and run-health reporting, using the same pipeline documented in the open repository. You provide corpus and configuration (and, if applicable, execution environment access); we execute the cycle and deliver machine-readable run health and trend outcomes (strict AINL rate, runtime compile rate, nonempty rate, regression vs prior run) with a documented runbook and agreed SLA for run completion and delivery. You get alignment quality signals and gate results without operating or maintaining the full pipeline yourself. The pipeline and runbook remain open; the paid value is execution, reporting, and SLA. Scope, terms, and pricing will be set out in a separate commercial agreement.

---

## Client goals

- Improve or maintain AINL generation quality (strict AINL rate, runtime compile rate, nonempty rate) without operating the full alignment cycle in-house.
- Receive run health and trend outputs in a defined format and timeline so you can act on gate results and regression signals.
- Have a single execution path (your VPC or ours, as agreed) with documented process and agreed SLA for run completion and delivery.
- Reduce ML ops and operator load while keeping the pipeline transparent and auditable (same pipeline as the open repo).

---

## Current situation / context

[Client Name] uses or plans to use the open AINL training and evaluation tooling and wants a managed execution and reporting option. The team prefers that we run the alignment cycle and deliver run health and trend outputs rather than standing up and maintaining the full pipeline themselves. They are prepared to supply corpus and configuration (and, if applicable, execution environment access) and want clear success criteria and deliverables.

---

## Scope of work

- **Execute the alignment cycle** — Using the open pipeline: supervision build, train (LoRA), sweep checkpoints, run eval gate, compute trends and run health. One execution path (customer VPC or our environment, as agreed in the commercial agreement).
- **Produce and deliver outputs** — **Run health** (machine-readable, e.g. `alignment_run_health.json`-style) and **trend summary** (strict/runtime/nonempty rates, regression vs previous run, pass/fail vs gates). Format and delivery mechanism as agreed (e.g. artifact package, secure transfer).
- **Runbook and handoff** — Documented process so runs are repeatable and supportable; you (or your team) can understand what was run and how to interpret results.
- **SLA** — Agreed targets for run completion and delivery of outputs (exact targets to be defined in the separate commercial agreement).
- **Support** — Limited to run execution, runbook, and delivery of the above outputs (per agreement); data ownership and retention governed by separate data/security terms.

---

## Customer responsibilities / inputs

- **Corpus and configuration** — Training/eval data (or access to it) and alignment parameters (e.g. epochs, gate thresholds, regression limits) as agreed in scope. May be supplied as repo reference, dataset path, or config file.
- **Execution environment (as applicable)** — If runs are in your environment (e.g. VPC), access and permissions needed to run the pipeline; otherwise we define a single execution path (e.g. our environment with your data under agreed terms).
- **Success criteria** — Definition of “pass” (e.g. minimum strict rate, runtime rate, nonempty rate; maximum regression vs prior run) so run health and deliverables are unambiguous.
- **Point of contact** — Designate a point of contact for intake, config handoff, and delivery of outputs.

---

## Deliverables

- **Run health report** — Machine-readable run health (pass/fail vs gates, key metrics) in the agreed format (e.g. `alignment_run_health.json`-style).
- **Trend summary** — Rates and regression vs previous run (as produced by the open pipeline): strict_ainl_rate, runtime_compile_rate, nonempty_rate; regression limits and pass/fail vs gates.
- **Deliverables package** — As agreed (e.g. run health JSON, trend summary, optional checkpoint/adapter artifacts per scope).
- **Runbook and handoff** — Documentation so you can understand what was run and how to interpret results; support for run execution and delivery per the agreement.

---

## What remains open / repo-grounded

The **alignment pipeline** (e.g. `scripts/run_alignment_cycle.sh`, `scripts/sweep_checkpoints.py`, `scripts/eval_finetuned_model.py`, `scripts/build_regression_supervision.py`) and **runbook** (`docs/TRAINING_ALIGNMENT_RUNBOOK.md`, `docs/FINETUNE_GUIDE.md`) remain part of the open AINL repository. You can run the pipeline yourself from the repo. The paid value of this offer is **we run it**, **we report outcomes**, and **we meet agreed SLA** for runs and results—not exclusive access to the pipeline. There is no lock-in to proprietary training logic.

---

## Out of scope

- **Custom pipeline logic** — We use the open pipeline; we do not build net-new alignment or training logic as part of this offering.
- **Full multi-tenant SaaS** — This is a defined “managed run” offering, not an open-ended platform.
- **Managed dashboard** — No aggregation UI, regression dashboard, or alerting product; only the run health and trend outputs as delivered. A dashboard may be offered later when we can deliver meaningful operational value (per our product boundary).
- **Data ownership / retention** — Governed by separate data and security terms.
- **Pricing** — Not specified in this proposal; to be agreed in a separate commercial agreement.

---

## Assumptions / dependencies

- [Client Name] will supply corpus and configuration (or access) and success criteria in the format and timeline agreed for intake.
- Execution path (customer VPC or our environment) will be confirmed in the commercial agreement; access and permissions will be provided as needed for that path.
- The exact SLA targets (run completion, delivery of outputs) will be defined in the separate commercial agreement.

---

## Timeline / phases

- **Phase 1 — Intake and scope confirmation:** Agree corpus/config, success criteria, execution path, and SLA. [e.g. Upon signature or TBD]
- **Phase 2 — Execution:** We run the alignment cycle (supervision build, train, sweep, eval gate, run health) and produce run health and trend outputs. [e.g. Per agreed schedule]
- **Phase 3 — Delivery and handoff:** We deliver the run health report, trend summary, and deliverables package per the agreement; runbook and handoff documentation provided. [e.g. Per agreement]

Exact dates and run cadence will be confirmed in the commercial agreement.

---

## Commercial terms

**[Commercial terms / pricing handled separately]**

Scope, pricing, and legal terms for this engagement will be set out in a separate commercial agreement (or SOW). This document describes the proposed scope and deliverables only.

---

## Acceptance / next steps

- [Client Name] confirms that this scope and these deliverables align with their goals (managed execution of the alignment cycle; run health and trend outputs; runbook and SLA).
- [Client Name] contacts us to finalize commercial terms and, if applicable, sign an agreement.
- Upon signed agreement, we will confirm kickoff date, intake details (corpus/config, success criteria, execution path), and first run timeline.

---

*Example only. Not a contract. For the full offer and boundaries, see [OFFER_MANAGED_ALIGNMENT_PIPELINE.md](OFFER_MANAGED_ALIGNMENT_PIPELINE.md). For a blank template, see [PROPOSAL_TEMPLATE_COMMERCIAL_OFFERS.md](PROPOSAL_TEMPLATE_COMMERCIAL_OFFERS.md).*
