# Commercial Proposal Template — First Deliverables

**Purpose:** Reusable proposal template for the three current commercial offers (Managed Alignment Pipeline, Supported Ops Monitor Pack, Implementation Review / Onboarding). Tailor per client; do not use as-is without filling placeholders and aligning scope to the selected offer. Consistent with the offer drafts and the locked open-core boundary. Scope, terms, and pricing are defined in a separate commercial agreement.

---

## 1. Usage note

This template supports the offers described in [OFFER_COMPARISON.md](OFFER_COMPARISON.md) and the individual offer drafts. Filled examples: [Managed Alignment Pipeline](EXAMPLE_PROPOSAL_MANAGED_ALIGNMENT_PIPELINE.md); [Supported Ops Monitor Pack](EXAMPLE_PROPOSAL_SUPPORTED_OPS_MONITOR_PACK.md); [Implementation Review](EXAMPLE_PROPOSAL_IMPLEMENTATION_REVIEW.md). For each proposal:

- Select **one** offer type.
- Replace all `[Placeholders]` with client- and project-specific content.
- Keep "what remains open" and "out of scope" consistent with the offer draft so the client understands what is repo/open vs service/support.
- Do not invent pricing, legal terms, or delivery infrastructure we do not already support. Use a clear placeholder for commercial terms and handle them in a separate agreement.

---

## 2. Proposal structure

### Client / project

- **Client:** [Client Name]
- **Project:** [Project Name or Engagement Name]
- **Selected offer:** [Managed Alignment Pipeline | Supported Ops Monitor Pack | Implementation Review / Onboarding]

---

### Summary

[2–4 sentences: what we are proposing, for whom, and the main outcome. Use the proposal-ready summary from the relevant offer doc as a base, then tailor to this client.]

---

### Client goals

- [Goal 1]
- [Goal 2]
- [Additional goals as needed]

---

### Current situation / context

[Brief description of the client’s current setup, pain points, or context that this engagement addresses. E.g. “You are running the alignment pipeline in-house and want managed execution and reporting” or “You are adopting AINL and want an expert review before scaling.”]

---

### Scope of work

[Bullet list of what we will do under this engagement. Pull from the “What we do” / “Scope” section of the selected offer draft; narrow or clarify as needed for this client.]

- [Scope item 1]
- [Scope item 2]
- [Scope item 3]
- [Add/remove as needed]

---

### Customer responsibilities / inputs

[What the client must provide or do. Pull from the offer draft (e.g. corpus and config, execution environment access, repo or description, point of contact).]

- [Input / responsibility 1]
- [Input / responsibility 2]
- [Add as needed]

---

### Deliverables

[What the client will receive. Pull from the offer draft (e.g. run health report and trend summary; supported pack and runbook; implementation review report and success plan).]

- [Deliverable 1]
- [Deliverable 2]
- [Add as needed]

---

### What remains open / repo-grounded

[Short statement that the underlying pipeline, monitors, or docs remain in the open repo; the paid value is execution/support/packaging/our time, not exclusive access to code. Use the “What stays open” row from OFFER_COMPARISON.md for the selected offer.]

---

### Out of scope

[Bullet list of what is explicitly not included. Use the “Explicitly out of scope” row from the offer draft; add any client-specific exclusions.]

- [Out of scope 1]
- [Out of scope 2]
- [Add as needed]

---

### Assumptions / dependencies

- [Assumption or dependency 1, e.g. “Client will provide read access to repo by [date].”]
- [Assumption or dependency 2]
- [Add as needed. Keep lightweight; no fake dates if not agreed.]

---

### Timeline / phases

[Lightweight phases only. Use placeholders for dates; do not invent delivery dates.]

- **Phase 1:** [e.g. Intake and scope confirmation] — [Timeline placeholder, e.g. “[TBD]” or “Week 1”]
- **Phase 2:** [e.g. Execution or review] — [Timeline placeholder]
- **Phase 3:** [e.g. Delivery and handoff] — [Timeline placeholder]

[Adjust phase names and count to match the selected offer.]

---

### Commercial terms

[Commercial Terms / Pricing handled separately]

Scope, pricing, and legal terms for this engagement will be set out in a separate commercial agreement (or SOW). This document describes the proposed scope and deliverables only.

---

### Acceptance / next steps

- [e.g. Client confirms scope and contacts us to finalize commercial terms.]
- [e.g. Upon signed agreement, we will confirm kickoff date and intake details.]
- [Add 1–2 concrete next steps.]

---

## 3. Offer-specific guidance

### Managed Alignment Pipeline

- **Emphasize:** Execution of the alignment cycle (we run it); delivery of run health and trend outputs; runbook and SLA for run completion and delivery. Customer provides corpus/config and (if applicable) execution environment.
- **Leave out:** Custom pipeline logic; multi-tenant platform; managed dashboard; any promise of infrastructure we do not yet operate.
- **Common scope boundaries:** One execution path (customer VPC or our environment, as agreed). Support limited to run execution, runbook, and delivery of run health/trend outputs. Data ownership and retention covered in separate data/security terms.

### Supported Ops Monitor Pack

- **Emphasize:** Runbook, guaranteed updates, and support for a curated set of monitors. Customer runs monitors in their environment; we do not host execution. Which monitors are in the pack (e.g. infrastructure watchdog, meta monitor, token cost tracker) and update cadence (e.g. quarterly) should be stated.
- **Leave out:** Hosted execution of monitors; custom monitors; premium connectors; exclusive access to code (code stays open).
- **Common scope boundaries:** Fixed supported set; no custom or one-off monitors unless agreed separately. Deployment and scheduling are the client’s responsibility; runbook covers how to deploy and consume the health envelope.

### Implementation Review / Onboarding

- **Emphasize:** Structured review against conformance, adapter usage, and recommended practices; written report and success plan; optional follow-up call. One-time or defined-scope engagement.
- **Leave out:** Ongoing support; certification; implementation work (we review and recommend, we do not implement fixes in the base engagement).
- **Common scope boundaries:** Scope of review (e.g. conformance only vs conformance + adapter/ops) agreed upfront. Deliverables are report and success plan; code/patches or ongoing support only if agreed separately (e.g. consulting SOW).

---

## 4. Placeholder checklist

Before sending a proposal, replace or confirm:

- [Client Name]
- [Project Name]
- [Selected Offer]
- [Summary — tailored from offer draft]
- [Scope of work — aligned to selected offer]
- [Customer responsibilities / inputs]
- [Deliverables]
- [What remains open — consistent with offer]
- [Out of scope — consistent with offer]
- [Assumptions / dependencies]
- [Timeline / phases — no fake dates]
- [Commercial Terms / Pricing handled separately]
- [Acceptance / next steps]

---

*Template only. Not a contract. For full offer text and boundaries, see [OFFER_COMPARISON.md](OFFER_COMPARISON.md) and the individual offer drafts. Boundary: [OPEN_CORE_DECISION_SHEET.md](OPEN_CORE_DECISION_SHEET.md).*
