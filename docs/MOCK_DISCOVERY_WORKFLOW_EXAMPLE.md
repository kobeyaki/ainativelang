# Mock Discovery Workflow Example

**Purpose:** One realistic internal example of the discovery workflow from first contact through recommended next step. Uses the OpenClaw repo and AINL usage as the “client” scenario to pressure-test how the commercial materials are used together. Not a real engagement; no pricing or legal terms.

**Docs used:** [SERVICES_PAGE_DRAFT.md](SERVICES_PAGE_DRAFT.md) · [DISCOVERY_CALL_CHECKLIST.md](DISCOVERY_CALL_CHECKLIST.md) · [DISCOVERY_INTAKE_FORM.md](DISCOVERY_INTAKE_FORM.md) · [OFFER_COMPARISON.md](OFFER_COMPARISON.md) · example proposals.

---

## 1. Prospect summary

**Scenario:** A team (treated as “OpenClaw-style” internal user) is using AINL for internal agent workflows: daily digest, monitor system, cron jobs, and adapters (email, calendar, social, db, svc, cache, queue, wasm). They have existing `.lang` programs, a runner/cron setup, and preflight/onboarding docs in use. They reached out to understand commercial options—initially unclear whether they need an implementation review, supported monitor pack, or managed alignment pipeline.

**First contact:** Inbound; “We’re running AINL for internal workflows and want to understand what supported options exist and whether we’re set up correctly.”

---

## 2. Likely pains / needs

- **Governance / auditability** — Want to confirm their AINL use (programs, adapters, deployment) aligns with contracts and best practices before scaling.
- **Operational clarity** — Want a single place for runbooks, support, or updates for monitors (e.g. infrastructure watchdog, token cost, meta-monitor) without reverse-engineering.
- **Unclear fit** — Not yet sure if they need expert review first, supported pack, or someone to run the alignment cycle; need triage.

---

## 3. Discovery notes (from intake form)

**Call date:** [Example] 2025-03-15
**Completed by:** [Internal owner]

### Prospect basics
| Field | Response |
|-------|----------|
| Client / company name | [Internal team / OpenClaw-style setup] |
| Contact | [Platform lead] |
| Team or role | Platform / agent automation |
| Current need | Using AINL for daily digest, monitor system, cron workflows; want to validate setup and understand supported options (review vs monitor pack vs managed alignment). |
| Source | Inbound |

### Discovery prompts (notes)
- **Current situation:** Running AINL today. In place: daily digest, monitor system, cron; adapters (email, calendar, social, db, svc, cache, queue, wasm); preflight and onboarding docs in use. No formal alignment pipeline runs yet; monitors are ad hoc from repo.
- **Technical environment:** Repo available for review. Monitors and workflows run in their environment (Python, cron, existing runner). No ask for us to host execution.
- **Desired outcomes:** (1) “We’ve been reviewed” artifact for governance; (2) optionally a supported path for monitors (runbook + updates) if it fits; (3) clarity on whether managed alignment is relevant later.
- **Constraints:** No requirement for hosted execution or custom pipeline. Open to running monitors in their environment. Timeline: next quarter for formal review or pack.
- **Ownership:** Platform lead = point of contact; same team deploys/operates today; would consume runbook/report outputs.
- **Success criteria:** For review—conformance + adapter usage + ops/monitor patterns. For pack—fixed set OK; run in their env OK. For pipeline—not in scope for this intake (no corpus/config yet).

---

## 4. Offer-fit decision

- [x] **Implementation Review / Onboarding** — Primary fit. Scope was unclear at first; they want expert pass, report, and success plan; good first engagement.
- [ ] **Supported Ops Monitor Pack** — Possible follow-on once review is done and they confirm they want supported runbook/updates for the monitor set they use.
- [ ] **Managed Alignment Pipeline** — Not in scope for this intake; no corpus/config or alignment pipeline use yet.
- [ ] **Unclear / needs review** — Resolved: recommend Implementation Review first.

**Notes:** Triage from checklist: “Wants an expert review… or scope is unclear” → Implementation Review. Pack and pipeline can be revisited after review.

---

## 5. Risks / red flags observed

- [ ] Expecting hosted execution — Not raised; they run in their environment.
- [ ] Custom pipeline logic — N/A; no alignment pipeline ask.
- [ ] Managed dashboard — Not asked.
- [ ] Custom monitors / premium connectors — Not asked; fixed supported set acceptable if we propose pack later.
- [x] **Unclear success criteria** — Addressed in call: agreed review scope = conformance + adapter + ops.
- [ ] Implementation work in base review — Clarified: we deliver report + success plan only; they implement.
- [ ] Multi-tenant SaaS — Not assumed.
- [x] **Recommend Implementation Review first** — Scope was unclear; they’re adopting AINL with existing programs; review will clarify and may lead to pack (or pipeline) later.

---

## 6. Recommended next step

- [x] **Recommend Implementation Review first** — Scope clarified; propose Implementation Review to deliver report and success plan; then discuss Supported Ops Monitor Pack if they want runbook/updates for monitors.
- [ ] Send proposal — After they confirm scope (conformance + adapter + ops).
- [ ] Schedule technical review — Not required; repo access and description sufficient for proposal.
- [ ] Decline / not a fit yet — Not applicable; fit confirmed.

**Next action:** Send Implementation Review example proposal (tailored with [Client Name], scope = conformance + adapter + ops); propose call to confirm scope and timeline. Commercial terms and pricing in separate agreement.

---

## 7. Document to send next

**Proposal:** [EXAMPLE_PROPOSAL_IMPLEMENTATION_REVIEW.md](EXAMPLE_PROPOSAL_IMPLEMENTATION_REVIEW.md)

- Use as the base; replace [Client Name] and project context with the actual team/setup.
- Confirm scope in proposal: conformance + adapter usage + ops/monitor patterns.
- Attach or reference [OFFER_IMPLEMENTATION_REVIEW.md](OFFER_IMPLEMENTATION_REVIEW.md) for full offer; [PROPOSAL_TEMPLATE_COMMERCIAL_OFFERS.md](PROPOSAL_TEMPLATE_COMMERCIAL_OFFERS.md) if customizing further.
- No pricing in the proposal; terms and pricing in separate commercial agreement.

---

*Mock example only. For real discovery use [DISCOVERY_INTAKE_FORM.md](DISCOVERY_INTAKE_FORM.md) and [DISCOVERY_CALL_CHECKLIST.md](DISCOVERY_CALL_CHECKLIST.md).*
