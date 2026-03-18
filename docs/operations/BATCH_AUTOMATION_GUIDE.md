## Batch repo-automation and Dispatch-style integration

This guide is for **batch issue-solving** and **worktree-based repo automation**
environments (Dispatch-style systems, CI bots, scheduled jobs, etc.) that want
to use AINL in a deterministic, auditable way.

It assumes:

- the host controls a **local checkout / worktree**
- changes are reviewed via normal VCS workflows
- AINL is one tool among several, not the orchestrator or control plane

---

## 1. Recommended surfaces

- **HTTP runner service (`ainl-runner-service`)**
  - Best for long-running or queued batch jobs.
  - Use `/run` for synchronous runs and `/enqueue` + `/result/{job_id}` for
    background work.
  - See `docs/operations/RUNTIME_CONTAINER_GUIDE.md` for deployment details.

- **MCP server (`ainl-mcp`)**
  - Best when your batch/automation host is an MCP-compatible agent runtime.
  - Exposes `ainl_validate`, `ainl_compile`, `ainl_capabilities`,
    `ainl_security_report`, and `ainl_run` as tools.
  - See section 9 of `docs/operations/EXTERNAL_ORCHESTRATION_GUIDE.md`.

Both surfaces share the same compiler/runtime and policy/limits model.

---

## 2. Worktree-safe practices

- **Run against a throwaway or dedicated worktree**
  - Use `git worktree` or a cloned checkout per job.
  - Never point AINL at a production working copy without review gates.

- **Review-before-write**
  - Prefer AINL workflows that **propose** patches or summaries rather than
    applying writes directly.
  - Have your automation host:
    - capture AINL output as machine-readable JSON,
    - render diffs or PRs,
    - route to a human or policy engine for approval before merging.

- **Deterministic inputs**
  - Pin:
    - repo revision (commit SHA),
    - runtime configuration (security profile, policy, limits),
    - any external configuration AINL reads.
  - Treat the combination of `(AINL program, inputs, commit, policy, limits)`
    as the **unit of audit**.

---

## 3. Read-only / inspect-first phase

For batch automation, run an **inspection phase** before any execution:

- Use `ainl_validate` and `ainl_compile` to:
  - check syntax and IR shape,
  - ensure workflows compile under your chosen strictness.
- Use `ainl_capabilities` and `ainl_security_report` to:
  - list adapters and verbs used,
  - confirm privilege tiers, privilege boundaries, and effects.

This phase should run under **read-only** exposure and security profiles.

---

## 4. Choosing exposure profiles

When using the MCP surface (`ainl-mcp`):

- **`validate_only`**
  - Use for **pure validation/IR inspection** workflows.
  - Good default when you only want to gate PRs or issues on “does the AINL
    program compile and pass policy?”.

- **`inspect_only`**
  - Use when batch jobs also need capabilities and security reports, but
    **must not execute** workflows.
  - Recommended for “inspection-first” repo automation and policy/reporting
    jobs.

- **`safe_workflow`**
  - Use only after operators have:
    - reviewed the security profile / capability grant,
    - set explicit policy and limits,
    - confirmed which adapters are allowed in this environment.
  - Suitable for controlled “apply changes” or “run monitor” jobs where
    execution is expected and approved.

Remember the three layers:

- **MCP exposure profile** — what tools/resources the host can discover.
- **Security profile / capability grant** — what runtime execution is allowed.
- **Policy / limits** — what each individual run is constrained by.

---

## 5. Machine-readable results and traces

Batch and repo automation flows should treat AINL runs as **structured events**:

- **Runner service**
  - `/run` and `/result/{job_id}` already return JSON with:
    - `ok`, `trace_id`, `error` / `error_structured`,
    - `out` (execution result) on success.
  - Your automation host can log `trace_id` and `result_hash` (from JSON logs)
    as stable references for audits.

- **MCP `ainl_run`**
  - Returns a JSON object with `ok`, `trace_id`, `label`, `out`,
    `runtime_version`, and `ir_version`.
  - For batch queues, consider wrapping this using
    `tooling/result_summary.py:summarize_run_result` to get a compact envelope
    with:
    - `task_id`, `status`, `summary`, `result`, `trace_id`, `policy_errors`,
      `artifacts`, `review_hint`.

In all cases, **host code** is responsible for:

- storing results and traces,
- associating them with issues/PRs,
- deciding what artifacts to keep or discard.

---

## 6. Timeouts, limits, and policy

For batch automation and CI-like environments:

- Prefer **restrictive defaults**:
  - use a named security profile with conservative limits, or
  - set server-level grants (runner service) / MCP grants that cap:
    - `max_steps`, `max_depth`, `max_adapter_calls`, `max_time_ms`.

- Use **policy validation** before execution:
  - For runner-service: validate IR against `policy` before running.
  - For MCP: rely on `ainl_security_report` plus host-side governance to decide
    which programs are allowed to run.

- Treat **policy violations** as:
  - validation failures in CI,
  - “do not apply” signals for any write-capable workflows.

---

## 7. Determinism and auditability checklist

To keep batch runs deterministic and auditable:

- Pin:
  - AINL version and runtime image.
  - Repo revision and dependency versions.
  - Security profile, policy, and limits config.
- Capture for each run:
  - `trace_id` (always present),
  - input AINL program (or a stable reference/commit),
  - structured output (`out` or the summary envelope),
  - any policy/validation errors.
- Route all file or repo writes through:
  - a review gate (PRs, code review),
  - or a separate, audited “apply” job that runs under `safe_workflow` with
    explicit operator approval.

This keeps AINL a **scoped, deterministic workflow engine** inside your
Dispatch-style or batch orchestration environment, without turning it into a
host, queue, or control plane.

---

## Batch-safe recipe (issue-solving / worktree automation)

If you are using AINL in batch issue-solving or worktree-based automation:

1. **Inspect first.** Run `ainl_validate` / `ainl_compile` and
   `ainl_capabilities` / `ainl_security_report` under `validate_only` or
   `inspect_only` to understand what a workflow will do before any execution.
2. **Execute only when needed.** Enable execution (runner `/run` or MCP
   `ainl_run` under `safe_workflow`) only for jobs that have been approved by
   policy and/or a human reviewer.
3. **Use result summaries for queues.** For job/result queues, wrap raw results
   with `tooling/result_summary.py:summarize_run_result` so automation can sort
   on `status`, `summary`, and `trace_id` while still keeping the full `result`
   payload available.
4. **Audit and log.** Log `trace_id`, policy/validation outcomes, and the
   associated repo revision for every job. Use these logs as the source of
   truth for debugging, compliance, and cost analysis.

