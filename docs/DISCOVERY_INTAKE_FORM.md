# Discovery Intake Form

**Purpose:** Internal fillable form for use during discovery calls. Capture prospect basics, offer fit, inputs, risks, and next step. Based on [DISCOVERY_CALL_CHECKLIST.md](DISCOVERY_CALL_CHECKLIST.md) and the three current offers. Not a contract; no pricing or legal language.

**Call date:** _______________
**Completed by:** _______________

---

## 1. Prospect basics

| Field | Response |
|-------|----------|
| Client / company name | |
| Contact (name, email) | |
| Team or role | |
| Current need (1–2 sentences) | |
| Source (e.g. inbound, referral) | |

---

## 2. Discovery prompts

*Fill in brief notes from the call.*

**Current situation**
- Are they running AINL today or evaluating? What’s in place (programs, adapters, monitors, pipeline)?
-

**Technical environment**
- Repo we can review or written description? Where would monitors/pipeline run (their infra vs ours)? What stack (Python, scheduler, adapters)?
-

**Desired outcomes**
- What does “success” look like? (e.g. governance artifact, run health outputs, supported monitors, risk reduction)
-

**Constraints**
- Timeline? Any must-haves that might be out of scope (hosted execution, custom monitors, dashboard, custom pipeline)?
-

**Ownership / who runs what**
- Point of contact for intake and delivery? Who deploys/operates? Who consumes outputs (run health, health envelope)?
-

**Success criteria**
- For Implementation Review: conformance only, or conformance + adapter + ops?
- For Managed Alignment: how do they define “pass” (min rates, max regression)?
- For Monitor Pack: fixed supported set OK? Run in their environment OK?
-

---

## 3. Offer-fit section

*Check one or more; use “Unclear / needs review” if triage is uncertain.*

- [ ] **Implementation Review / Onboarding** — Expert review, report, success plan; or scope unclear / first engagement.
- [ ] **Supported Ops Monitor Pack** — Supported monitors, runbook, updates, support; they run in their environment.
- [ ] **Managed Alignment Pipeline** — We run alignment cycle; deliver run health + trend outputs; agreed SLA.
- [ ] **Unclear / needs review** — Recommend Implementation Review first to clarify scope.

**Notes:**

---

## 4. Inputs required

*Check what the prospect has committed or still needs to provide.*

### If Implementation Review
- [ ] Repo access (or representative slice) or written description of setup, programs, adapters, deployment
- [ ] Scope of review agreed (conformance only vs conformance + adapter + ops)
- [ ] Point of contact for intake and delivery

### If Supported Ops Monitor Pack
- [ ] Environment where AINL runtime and dependencies can run
- [ ] Scheduler (e.g. cron) for running monitors
- [ ] Confirmation they operate and secure their infra; we do not host execution
- [ ] Point of contact for support and updates

### If Managed Alignment Pipeline
- [ ] Corpus and configuration (or access)
- [ ] Success criteria (“pass” definition: e.g. min strict rate, runtime rate, nonempty rate; max regression)
- [ ] If runs in their VPC: access and permissions
- [ ] Point of contact

**Gaps / follow-up:**

---

## 5. Risks / red flags

*Check any that came up; note in “Other” if needed.*

- [ ] Expecting **hosted execution** of monitors (we don’t host; they run pack in their environment)
- [ ] Asking for **custom pipeline logic** or new training/eval logic (we use open pipeline only)
- [ ] Expecting **managed dashboard** or aggregation UI (we deliver run health/trend outputs only)
- [ ] Expecting **custom monitors** or **premium connectors** (pack is fixed set; out of scope unless agreed separately)
- [ ] **Unclear success criteria** (e.g. no “pass” definition for alignment; or review scope not agreed)
- [ ] Expecting **implementation work, code, or ongoing support** in base Implementation Review (report + plan only unless agreed separately)
- [ ] Treating offer as **full multi-tenant SaaS** or open-ended platform (defined scope and deliverables only)
- [ ] **Recommend Implementation Review first** — scope unclear, new to AINL, or need to clarify before pack/pipeline

**Other:**

---

## 6. Recommended next step

*Check one.*

- [ ] **Send proposal** — Offer fit clear; inputs understood; use appropriate example proposal and template.
- [ ] **Schedule technical review** — Need deeper technical discussion (e.g. repo walkthrough, environment details) before proposal.
- [ ] **Recommend Implementation Review first** — Scope unclear or prospect new to AINL; propose review to clarify, then pack or pipeline if relevant.
- [ ] **Decline / not a fit yet** — Needs don’t match current offers (e.g. requires hosted execution, custom work, or dashboard we don’t offer); or timing/budget not aligned.

**Next action / owner:**

---

*Internal use only. For offer details and triage rules, see [DISCOVERY_CALL_CHECKLIST.md](DISCOVERY_CALL_CHECKLIST.md) and [OFFER_COMPARISON.md](OFFER_COMPARISON.md).*
