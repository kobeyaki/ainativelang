# Discovery Call Checklist — Commercial Offers

**Purpose:** Internal guide for discovery calls: triage to the right offer, questions to ask, inputs required, scope risks, and when to recommend Implementation Review first. Based on the three current offers. Not a strategy doc—use it in real conversations.

**Offers:** [Managed Alignment Pipeline](OFFER_MANAGED_ALIGNMENT_PIPELINE.md) · [Supported Ops Monitor Pack](OFFER_SUPPORTED_OPS_MONITOR_PACK.md) · [Implementation Review](OFFER_IMPLEMENTATION_REVIEW.md) · [Comparison](OFFER_COMPARISON.md)

---

## 1. Quick triage

| If the prospect… | Likely fit |
|------------------|------------|
| Wants us to **run** the AINL alignment cycle and **deliver** run health + trend outputs | **Managed Alignment Pipeline** |
| Wants **supported** AINL ops monitors (runbook, updates, support) and will **run them in their own environment** | **Supported Ops Monitor Pack** |
| Wants an **expert review** of their AINL use, a **report**, and a **success plan**; or scope is unclear | **Implementation Review / Onboarding** |

When in doubt or when they mention multiple needs, start with **Implementation Review** to clarify scope and then point to pack or pipeline if relevant.

---

## 2. Questions to ask

### Implementation Review / Onboarding

- **Current situation:** Are you already running AINL, or still evaluating? What’s in place (programs, adapters, deployment)?
- **Technical environment:** Repo we can review, or a written description? Which adapters and monitors do you use?
- **Desired outcomes:** What does “success” look like? Governance artifact? Risk reduction before scaling? Clear next steps?
- **Constraints:** Timeline, budget range (if they volunteer), who needs to sign off on the report?
- **Ownership:** Who will be the point of contact for intake and delivery? Who will act on the success plan?
- **Success criteria:** Conformance only, or conformance + adapter usage + ops/monitor patterns?

### Supported Ops Monitor Pack

- **Current situation:** Are you running (or planning) AINL-based monitors today? Which ones (health checks, token cost, meta-monitor, etc.)?
- **Technical environment:** Where will monitors run (your infra)? Do you have Python, scheduler (cron), and adapter backends (queue, etc.)?
- **Desired outcomes:** Single place for runbook and support? Governance-ready docs? Predictable updates?
- **Constraints:** Must we host execution? (If yes → red flag; we don’t host.) Need custom monitors or premium connectors? (If yes → out of scope for this pack.)
- **Ownership:** Who will deploy and operate the pack? Who will consume the health envelope (queue, webhook, dashboard)?
- **Success criteria:** Fixed supported set acceptable? Need only runbook + updates + support, not hosted execution?

### Managed Alignment Pipeline

- **Current situation:** Do you use (or plan to use) the open AINL training/eval pipeline? What’s your corpus and config story?
- **Technical environment:** Where should runs happen—your VPC or our environment? What access can you provide for corpus/config?
- **Desired outcomes:** Run health and trend outputs on a schedule? SLA for run completion and delivery?
- **Constraints:** Expecting custom pipeline logic, multi-tenant platform, or a managed dashboard? (All out of scope.)
- **Ownership:** Who provides corpus, config, and success criteria? Who consumes run health and trend outputs?
- **Success criteria:** How do you define “pass” (e.g. minimum strict rate, runtime rate, nonempty rate; max regression vs prior run)?

---

## 3. Inputs required

| Offer | Customer must provide |
|-------|------------------------|
| **Implementation Review** | Repo access (or representative slice) or written description of setup, programs, adapters, deployment; scope of review; point of contact. |
| **Supported Ops Monitor Pack** | Environment where AINL runtime and dependencies can run; scheduler (e.g. cron); they operate and secure their infra; point of contact for support and updates. |
| **Managed Alignment Pipeline** | Corpus and configuration (or access); success criteria (“pass” definition); if runs in their VPC, access and permissions; point of contact. |

---

## 4. Scope risks / red flags

- **Asking for hosted execution** (e.g. “Can you run the monitors for us in your cloud?”) when the offer does not include it → Supported Ops Monitor Pack is runbook + updates + support; **they** run monitors in their environment. Managed Alignment Pipeline may run in our environment by agreement, but monitors are not hosted by us in the pack.
- **Asking for custom pipeline logic or new training/eval logic** → Managed Alignment Pipeline uses the **open** pipeline only; no net-new alignment logic in scope.
- **Expecting a managed dashboard, aggregation UI, or alerting product** → Out of scope for current Managed Alignment Pipeline; we deliver run health and trend **outputs**, not a dashboard.
- **Expecting custom monitors or premium connectors** → Supported Ops Monitor Pack is a **fixed supported set**; custom monitors and premium connectors are out of scope unless agreed separately.
- **Unclear success criteria** → Especially for Managed Alignment Pipeline: need a clear “pass” definition (e.g. min rates, max regression). For Implementation Review: agree scope (conformance only vs conformance + adapter + ops) before engagement.
- **Expecting us to implement fixes, write code, or provide ongoing support** in the base Implementation Review engagement → We deliver report + success plan; code/patches or ongoing support only if agreed separately.
- **Treating the offer as full multi-tenant SaaS or open-ended platform** → All three offers are defined scope and deliverables; terms and pricing in a separate agreement.

---

## 5. Recommendation rules

- **Start with Implementation Review** when scope is unclear, they’re new to AINL, or they want a “we’ve been reviewed” artifact first. Use it to clarify whether they later need Supported Ops Monitor Pack or Managed Alignment Pipeline.
- **Use Supported Ops Monitor Pack** when the customer explicitly wants supported operational monitors (runbook, updates, support) and is willing to run them **in their own environment**. Confirm they do not expect hosted execution or custom monitors in the pack.
- **Use Managed Alignment Pipeline** when the customer explicitly wants **us** to run the alignment cycle and deliver run health + trend outputs with agreed SLA. Confirm they can provide corpus, config, and success criteria; and that they are not expecting custom pipeline, multi-tenant platform, or managed dashboard.

---

*Internal use. For offer details and boundaries, see [OFFER_COMPARISON.md](OFFER_COMPARISON.md) and the individual offer drafts. A fillable [discovery intake form](DISCOVERY_INTAKE_FORM.md) is available for use during calls.*
