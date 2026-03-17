# Offer Comparison — First Commercial Deliverables

**Purpose:** Side-by-side comparison of the three first commercial offers for proposals and buyer conversations. Source: the individual offer drafts. Scope, terms, and pricing are always handled in a separate commercial agreement.

---

| | **Managed Alignment Pipeline** | **Supported Ops Monitor Pack** | **Implementation Review / Onboarding** |
|---|--------------------------------|--------------------------------|----------------------------------------|
| **Offer** | We run the AINL alignment cycle for you; you receive run health and trend outputs with agreed SLA. | Curated AINL monitors with runbook, guaranteed updates, and support. You run them in your environment. | Structured review of your AINL use; written report and success plan. |
| **Who it is for** | Teams that want AINL generation quality (strict/runtime/nonempty rates) without operating the full alignment pipeline. ML/platform teams that want managed execution and reporting. | Operators or platform teams running (or planning) AINL-based monitors and wanting a supported, governance-ready option. | Teams adopting AINL that want an expert pass to reduce risk and time-to-value; orgs that want a “we’ve been reviewed” artifact. |
| **Problem it solves** | Reduces operator and ML ops load; you get alignment quality signals and gate results without standing up and maintaining the pipeline yourself. | Single place for runbook, support, and updates so you can deploy and operate production-style monitors without reverse-engineering; governance-ready documentation. | Catches conformance issues, adapter misuse, or missing discipline before production; gives a prioritized success plan; clear artifact for governance. |
| **Repo grounding** | `run_alignment_cycle.sh`, `sweep_checkpoints.py`, `eval_finetuned_model.py`, `build_regression_supervision.py`; `TRAINING_ALIGNMENT_RUNBOOK.md`; `alignment_run_health.json`. | `examples/autonomous_ops/`, `demo/`, `scripts/run_*.py`; `operations/AUTONOMOUS_OPS_MONITORS.md`, `operations/STANDARDIZED_HEALTH_ENVELOPE.md`. | `BOT_ONBOARDING.md`, `OPENCLAW_IMPLEMENTATION_PREFLIGHT.md`, `CONFORMANCE.md`, `RELEASE_READINESS.md`, `DOCS_INDEX.md`. |
| **What customer gets** | Run health report, trend summary, deliverables package (per scope), runbook and handoff; execution and SLA for run completion and delivery. | Supported pack (programs + runbook + updates + support); governance-ready docs. Runbook covers install, config, cron, health envelope consumption. | Implementation review report (conformance, adapter/ops usage, recommendations); success plan (prioritized next steps); optional follow-up call. |
| **What stays open** | The alignment pipeline, scripts, and runbook remain in the open repo. Paid value is execution, reporting, and SLA. | Monitor source and runner scripts stay open. Health envelope schema and monitor index docs stay open. Paid value is runbook, packaging, updates, support. | All checklists and conformance docs are open. Paid value is our time and structured application to your setup. |
| **Explicitly out of scope** | Custom pipeline logic; full multi-tenant SaaS; managed dashboard; pricing in the draft. | Hosted execution; custom monitors; premium connectors; pricing in the draft. | Ongoing support; certification; implementation work in base engagement; pricing in the draft. |

---

**Full offer drafts:** [Managed Alignment Pipeline](OFFER_MANAGED_ALIGNMENT_PIPELINE.md) · [Supported Ops Monitor Pack](OFFER_SUPPORTED_OPS_MONITOR_PACK.md) · [Implementation Review](OFFER_IMPLEMENTATION_REVIEW.md)

**Note:** Scope, terms, and pricing for any offering are defined in a separate commercial agreement, not in these drafts.
