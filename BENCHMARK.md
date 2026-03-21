# AI Native Lang Size Benchmark

This benchmark measures AINL source compactness against generated implementation artifacts.
It is segmented by profile and mode; it is not a universal compactness claim across programming languages.

> **Sizing:** All markdown tables foreground **tiktoken** **cl100k_base** token counts (billing-accurate for GPT-4o-class models). JSON numeric fields still use the CLI `--metric`.
> **Emitters:** `prisma` and `react_ts` benchmark stubs were **compacted (Mar 2026)** for benchmark efficiency.
> **minimal_emit:** includes a tiny **python_api** async **fallback stub** when no selected target emits code.
> **Headline ratios:** **viable** subset for `public_mixed` / `compatibility_only` (legacy / pure-cron focus); **full legacy-inclusive** totals appear [below](#including-legacy-artifacts).

## Benchmark Profiles

- `canonical_strict_valid`: Primary public benchmark headline set (strict-valid canonical examples).
- `public_mixed`: Mixed public examples (strict-valid + non-strict-only), clearly labeled as mixed.
- `compatibility_only`: Compatibility-oriented examples only (non-strict/legacy classes). Not a headline set.

## Benchmark Modes

- `full_multitarget`: includes all benchmark targets for each artifact.
- `minimal_emit`: includes only capability-required targets for each artifact.

## Compiler IR Capability Contract

- `emit_capabilities.needs_python_api`: backend/API execution surface is required.
- `emit_capabilities.needs_react_ts`: frontend UI output is required.
- `emit_capabilities.needs_prisma`: schema/data model output is required.
- `emit_capabilities.needs_mt5`: MT5 strategy output is required.
- `emit_capabilities.needs_scraper`: scraper output is required.
- `emit_capabilities.needs_cron`: cron/scheduler output is required.
- `required_emit_targets.minimal_emit`: compiler-planned minimal target set (planner primary source).

## Metrics

- **Default / recommended:** `tiktoken` (**cl100k_base**) via `tooling/bench_metrics.py` (shared with runtime benchmarks).
- **Active CLI metric (JSON):** `tiktoken` — drives raw JSON sizes, economics basis, and viable-threshold comparisons where noted; markdown artifact tables still list **(tk)** for readability.
- **Compile ms (mean×3):** mean wall time of three ``compile(..., emit_graph=True)`` calls per artifact (see JSON ``compile_time_ms_mean``); unrelated to optional compile-reliability batches.

## How To Read These Results

- Ratio `> 1`: generated output is larger than AINL source.
- Ratio `~ 1`: near parity.
- Ratio `< 1`: generated output is smaller than AINL source.
- Summary and mode-comparison ratios in this document use **tiktoken** sums unless labeled otherwise; match them to the **(tk)** columns in detail tables.

## Full Multitarget vs Minimal Emit

- `full_multitarget` shows total downstream expansion potential across all emitters.
- `minimal_emit` is closer to practical deployment comparison because it emits only required targets.

## Why Some Ratios Got Worse After Truthfulness Fixes

- Ratios can worsen when examples are corrected to express capabilities they were already claiming publicly.
- This is expected: honest capability accounting increases counted generated output where prior under-emission existed.
- The result is less flattering but more trustworthy and action-guiding.

## What We Can Honestly Claim

- The benchmark is reproducible, profile-segmented, and mode-segmented.
- Minimal mode is the better comparison for practical deployment size discussions.
- Full mode is useful for measuring expansion leverage, not apples-to-apples terseness.

## What These Numbers Are Not

- They are not universal superiority claims over mainstream languages.
- They are not a substitute for measuring your own prompts: tiktoken counts are reproducible for this repo’s emitted text, but vendor tokenizers may differ slightly.
- They are not a proxy for runtime performance or product quality by themselves.

> **Viable subset (`public_mixed` / `compatibility_only`):** selection rules use the **CLI metric** (`tiktoken`) on JSON row fields — aggregate emit &lt; 50 (tiktoken units), large-source low-ratio heuristic (source ≥ 400, ratio &lt; 0.22), plus `viable_for_aggregate` overrides in `tooling/artifact_profiles.json`. **Markdown** headline ratios are recomputed in **tiktoken** for the same viable rows. Strict-valid rows in `public_mixed` stay viable. **Legacy-inclusive** totals: [Including Legacy Artifacts](#including-legacy-artifacts).

## Mode Comparison (Headline + Mixed)

| Profile | Full ratio (viable, tk) | Minimal ratio (viable, tk) | Viable artifacts |
|---|---:|---:|---|
| canonical_strict_valid | 8.91x | 2.22x | 10/10 |
| public_mixed | 0.96x | 1.02x | 46/59 |
| compatibility_only | 0.79x | 0.83x | 36/49 |

Compatibility/non-strict artifacts are segmented and not used as the primary benchmark headline.

## Size Drivers (Actionable Diagnosis)

- Values below are **tiktoken (tk)** on the same **viable** subset as headline drivers when applicable (CLI metric: `tiktoken`).

### full_multitarget
- `canonical_strict_valid` top targets (tk): mt5=1770, python_api=961, scraper=919
- `canonical_strict_valid` top artifacts (tk): examples/scraper/basic_scraper.ainl=591, examples/monitor_escalation.ainl=521, examples/web/basic_web_api.ainl=434
- `public_mixed` top targets (tk): mt5=8907, python_api=4593, scraper=3979
- `public_mixed` top artifacts (tk): examples/internal_tool.lang=787, examples/ticketing.lang=743, examples/ecom.lang=712
- `compatibility_only` top targets (tk): mt5=7137, python_api=3632, scraper=3060
- `compatibility_only` top artifacts (tk): examples/internal_tool.lang=787, examples/ticketing.lang=743, examples/ecom.lang=712

### minimal_emit
- `canonical_strict_valid` top targets (tk): python_api=771, cron=197, scraper=154
- `canonical_strict_valid` top artifacts (tk): examples/scraper/basic_scraper.ainl=253, examples/web/basic_web_api.ainl=106, examples/monitor_escalation.ainl=98
- `public_mixed` top targets (tk): python_api=1743, prisma=766, react_ts=667
- `public_mixed` top artifacts (tk): examples/internal_tool.lang=459, examples/ticketing.lang=419, examples/ecom.lang=394
- `compatibility_only` top targets (tk): python_api=972, prisma=766, react_ts=667
- `compatibility_only` top artifacts (tk): examples/internal_tool.lang=459, examples/ticketing.lang=419, examples/ecom.lang=394

## Residual Overhead Audit (minimal_emit)

### canonical_strict_valid
- `python_api` total=771; structure: decorator_chunks=5, function_def_chunks=6, imports_chunks=56, return_chunks=6, total_chunks=771
- `cron` total=197; structure: function_def_chunks=11, pass_chunks=6, schedule_comment_chunks=180, total_chunks=197
- `scraper` total=154; structure: function_def_chunks=4, imports_chunks=11, request_call_chunks=18, return_chunks=17, selector_chunks=22, total_chunks=154

### public_mixed
- `python_api` total=1743; structure: decorator_chunks=103, function_def_chunks=120, imports_chunks=112, return_chunks=120, total_chunks=1743
- `prisma` total=766; structure: total_chunks=766
- `react_ts` total=667; structure: total_chunks=667

### compatibility_only
- `python_api` total=972; structure: decorator_chunks=98, function_def_chunks=114, imports_chunks=56, return_chunks=114, total_chunks=972
- `prisma` total=766; structure: total_chunks=766
- `react_ts` total=667; structure: total_chunks=667

## Details (full_multitarget)

| Profile | Viable artifacts | AINL source Σ (tk, viable) | Aggregate Σ (tk, viable) | Ratio (tk, viable) | Excluded legacy |
|---|---:|---:|---:|---:|---:|
| canonical_strict_valid | 10 | 506 | 4507 | 8.91x | 0 |
| public_mixed | 46 | 24138 | 23272 | 0.96x | 13 |
| compatibility_only | 36 | 23632 | 18765 | 0.79x | 13 |

### canonical_strict_valid
| Artifact | Class | AINL source (tk) | Compile ms (mean×3) | React/TS (tk) | Python API (tk) | Prisma (tk) | MT5 (tk) | Scraper (tk) | Cron (tk) | Aggregate Σ (tk) | Ratio (tk) | Included targets | Notes |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---|
| examples/crud_api.ainl | strict-valid | 37 | 0.496 | 26 | 95 | 40 | 177 | 85 | 0 | 423 | 11.43x | react_ts, python_api, prisma, mt5, scraper, cron | (compacted prisma emitter); (compacted react_ts emitter) |
| examples/hello.ainl | strict-valid | 18 | 0.218 | 26 | 95 | 40 | 177 | 85 | 0 | 423 | 23.50x | react_ts, python_api, prisma, mt5, scraper, cron | (compacted prisma emitter); (compacted react_ts emitter) |
| examples/if_call_workflow.ainl | strict-valid | 83 | 0.797 | 26 | 95 | 40 | 177 | 85 | 0 | 423 | 5.10x | react_ts, python_api, prisma, mt5, scraper, cron | (compacted prisma emitter); (compacted react_ts emitter) |
| examples/monitor_escalation.ainl | strict-valid | 72 | 0.506 | 26 | 95 | 40 | 177 | 85 | 98 | 521 | 7.24x | react_ts, python_api, prisma, mt5, scraper, cron | (compacted prisma emitter); (compacted react_ts emitter) |
| examples/rag_pipeline.ainl | strict-valid | 29 | 0.346 | 26 | 95 | 40 | 177 | 85 | 0 | 423 | 14.59x | react_ts, python_api, prisma, mt5, scraper, cron | (compacted prisma emitter); (compacted react_ts emitter) |
| examples/retry_error_resilience.ainl | strict-valid | 54 | 0.501 | 26 | 95 | 40 | 177 | 85 | 0 | 423 | 7.83x | react_ts, python_api, prisma, mt5, scraper, cron | (compacted prisma emitter); (compacted react_ts emitter) |
| examples/scraper/basic_scraper.ainl | strict-valid | 67 | 0.329 | 26 | 95 | 40 | 177 | 154 | 99 | 591 | 8.82x | react_ts, python_api, prisma, mt5, scraper, cron | (compacted prisma emitter); (compacted react_ts emitter) |
| examples/status_branching.ainl | strict-valid | 48 | 0.488 | 26 | 95 | 40 | 177 | 85 | 0 | 423 | 8.81x | react_ts, python_api, prisma, mt5, scraper, cron | (compacted prisma emitter); (compacted react_ts emitter) |
| examples/web/basic_web_api.ainl | strict-valid | 32 | 0.265 | 26 | 106 | 40 | 177 | 85 | 0 | 434 | 13.56x | react_ts, python_api, prisma, mt5, scraper, cron | (compacted prisma emitter); (compacted react_ts emitter) |
| examples/webhook_automation.ainl | strict-valid | 66 | 0.748 | 26 | 95 | 40 | 177 | 85 | 0 | 423 | 6.41x | react_ts, python_api, prisma, mt5, scraper, cron | (compacted prisma emitter); (compacted react_ts emitter) |

*Token counts via tiktoken **cl100k_base**. Minimal_emit **fallback** stubs are typically ~20–30 tk.*

### public_mixed
| Artifact | Class | AINL source (tk) | Compile ms (mean×3) | React/TS (tk) | Python API (tk) | Prisma (tk) | MT5 (tk) | Scraper (tk) | Cron (tk) | Aggregate Σ (tk) | Ratio (tk) | Included targets | Notes |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---|
| examples/api_only.lang | non-strict-only | 107 | 0.631 | 26 | 128 | 76 | 219 | 85 | 0 | 534 | 4.99x | react_ts, python_api, prisma, mt5, scraper, cron | (compacted prisma emitter); (compacted react_ts emitter) |
| examples/autonomous_ops/backup_freshness_to_queue.lang | non-strict-only | 192 | 1.058 | 26 | 95 | 40 | 177 | 85 | 0 | 423 | 2.20x | react_ts, python_api, prisma, mt5, scraper, cron | (legacy excluded from viable); (compacted prisma emitter); (compacted react_ts emitter) |
| examples/autonomous_ops/canary_sampler.lang | non-strict-only | 1370 | 5.695 | 26 | 95 | 40 | 177 | 85 | 98 | 521 | 0.38x | react_ts, python_api, prisma, mt5, scraper, cron | (compacted prisma emitter); (compacted react_ts emitter) |
| examples/autonomous_ops/duplicate_detection.lang | non-strict-only | 625 | 1.255 | 26 | 95 | 68 | 202 | 85 | 0 | 476 | 0.76x | react_ts, python_api, prisma, mt5, scraper, cron | (compacted prisma emitter); (compacted react_ts emitter) |
| examples/autonomous_ops/infrastructure_watchdog.lang | non-strict-only | 2222 | 5.077 | 26 | 95 | 40 | 177 | 85 | 98 | 521 | 0.23x | react_ts, python_api, prisma, mt5, scraper, cron | (compacted prisma emitter); (compacted react_ts emitter) |
| examples/autonomous_ops/invoice_aging.lang | non-strict-only | 384 | 0.881 | 26 | 95 | 69 | 204 | 85 | 0 | 479 | 1.25x | react_ts, python_api, prisma, mt5, scraper, cron | (compacted prisma emitter); (compacted react_ts emitter) |
| examples/autonomous_ops/lead_aging.lang | non-strict-only | 404 | 0.836 | 26 | 95 | 73 | 210 | 85 | 0 | 489 | 1.21x | react_ts, python_api, prisma, mt5, scraper, cron | (compacted prisma emitter); (compacted react_ts emitter) |
| examples/autonomous_ops/lead_quality_audit.lang | non-strict-only | 1417 | 3.788 | 26 | 95 | 40 | 177 | 85 | 99 | 522 | 0.37x | react_ts, python_api, prisma, mt5, scraper, cron | (compacted prisma emitter); (compacted react_ts emitter) |
| examples/autonomous_ops/lead_score_drift.lang | non-strict-only | 642 | 1.102 | 26 | 95 | 66 | 197 | 85 | 0 | 469 | 0.73x | react_ts, python_api, prisma, mt5, scraper, cron | (compacted prisma emitter); (compacted react_ts emitter) |
| examples/autonomous_ops/memory_prune.lang | non-strict-only | 220 | 0.534 | 26 | 95 | 40 | 177 | 85 | 99 | 522 | 2.37x | react_ts, python_api, prisma, mt5, scraper, cron | (compacted prisma emitter); (compacted react_ts emitter) |
| examples/autonomous_ops/meta_monitor.lang | non-strict-only | 498 | 1.191 | 26 | 95 | 40 | 177 | 85 | 98 | 521 | 1.05x | react_ts, python_api, prisma, mt5, scraper, cron | (compacted prisma emitter); (compacted react_ts emitter) |
| examples/autonomous_ops/missing_fields.lang | non-strict-only | 631 | 1.750 | 26 | 95 | 68 | 202 | 85 | 0 | 476 | 0.75x | react_ts, python_api, prisma, mt5, scraper, cron | (compacted prisma emitter); (compacted react_ts emitter) |
| examples/autonomous_ops/monitor_system.lang | non-strict-only | 2117 | 16.292 | 26 | 95 | 127 | 257 | 85 | 0 | 590 | 0.28x | react_ts, python_api, prisma, mt5, scraper, cron | (compacted react_ts emitter) |
| examples/autonomous_ops/pipeline_readiness_snapshot.lang | non-strict-only | 216 | 1.314 | 26 | 95 | 40 | 177 | 85 | 0 | 423 | 1.96x | react_ts, python_api, prisma, mt5, scraper, cron | (legacy excluded from viable); (compacted prisma emitter); (compacted react_ts emitter) |
| examples/autonomous_ops/revenue_forecast.lang | non-strict-only | 454 | 1.034 | 26 | 95 | 69 | 204 | 85 | 0 | 479 | 1.06x | react_ts, python_api, prisma, mt5, scraper, cron | (compacted prisma emitter); (compacted react_ts emitter) |
| examples/autonomous_ops/service_health_trends.lang | non-strict-only | 1042 | 4.404 | 26 | 95 | 60 | 186 | 85 | 0 | 452 | 0.43x | react_ts, python_api, prisma, mt5, scraper, cron | (compacted prisma emitter); (compacted react_ts emitter) |
| examples/autonomous_ops/session_continuity.lang | non-strict-only | 1026 | 1.841 | 26 | 95 | 40 | 177 | 85 | 99 | 522 | 0.51x | react_ts, python_api, prisma, mt5, scraper, cron | (compacted prisma emitter); (compacted react_ts emitter) |
| examples/autonomous_ops/status_snapshot_to_queue.lang | non-strict-only | 214 | 1.300 | 26 | 95 | 40 | 177 | 85 | 0 | 423 | 1.98x | react_ts, python_api, prisma, mt5, scraper, cron | (legacy excluded from viable); (compacted prisma emitter); (compacted react_ts emitter) |
| examples/autonomous_ops/tiktok_health.lang | non-strict-only | 293 | 0.663 | 26 | 95 | 65 | 195 | 85 | 0 | 466 | 1.59x | react_ts, python_api, prisma, mt5, scraper, cron | (compacted prisma emitter); (compacted react_ts emitter) |
| examples/autonomous_ops/tiktok_sla_monitor.lang | non-strict-only | 1019 | 3.631 | 26 | 95 | 40 | 177 | 85 | 98 | 521 | 0.51x | react_ts, python_api, prisma, mt5, scraper, cron | (compacted prisma emitter); (compacted react_ts emitter) |
| examples/autonomous_ops/token_budget_tracker.lang | non-strict-only | 1089 | 2.133 | 26 | 95 | 40 | 177 | 85 | 98 | 521 | 0.48x | react_ts, python_api, prisma, mt5, scraper, cron | (compacted prisma emitter); (compacted react_ts emitter) |
| examples/autonomous_ops/token_cost_tracker.lang | non-strict-only | 1266 | 2.519 | 26 | 95 | 40 | 177 | 85 | 98 | 521 | 0.41x | react_ts, python_api, prisma, mt5, scraper, cron | (compacted prisma emitter); (compacted react_ts emitter) |
| examples/blog.lang | non-strict-only | 237 | 0.930 | 150 | 139 | 88 | 238 | 85 | 0 | 700 | 2.95x | react_ts, python_api, prisma, mt5, scraper, cron | (compacted prisma emitter) |
| examples/cron/monitor_and_alert.ainl | non-strict-only | 73 | 0.513 | 26 | 95 | 40 | 177 | 85 | 98 | 521 | 7.14x | react_ts, python_api, prisma, mt5, scraper, cron | (compacted prisma emitter); (compacted react_ts emitter) |
| examples/crud_api.ainl | strict-valid | 37 | 0.503 | 26 | 95 | 40 | 177 | 85 | 0 | 423 | 11.43x | react_ts, python_api, prisma, mt5, scraper, cron | (compacted prisma emitter); (compacted react_ts emitter) |
| examples/ecom.lang | non-strict-only | 238 | 0.859 | 186 | 128 | 80 | 233 | 85 | 0 | 712 | 2.99x | react_ts, python_api, prisma, mt5, scraper, cron | (compacted prisma emitter) |
| examples/golden/01_web_server.ainl | non-strict-only | 595 | 2.251 | 26 | 95 | 81 | 197 | 85 | 0 | 484 | 0.81x | react_ts, python_api, prisma, mt5, scraper, cron | (compacted prisma emitter); (compacted react_ts emitter) |
| examples/golden/02_dashboard.ainl | non-strict-only | 710 | 2.891 | 26 | 95 | 78 | 191 | 85 | 0 | 475 | 0.67x | react_ts, python_api, prisma, mt5, scraper, cron | (compacted prisma emitter); (compacted react_ts emitter) |
| examples/golden/03_scraper.ainl | non-strict-only | 713 | 2.688 | 26 | 95 | 79 | 192 | 85 | 0 | 477 | 0.67x | react_ts, python_api, prisma, mt5, scraper, cron | (compacted prisma emitter); (compacted react_ts emitter) |
| examples/golden/04_alerting_monitor.ainl | non-strict-only | 714 | 2.816 | 26 | 95 | 79 | 192 | 85 | 0 | 477 | 0.67x | react_ts, python_api, prisma, mt5, scraper, cron | (compacted prisma emitter); (compacted react_ts emitter) |
| examples/golden/05_file_processor.ainl | non-strict-only | 838 | 2.685 | 26 | 95 | 82 | 199 | 85 | 0 | 487 | 0.58x | react_ts, python_api, prisma, mt5, scraper, cron | (compacted prisma emitter); (compacted react_ts emitter) |
| examples/hello.ainl | strict-valid | 18 | 0.205 | 26 | 95 | 40 | 177 | 85 | 0 | 423 | 23.50x | react_ts, python_api, prisma, mt5, scraper, cron | (compacted prisma emitter); (compacted react_ts emitter) |
| examples/if_call_workflow.ainl | strict-valid | 83 | 0.784 | 26 | 95 | 40 | 177 | 85 | 0 | 423 | 5.10x | react_ts, python_api, prisma, mt5, scraper, cron | (compacted prisma emitter); (compacted react_ts emitter) |
| examples/integrations/executor_bridge_adapter_min.ainl | non-strict-only | 226 | 0.711 | 26 | 95 | 40 | 177 | 85 | 0 | 423 | 1.87x | react_ts, python_api, prisma, mt5, scraper, cron | (compacted prisma emitter); (compacted react_ts emitter) |
| examples/integrations/executor_bridge_min.ainl | non-strict-only | 241 | 0.713 | 26 | 95 | 40 | 177 | 85 | 0 | 423 | 1.76x | react_ts, python_api, prisma, mt5, scraper, cron | (compacted prisma emitter); (compacted react_ts emitter) |
| examples/internal_tool.lang | non-strict-only | 227 | 1.282 | 148 | 128 | 85 | 243 | 85 | 98 | 787 | 3.47x | react_ts, python_api, prisma, mt5, scraper, cron | (compacted prisma emitter) |
| examples/monitor_escalation.ainl | strict-valid | 72 | 0.547 | 26 | 95 | 40 | 177 | 85 | 98 | 521 | 7.24x | react_ts, python_api, prisma, mt5, scraper, cron | (compacted prisma emitter); (compacted react_ts emitter) |
| examples/openclaw/agent_read_result.lang | non-strict-only | 109 | 0.235 | 26 | 95 | 40 | 177 | 85 | 0 | 423 | 3.88x | react_ts, python_api, prisma, mt5, scraper, cron | (legacy excluded from viable); (compacted prisma emitter); (compacted react_ts emitter) |
| examples/openclaw/agent_send_task.lang | non-strict-only | 349 | 0.830 | 26 | 95 | 40 | 177 | 85 | 0 | 423 | 1.21x | react_ts, python_api, prisma, mt5, scraper, cron | (legacy excluded from viable); (compacted prisma emitter); (compacted react_ts emitter) |
| examples/openclaw/backup_manager.lang | non-strict-only | 485 | 3.504 | 26 | 95 | 78 | 192 | 85 | 0 | 476 | 0.98x | react_ts, python_api, prisma, mt5, scraper, cron | (legacy excluded from viable); (compacted prisma emitter); (compacted react_ts emitter) |
| examples/openclaw/daily_digest.lang | non-strict-only | 283 | 2.062 | 26 | 95 | 78 | 191 | 85 | 0 | 475 | 1.68x | react_ts, python_api, prisma, mt5, scraper, cron | (compacted prisma emitter); (compacted react_ts emitter) |
| examples/openclaw/daily_digest.strict.lang | non-strict-only | 565 | 3.189 | 26 | 95 | 101 | 227 | 85 | 0 | 534 | 0.95x | react_ts, python_api, prisma, mt5, scraper, cron | (compacted react_ts emitter) |
| examples/openclaw/daily_lead_summary.lang | non-strict-only | 147 | 0.973 | 26 | 95 | 79 | 192 | 85 | 0 | 477 | 3.24x | react_ts, python_api, prisma, mt5, scraper, cron | (compacted prisma emitter); (compacted react_ts emitter) |
| examples/openclaw/infrastructure_watchdog.lang | non-strict-only | 419 | 3.040 | 26 | 95 | 79 | 192 | 85 | 0 | 477 | 1.14x | react_ts, python_api, prisma, mt5, scraper, cron | (compacted prisma emitter); (compacted react_ts emitter) |
| examples/openclaw/lead_enrichment.lang | non-strict-only | 368 | 2.653 | 26 | 95 | 40 | 177 | 85 | 0 | 423 | 1.15x | react_ts, python_api, prisma, mt5, scraper, cron | (legacy excluded from viable); (compacted prisma emitter); (compacted react_ts emitter) |
| examples/openclaw/memory_daily_log_note.lang | non-strict-only | 349 | 1.182 | 26 | 95 | 40 | 177 | 85 | 0 | 423 | 1.21x | react_ts, python_api, prisma, mt5, scraper, cron | (legacy excluded from viable); (compacted prisma emitter); (compacted react_ts emitter) |
| examples/openclaw/memory_token_cost_state.lang | non-strict-only | 361 | 1.225 | 26 | 95 | 40 | 177 | 85 | 0 | 423 | 1.17x | react_ts, python_api, prisma, mt5, scraper, cron | (legacy excluded from viable); (compacted prisma emitter); (compacted react_ts emitter) |
| examples/openclaw/monitor_status_advice_read.lang | non-strict-only | 121 | 0.404 | 26 | 95 | 40 | 177 | 85 | 0 | 423 | 3.50x | react_ts, python_api, prisma, mt5, scraper, cron | (legacy excluded from viable); (compacted prisma emitter); (compacted react_ts emitter) |
| examples/openclaw/monitor_status_advice_request.lang | non-strict-only | 626 | 1.434 | 26 | 95 | 40 | 177 | 85 | 0 | 423 | 0.68x | react_ts, python_api, prisma, mt5, scraper, cron | (legacy excluded from viable); (compacted prisma emitter); (compacted react_ts emitter) |
| examples/openclaw/token_cost_advice_read.lang | non-strict-only | 119 | 0.269 | 26 | 95 | 40 | 177 | 85 | 0 | 423 | 3.55x | react_ts, python_api, prisma, mt5, scraper, cron | (legacy excluded from viable); (compacted prisma emitter); (compacted react_ts emitter) |
| examples/openclaw/token_cost_advice_request.lang | non-strict-only | 418 | 0.984 | 26 | 95 | 40 | 177 | 85 | 0 | 423 | 1.01x | react_ts, python_api, prisma, mt5, scraper, cron | (legacy excluded from viable); (compacted prisma emitter); (compacted react_ts emitter) |
| examples/openclaw/webhook_handler.lang | non-strict-only | 306 | 1.690 | 26 | 107 | 62 | 211 | 85 | 0 | 491 | 1.60x | react_ts, python_api, prisma, mt5, scraper, cron | (compacted prisma emitter); (compacted react_ts emitter) |
| examples/rag_pipeline.ainl | strict-valid | 29 | 0.356 | 26 | 95 | 40 | 177 | 85 | 0 | 423 | 14.59x | react_ts, python_api, prisma, mt5, scraper, cron | (compacted prisma emitter); (compacted react_ts emitter) |
| examples/retry_error_resilience.ainl | strict-valid | 54 | 0.537 | 26 | 95 | 40 | 177 | 85 | 0 | 423 | 7.83x | react_ts, python_api, prisma, mt5, scraper, cron | (compacted prisma emitter); (compacted react_ts emitter) |
| examples/scraper/basic_scraper.ainl | strict-valid | 67 | 0.350 | 26 | 95 | 40 | 177 | 154 | 99 | 591 | 8.82x | react_ts, python_api, prisma, mt5, scraper, cron | (compacted prisma emitter); (compacted react_ts emitter) |
| examples/status_branching.ainl | strict-valid | 48 | 0.468 | 26 | 95 | 40 | 177 | 85 | 0 | 423 | 8.81x | react_ts, python_api, prisma, mt5, scraper, cron | (compacted prisma emitter); (compacted react_ts emitter) |
| examples/ticketing.lang | non-strict-only | 274 | 1.092 | 183 | 152 | 84 | 239 | 85 | 0 | 743 | 2.71x | react_ts, python_api, prisma, mt5, scraper, cron | (compacted prisma emitter) |
| examples/web/basic_web_api.ainl | strict-valid | 32 | 0.227 | 26 | 106 | 40 | 177 | 85 | 0 | 434 | 13.56x | react_ts, python_api, prisma, mt5, scraper, cron | (compacted prisma emitter); (compacted react_ts emitter) |
| examples/webhook_automation.ainl | strict-valid | 66 | 0.593 | 26 | 95 | 40 | 177 | 85 | 0 | 423 | 6.41x | react_ts, python_api, prisma, mt5, scraper, cron | (compacted prisma emitter); (compacted react_ts emitter) |

*Token counts via tiktoken **cl100k_base**. Minimal_emit **fallback** stubs are typically ~20–30 tk.*

### compatibility_only
| Artifact | Class | AINL source (tk) | Compile ms (mean×3) | React/TS (tk) | Python API (tk) | Prisma (tk) | MT5 (tk) | Scraper (tk) | Cron (tk) | Aggregate Σ (tk) | Ratio (tk) | Included targets | Notes |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---|
| examples/api_only.lang | non-strict-only | 107 | 0.735 | 26 | 128 | 76 | 219 | 85 | 0 | 534 | 4.99x | react_ts, python_api, prisma, mt5, scraper, cron | (compacted prisma emitter); (compacted react_ts emitter) |
| examples/autonomous_ops/backup_freshness_to_queue.lang | non-strict-only | 192 | 1.067 | 26 | 95 | 40 | 177 | 85 | 0 | 423 | 2.20x | react_ts, python_api, prisma, mt5, scraper, cron | (legacy excluded from viable); (compacted prisma emitter); (compacted react_ts emitter) |
| examples/autonomous_ops/canary_sampler.lang | non-strict-only | 1370 | 5.933 | 26 | 95 | 40 | 177 | 85 | 98 | 521 | 0.38x | react_ts, python_api, prisma, mt5, scraper, cron | (compacted prisma emitter); (compacted react_ts emitter) |
| examples/autonomous_ops/duplicate_detection.lang | non-strict-only | 625 | 1.249 | 26 | 95 | 68 | 202 | 85 | 0 | 476 | 0.76x | react_ts, python_api, prisma, mt5, scraper, cron | (compacted prisma emitter); (compacted react_ts emitter) |
| examples/autonomous_ops/infrastructure_watchdog.lang | non-strict-only | 2222 | 4.897 | 26 | 95 | 40 | 177 | 85 | 98 | 521 | 0.23x | react_ts, python_api, prisma, mt5, scraper, cron | (compacted prisma emitter); (compacted react_ts emitter) |
| examples/autonomous_ops/invoice_aging.lang | non-strict-only | 384 | 0.843 | 26 | 95 | 69 | 204 | 85 | 0 | 479 | 1.25x | react_ts, python_api, prisma, mt5, scraper, cron | (compacted prisma emitter); (compacted react_ts emitter) |
| examples/autonomous_ops/lead_aging.lang | non-strict-only | 404 | 0.894 | 26 | 95 | 73 | 210 | 85 | 0 | 489 | 1.21x | react_ts, python_api, prisma, mt5, scraper, cron | (compacted prisma emitter); (compacted react_ts emitter) |
| examples/autonomous_ops/lead_quality_audit.lang | non-strict-only | 1417 | 3.714 | 26 | 95 | 40 | 177 | 85 | 99 | 522 | 0.37x | react_ts, python_api, prisma, mt5, scraper, cron | (compacted prisma emitter); (compacted react_ts emitter) |
| examples/autonomous_ops/lead_score_drift.lang | non-strict-only | 642 | 1.019 | 26 | 95 | 66 | 197 | 85 | 0 | 469 | 0.73x | react_ts, python_api, prisma, mt5, scraper, cron | (compacted prisma emitter); (compacted react_ts emitter) |
| examples/autonomous_ops/memory_prune.lang | non-strict-only | 220 | 0.470 | 26 | 95 | 40 | 177 | 85 | 99 | 522 | 2.37x | react_ts, python_api, prisma, mt5, scraper, cron | (compacted prisma emitter); (compacted react_ts emitter) |
| examples/autonomous_ops/meta_monitor.lang | non-strict-only | 498 | 1.201 | 26 | 95 | 40 | 177 | 85 | 98 | 521 | 1.05x | react_ts, python_api, prisma, mt5, scraper, cron | (compacted prisma emitter); (compacted react_ts emitter) |
| examples/autonomous_ops/missing_fields.lang | non-strict-only | 631 | 1.699 | 26 | 95 | 68 | 202 | 85 | 0 | 476 | 0.75x | react_ts, python_api, prisma, mt5, scraper, cron | (compacted prisma emitter); (compacted react_ts emitter) |
| examples/autonomous_ops/monitor_system.lang | non-strict-only | 2117 | 16.301 | 26 | 95 | 127 | 257 | 85 | 0 | 590 | 0.28x | react_ts, python_api, prisma, mt5, scraper, cron | (compacted react_ts emitter) |
| examples/autonomous_ops/pipeline_readiness_snapshot.lang | non-strict-only | 216 | 1.284 | 26 | 95 | 40 | 177 | 85 | 0 | 423 | 1.96x | react_ts, python_api, prisma, mt5, scraper, cron | (legacy excluded from viable); (compacted prisma emitter); (compacted react_ts emitter) |
| examples/autonomous_ops/revenue_forecast.lang | non-strict-only | 454 | 0.978 | 26 | 95 | 69 | 204 | 85 | 0 | 479 | 1.06x | react_ts, python_api, prisma, mt5, scraper, cron | (compacted prisma emitter); (compacted react_ts emitter) |
| examples/autonomous_ops/service_health_trends.lang | non-strict-only | 1042 | 4.290 | 26 | 95 | 60 | 186 | 85 | 0 | 452 | 0.43x | react_ts, python_api, prisma, mt5, scraper, cron | (compacted prisma emitter); (compacted react_ts emitter) |
| examples/autonomous_ops/session_continuity.lang | non-strict-only | 1026 | 1.937 | 26 | 95 | 40 | 177 | 85 | 99 | 522 | 0.51x | react_ts, python_api, prisma, mt5, scraper, cron | (compacted prisma emitter); (compacted react_ts emitter) |
| examples/autonomous_ops/status_snapshot_to_queue.lang | non-strict-only | 214 | 1.258 | 26 | 95 | 40 | 177 | 85 | 0 | 423 | 1.98x | react_ts, python_api, prisma, mt5, scraper, cron | (legacy excluded from viable); (compacted prisma emitter); (compacted react_ts emitter) |
| examples/autonomous_ops/tiktok_health.lang | non-strict-only | 293 | 0.621 | 26 | 95 | 65 | 195 | 85 | 0 | 466 | 1.59x | react_ts, python_api, prisma, mt5, scraper, cron | (compacted prisma emitter); (compacted react_ts emitter) |
| examples/autonomous_ops/tiktok_sla_monitor.lang | non-strict-only | 1019 | 3.623 | 26 | 95 | 40 | 177 | 85 | 98 | 521 | 0.51x | react_ts, python_api, prisma, mt5, scraper, cron | (compacted prisma emitter); (compacted react_ts emitter) |
| examples/autonomous_ops/token_budget_tracker.lang | non-strict-only | 1089 | 3.121 | 26 | 95 | 40 | 177 | 85 | 98 | 521 | 0.48x | react_ts, python_api, prisma, mt5, scraper, cron | (compacted prisma emitter); (compacted react_ts emitter) |
| examples/autonomous_ops/token_cost_tracker.lang | non-strict-only | 1266 | 2.793 | 26 | 95 | 40 | 177 | 85 | 98 | 521 | 0.41x | react_ts, python_api, prisma, mt5, scraper, cron | (compacted prisma emitter); (compacted react_ts emitter) |
| examples/blog.lang | non-strict-only | 237 | 0.976 | 150 | 139 | 88 | 238 | 85 | 0 | 700 | 2.95x | react_ts, python_api, prisma, mt5, scraper, cron | (compacted prisma emitter) |
| examples/cron/monitor_and_alert.ainl | non-strict-only | 73 | 0.490 | 26 | 95 | 40 | 177 | 85 | 98 | 521 | 7.14x | react_ts, python_api, prisma, mt5, scraper, cron | (compacted prisma emitter); (compacted react_ts emitter) |
| examples/ecom.lang | non-strict-only | 238 | 0.825 | 186 | 128 | 80 | 233 | 85 | 0 | 712 | 2.99x | react_ts, python_api, prisma, mt5, scraper, cron | (compacted prisma emitter) |
| examples/golden/01_web_server.ainl | non-strict-only | 595 | 2.336 | 26 | 95 | 81 | 197 | 85 | 0 | 484 | 0.81x | react_ts, python_api, prisma, mt5, scraper, cron | (compacted prisma emitter); (compacted react_ts emitter) |
| examples/golden/02_dashboard.ainl | non-strict-only | 710 | 3.026 | 26 | 95 | 78 | 191 | 85 | 0 | 475 | 0.67x | react_ts, python_api, prisma, mt5, scraper, cron | (compacted prisma emitter); (compacted react_ts emitter) |
| examples/golden/03_scraper.ainl | non-strict-only | 713 | 2.708 | 26 | 95 | 79 | 192 | 85 | 0 | 477 | 0.67x | react_ts, python_api, prisma, mt5, scraper, cron | (compacted prisma emitter); (compacted react_ts emitter) |
| examples/golden/04_alerting_monitor.ainl | non-strict-only | 714 | 2.837 | 26 | 95 | 79 | 192 | 85 | 0 | 477 | 0.67x | react_ts, python_api, prisma, mt5, scraper, cron | (compacted prisma emitter); (compacted react_ts emitter) |
| examples/golden/05_file_processor.ainl | non-strict-only | 838 | 2.689 | 26 | 95 | 82 | 199 | 85 | 0 | 487 | 0.58x | react_ts, python_api, prisma, mt5, scraper, cron | (compacted prisma emitter); (compacted react_ts emitter) |
| examples/integrations/executor_bridge_adapter_min.ainl | non-strict-only | 226 | 0.709 | 26 | 95 | 40 | 177 | 85 | 0 | 423 | 1.87x | react_ts, python_api, prisma, mt5, scraper, cron | (compacted prisma emitter); (compacted react_ts emitter) |
| examples/integrations/executor_bridge_min.ainl | non-strict-only | 241 | 0.715 | 26 | 95 | 40 | 177 | 85 | 0 | 423 | 1.76x | react_ts, python_api, prisma, mt5, scraper, cron | (compacted prisma emitter); (compacted react_ts emitter) |
| examples/internal_tool.lang | non-strict-only | 227 | 0.776 | 148 | 128 | 85 | 243 | 85 | 98 | 787 | 3.47x | react_ts, python_api, prisma, mt5, scraper, cron | (compacted prisma emitter) |
| examples/openclaw/agent_read_result.lang | non-strict-only | 109 | 0.231 | 26 | 95 | 40 | 177 | 85 | 0 | 423 | 3.88x | react_ts, python_api, prisma, mt5, scraper, cron | (legacy excluded from viable); (compacted prisma emitter); (compacted react_ts emitter) |
| examples/openclaw/agent_send_task.lang | non-strict-only | 349 | 0.756 | 26 | 95 | 40 | 177 | 85 | 0 | 423 | 1.21x | react_ts, python_api, prisma, mt5, scraper, cron | (legacy excluded from viable); (compacted prisma emitter); (compacted react_ts emitter) |
| examples/openclaw/backup_manager.lang | non-strict-only | 485 | 3.492 | 26 | 95 | 78 | 192 | 85 | 0 | 476 | 0.98x | react_ts, python_api, prisma, mt5, scraper, cron | (legacy excluded from viable); (compacted prisma emitter); (compacted react_ts emitter) |
| examples/openclaw/daily_digest.lang | non-strict-only | 283 | 2.125 | 26 | 95 | 78 | 191 | 85 | 0 | 475 | 1.68x | react_ts, python_api, prisma, mt5, scraper, cron | (compacted prisma emitter); (compacted react_ts emitter) |
| examples/openclaw/daily_digest.strict.lang | non-strict-only | 565 | 3.080 | 26 | 95 | 101 | 227 | 85 | 0 | 534 | 0.95x | react_ts, python_api, prisma, mt5, scraper, cron | (compacted react_ts emitter) |
| examples/openclaw/daily_lead_summary.lang | non-strict-only | 147 | 0.904 | 26 | 95 | 79 | 192 | 85 | 0 | 477 | 3.24x | react_ts, python_api, prisma, mt5, scraper, cron | (compacted prisma emitter); (compacted react_ts emitter) |
| examples/openclaw/infrastructure_watchdog.lang | non-strict-only | 419 | 2.755 | 26 | 95 | 79 | 192 | 85 | 0 | 477 | 1.14x | react_ts, python_api, prisma, mt5, scraper, cron | (compacted prisma emitter); (compacted react_ts emitter) |
| examples/openclaw/lead_enrichment.lang | non-strict-only | 368 | 2.349 | 26 | 95 | 40 | 177 | 85 | 0 | 423 | 1.15x | react_ts, python_api, prisma, mt5, scraper, cron | (legacy excluded from viable); (compacted prisma emitter); (compacted react_ts emitter) |
| examples/openclaw/memory_daily_log_note.lang | non-strict-only | 349 | 1.154 | 26 | 95 | 40 | 177 | 85 | 0 | 423 | 1.21x | react_ts, python_api, prisma, mt5, scraper, cron | (legacy excluded from viable); (compacted prisma emitter); (compacted react_ts emitter) |
| examples/openclaw/memory_token_cost_state.lang | non-strict-only | 361 | 1.118 | 26 | 95 | 40 | 177 | 85 | 0 | 423 | 1.17x | react_ts, python_api, prisma, mt5, scraper, cron | (legacy excluded from viable); (compacted prisma emitter); (compacted react_ts emitter) |
| examples/openclaw/monitor_status_advice_read.lang | non-strict-only | 121 | 0.375 | 26 | 95 | 40 | 177 | 85 | 0 | 423 | 3.50x | react_ts, python_api, prisma, mt5, scraper, cron | (legacy excluded from viable); (compacted prisma emitter); (compacted react_ts emitter) |
| examples/openclaw/monitor_status_advice_request.lang | non-strict-only | 626 | 1.292 | 26 | 95 | 40 | 177 | 85 | 0 | 423 | 0.68x | react_ts, python_api, prisma, mt5, scraper, cron | (legacy excluded from viable); (compacted prisma emitter); (compacted react_ts emitter) |
| examples/openclaw/token_cost_advice_read.lang | non-strict-only | 119 | 0.236 | 26 | 95 | 40 | 177 | 85 | 0 | 423 | 3.55x | react_ts, python_api, prisma, mt5, scraper, cron | (legacy excluded from viable); (compacted prisma emitter); (compacted react_ts emitter) |
| examples/openclaw/token_cost_advice_request.lang | non-strict-only | 418 | 0.909 | 26 | 95 | 40 | 177 | 85 | 0 | 423 | 1.01x | react_ts, python_api, prisma, mt5, scraper, cron | (legacy excluded from viable); (compacted prisma emitter); (compacted react_ts emitter) |
| examples/openclaw/webhook_handler.lang | non-strict-only | 306 | 1.545 | 26 | 107 | 62 | 211 | 85 | 0 | 491 | 1.60x | react_ts, python_api, prisma, mt5, scraper, cron | (compacted prisma emitter); (compacted react_ts emitter) |
| examples/ticketing.lang | non-strict-only | 274 | 1.110 | 183 | 152 | 84 | 239 | 85 | 0 | 743 | 2.71x | react_ts, python_api, prisma, mt5, scraper, cron | (compacted prisma emitter) |

*Token counts via tiktoken **cl100k_base**. Minimal_emit **fallback** stubs are typically ~20–30 tk.*

## Details (minimal_emit)

| Profile | Viable artifacts | AINL source Σ (tk, viable) | Aggregate Σ (tk, viable) | Ratio (tk, viable) | Excluded legacy |
|---|---:|---:|---:|---:|---:|
| canonical_strict_valid | 10 | 506 | 1122 | 2.22x | 0 |
| public_mixed | 24 | 3762 | 3822 | 1.02x | 35 |
| compatibility_only | 14 | 3256 | 2700 | 0.83x | 35 |

### canonical_strict_valid
| Artifact | Class | AINL source (tk) | Compile ms (mean×3) | React/TS (tk) | Python API (tk) | Prisma (tk) | MT5 (tk) | Scraper (tk) | Cron (tk) | Aggregate Σ (tk) | Ratio (tk) | Included targets | Notes |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---|
| examples/crud_api.ainl | strict-valid | 37 | 0.485 | — | 95 | — | — | — | — | 95 | 2.57x | python_api |  |
| examples/hello.ainl | strict-valid | 18 | 0.195 | — | 95 | — | — | — | — | 95 | 5.28x | python_api |  |
| examples/if_call_workflow.ainl | strict-valid | 83 | 0.772 | — | 95 | — | — | — | — | 95 | 1.14x | python_api |  |
| examples/monitor_escalation.ainl | strict-valid | 72 | 0.525 | — | — | — | — | — | 98 | 98 | 1.36x | cron |  |
| examples/rag_pipeline.ainl | strict-valid | 29 | 0.337 | — | 95 | — | — | — | — | 95 | 3.28x | python_api |  |
| examples/retry_error_resilience.ainl | strict-valid | 54 | 0.546 | — | 95 | — | — | — | — | 95 | 1.76x | python_api |  |
| examples/scraper/basic_scraper.ainl | strict-valid | 67 | 0.313 | — | — | — | — | 154 | 99 | 253 | 3.78x | scraper, cron |  |
| examples/status_branching.ainl | strict-valid | 48 | 0.455 | — | 95 | — | — | — | — | 95 | 1.98x | python_api |  |
| examples/web/basic_web_api.ainl | strict-valid | 32 | 0.215 | — | 106 | — | — | — | — | 106 | 3.31x | python_api |  |
| examples/webhook_automation.ainl | strict-valid | 66 | 0.551 | — | 95 | — | — | — | — | 95 | 1.44x | python_api |  |

*Token counts via tiktoken **cl100k_base**. Minimal_emit **fallback** stubs are typically ~20–30 tk.*

### public_mixed
| Artifact | Class | AINL source (tk) | Compile ms (mean×3) | React/TS (tk) | Python API (tk) | Prisma (tk) | MT5 (tk) | Scraper (tk) | Cron (tk) | Aggregate Σ (tk) | Ratio (tk) | Included targets | Notes |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---|
| examples/api_only.lang | non-strict-only | 107 | 0.627 | — | 128 | 76 | — | — | — | 204 | 1.91x | python_api, prisma | (compacted prisma emitter) |
| examples/autonomous_ops/backup_freshness_to_queue.lang | non-strict-only | 192 | 1.584 | — | 34 | — | — | — | 0 | 34 | 0.18x | cron, python_api | (fallback stub); (legacy excluded from viable) |
| examples/autonomous_ops/canary_sampler.lang | non-strict-only | 1370 | 5.654 | — | — | — | — | — | 98 | 98 | 0.07x | cron | (legacy excluded from viable) |
| examples/autonomous_ops/duplicate_detection.lang | non-strict-only | 625 | 1.333 | — | — | 68 | — | — | — | 68 | 0.11x | prisma | (legacy excluded from viable); (compacted prisma emitter) |
| examples/autonomous_ops/infrastructure_watchdog.lang | non-strict-only | 2222 | 5.438 | — | — | — | — | — | 98 | 98 | 0.04x | cron | (legacy excluded from viable) |
| examples/autonomous_ops/invoice_aging.lang | non-strict-only | 384 | 0.872 | — | — | 69 | — | — | — | 69 | 0.18x | prisma | (compacted prisma emitter) |
| examples/autonomous_ops/lead_aging.lang | non-strict-only | 404 | 0.868 | — | — | 73 | — | — | — | 73 | 0.18x | prisma | (legacy excluded from viable); (compacted prisma emitter) |
| examples/autonomous_ops/lead_quality_audit.lang | non-strict-only | 1417 | 3.675 | — | — | — | — | — | 99 | 99 | 0.07x | cron | (legacy excluded from viable) |
| examples/autonomous_ops/lead_score_drift.lang | non-strict-only | 642 | 0.983 | — | — | 66 | — | — | — | 66 | 0.10x | prisma | (legacy excluded from viable); (compacted prisma emitter) |
| examples/autonomous_ops/memory_prune.lang | non-strict-only | 220 | 0.441 | — | — | — | — | — | 99 | 99 | 0.45x | cron |  |
| examples/autonomous_ops/meta_monitor.lang | non-strict-only | 498 | 1.129 | — | — | — | — | — | 98 | 98 | 0.20x | cron | (legacy excluded from viable) |
| examples/autonomous_ops/missing_fields.lang | non-strict-only | 631 | 1.605 | — | — | 68 | — | — | — | 68 | 0.11x | prisma | (legacy excluded from viable); (compacted prisma emitter) |
| examples/autonomous_ops/monitor_system.lang | non-strict-only | 2117 | 14.679 | — | — | 127 | — | — | 0 | 127 | 0.06x | prisma, cron | (legacy excluded from viable) |
| examples/autonomous_ops/pipeline_readiness_snapshot.lang | non-strict-only | 216 | 1.240 | — | 34 | — | — | — | 0 | 34 | 0.16x | cron, python_api | (fallback stub); (legacy excluded from viable) |
| examples/autonomous_ops/revenue_forecast.lang | non-strict-only | 454 | 0.981 | — | — | 69 | — | — | — | 69 | 0.15x | prisma | (legacy excluded from viable); (compacted prisma emitter) |
| examples/autonomous_ops/service_health_trends.lang | non-strict-only | 1042 | 4.151 | — | 95 | 60 | — | — | — | 155 | 0.15x | python_api, prisma | (legacy excluded from viable); (compacted prisma emitter) |
| examples/autonomous_ops/session_continuity.lang | non-strict-only | 1026 | 1.714 | — | — | — | — | — | 99 | 99 | 0.10x | cron | (legacy excluded from viable) |
| examples/autonomous_ops/status_snapshot_to_queue.lang | non-strict-only | 214 | 1.246 | — | 34 | — | — | — | 0 | 34 | 0.16x | cron, python_api | (fallback stub); (legacy excluded from viable) |
| examples/autonomous_ops/tiktok_health.lang | non-strict-only | 293 | 0.631 | — | — | 65 | — | — | — | 65 | 0.22x | prisma | (compacted prisma emitter) |
| examples/autonomous_ops/tiktok_sla_monitor.lang | non-strict-only | 1019 | 3.481 | — | — | — | — | — | 98 | 98 | 0.10x | cron | (legacy excluded from viable) |
| examples/autonomous_ops/token_budget_tracker.lang | non-strict-only | 1089 | 2.154 | — | — | — | — | — | 98 | 98 | 0.09x | cron | (legacy excluded from viable) |
| examples/autonomous_ops/token_cost_tracker.lang | non-strict-only | 1266 | 2.478 | — | — | — | — | — | 98 | 98 | 0.08x | cron | (legacy excluded from viable) |
| examples/blog.lang | non-strict-only | 237 | 0.930 | 150 | 139 | 88 | — | — | — | 377 | 1.59x | react_ts, python_api, prisma | (compacted prisma emitter) |
| examples/cron/monitor_and_alert.ainl | non-strict-only | 73 | 0.498 | — | — | — | — | — | 98 | 98 | 1.34x | cron |  |
| examples/crud_api.ainl | strict-valid | 37 | 0.508 | — | 95 | — | — | — | — | 95 | 2.57x | python_api |  |
| examples/ecom.lang | non-strict-only | 238 | 0.831 | 186 | 128 | 80 | — | — | — | 394 | 1.66x | react_ts, python_api, prisma | (compacted prisma emitter) |
| examples/golden/01_web_server.ainl | non-strict-only | 595 | 2.228 | — | — | 81 | — | — | 0 | 81 | 0.14x | prisma, cron | (legacy excluded from viable); (compacted prisma emitter) |
| examples/golden/02_dashboard.ainl | non-strict-only | 710 | 3.024 | — | — | 78 | — | — | 0 | 78 | 0.11x | prisma, cron | (legacy excluded from viable); (compacted prisma emitter) |
| examples/golden/03_scraper.ainl | non-strict-only | 713 | 2.687 | — | — | 79 | — | — | 0 | 79 | 0.11x | prisma, cron | (legacy excluded from viable); (compacted prisma emitter) |
| examples/golden/04_alerting_monitor.ainl | non-strict-only | 714 | 2.757 | — | — | 79 | — | — | 0 | 79 | 0.11x | prisma, cron | (legacy excluded from viable); (compacted prisma emitter) |
| examples/golden/05_file_processor.ainl | non-strict-only | 838 | 2.645 | — | — | 82 | — | — | 0 | 82 | 0.10x | prisma, cron | (legacy excluded from viable); (compacted prisma emitter) |
| examples/hello.ainl | strict-valid | 18 | 0.200 | — | 95 | — | — | — | — | 95 | 5.28x | python_api |  |
| examples/if_call_workflow.ainl | strict-valid | 83 | 0.775 | — | 95 | — | — | — | — | 95 | 1.14x | python_api |  |
| examples/integrations/executor_bridge_adapter_min.ainl | non-strict-only | 226 | 0.736 | — | 95 | — | — | — | — | 95 | 0.42x | python_api |  |
| examples/integrations/executor_bridge_min.ainl | non-strict-only | 241 | 0.736 | — | 95 | — | — | — | — | 95 | 0.39x | python_api |  |
| examples/internal_tool.lang | non-strict-only | 227 | 0.794 | 148 | 128 | 85 | — | — | 98 | 459 | 2.02x | react_ts, python_api, prisma, cron | (compacted prisma emitter) |
| examples/monitor_escalation.ainl | strict-valid | 72 | 0.530 | — | — | — | — | — | 98 | 98 | 1.36x | cron |  |
| examples/openclaw/agent_read_result.lang | non-strict-only | 109 | 0.238 | — | 95 | — | — | — | — | 95 | 0.87x | python_api | (legacy excluded from viable) |
| examples/openclaw/agent_send_task.lang | non-strict-only | 349 | 0.758 | — | 95 | — | — | — | — | 95 | 0.27x | python_api | (legacy excluded from viable) |
| examples/openclaw/backup_manager.lang | non-strict-only | 485 | 3.460 | — | — | 78 | — | — | 0 | 78 | 0.16x | prisma, cron | (legacy excluded from viable); (compacted prisma emitter) |
| examples/openclaw/daily_digest.lang | non-strict-only | 283 | 2.034 | — | — | 78 | — | — | 0 | 78 | 0.28x | prisma, cron | (compacted prisma emitter) |
| examples/openclaw/daily_digest.strict.lang | non-strict-only | 565 | 3.138 | — | — | 101 | — | — | 0 | 101 | 0.18x | prisma, cron | (legacy excluded from viable) |
| examples/openclaw/daily_lead_summary.lang | non-strict-only | 147 | 0.984 | — | — | 79 | — | — | 0 | 79 | 0.54x | prisma, cron | (compacted prisma emitter) |
| examples/openclaw/infrastructure_watchdog.lang | non-strict-only | 419 | 2.818 | — | — | 79 | — | — | 0 | 79 | 0.19x | prisma, cron | (legacy excluded from viable); (compacted prisma emitter) |
| examples/openclaw/lead_enrichment.lang | non-strict-only | 368 | 2.431 | — | 34 | — | — | — | 0 | 34 | 0.09x | cron, python_api | (fallback stub); (legacy excluded from viable) |
| examples/openclaw/memory_daily_log_note.lang | non-strict-only | 349 | 1.246 | — | 95 | — | — | — | — | 95 | 0.27x | python_api | (legacy excluded from viable) |
| examples/openclaw/memory_token_cost_state.lang | non-strict-only | 361 | 1.113 | — | 95 | — | — | — | — | 95 | 0.26x | python_api | (legacy excluded from viable) |
| examples/openclaw/monitor_status_advice_read.lang | non-strict-only | 121 | 0.406 | — | 95 | — | — | — | — | 95 | 0.79x | python_api | (legacy excluded from viable) |
| examples/openclaw/monitor_status_advice_request.lang | non-strict-only | 626 | 1.300 | — | 95 | — | — | — | — | 95 | 0.15x | python_api | (legacy excluded from viable) |
| examples/openclaw/token_cost_advice_read.lang | non-strict-only | 119 | 0.232 | — | 95 | — | — | — | — | 95 | 0.80x | python_api | (legacy excluded from viable) |
| examples/openclaw/token_cost_advice_request.lang | non-strict-only | 418 | 0.934 | — | 95 | — | — | — | — | 95 | 0.23x | python_api | (legacy excluded from viable) |
| examples/openclaw/webhook_handler.lang | non-strict-only | 306 | 1.546 | — | 107 | 62 | — | — | — | 169 | 0.55x | python_api, prisma | (compacted prisma emitter) |
| examples/rag_pipeline.ainl | strict-valid | 29 | 0.334 | — | 95 | — | — | — | — | 95 | 3.28x | python_api |  |
| examples/retry_error_resilience.ainl | strict-valid | 54 | 0.463 | — | 95 | — | — | — | — | 95 | 1.76x | python_api |  |
| examples/scraper/basic_scraper.ainl | strict-valid | 67 | 0.309 | — | — | — | — | 154 | 99 | 253 | 3.78x | scraper, cron |  |
| examples/status_branching.ainl | strict-valid | 48 | 0.457 | — | 95 | — | — | — | — | 95 | 1.98x | python_api |  |
| examples/ticketing.lang | non-strict-only | 274 | 1.139 | 183 | 152 | 84 | — | — | — | 419 | 1.53x | react_ts, python_api, prisma | (compacted prisma emitter) |
| examples/web/basic_web_api.ainl | strict-valid | 32 | 0.221 | — | 106 | — | — | — | — | 106 | 3.31x | python_api |  |
| examples/webhook_automation.ainl | strict-valid | 66 | 0.590 | — | 95 | — | — | — | — | 95 | 1.44x | python_api |  |

*Token counts via tiktoken **cl100k_base**. Minimal_emit **fallback** stubs are typically ~20–30 tk.*

### compatibility_only
| Artifact | Class | AINL source (tk) | Compile ms (mean×3) | React/TS (tk) | Python API (tk) | Prisma (tk) | MT5 (tk) | Scraper (tk) | Cron (tk) | Aggregate Σ (tk) | Ratio (tk) | Included targets | Notes |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---|
| examples/api_only.lang | non-strict-only | 107 | 0.624 | — | 128 | 76 | — | — | — | 204 | 1.91x | python_api, prisma | (compacted prisma emitter) |
| examples/autonomous_ops/backup_freshness_to_queue.lang | non-strict-only | 192 | 1.056 | — | 34 | — | — | — | 0 | 34 | 0.18x | cron, python_api | (fallback stub); (legacy excluded from viable) |
| examples/autonomous_ops/canary_sampler.lang | non-strict-only | 1370 | 5.572 | — | — | — | — | — | 98 | 98 | 0.07x | cron | (legacy excluded from viable) |
| examples/autonomous_ops/duplicate_detection.lang | non-strict-only | 625 | 1.219 | — | — | 68 | — | — | — | 68 | 0.11x | prisma | (legacy excluded from viable); (compacted prisma emitter) |
| examples/autonomous_ops/infrastructure_watchdog.lang | non-strict-only | 2222 | 4.818 | — | — | — | — | — | 98 | 98 | 0.04x | cron | (legacy excluded from viable) |
| examples/autonomous_ops/invoice_aging.lang | non-strict-only | 384 | 0.962 | — | — | 69 | — | — | — | 69 | 0.18x | prisma | (compacted prisma emitter) |
| examples/autonomous_ops/lead_aging.lang | non-strict-only | 404 | 0.850 | — | — | 73 | — | — | — | 73 | 0.18x | prisma | (legacy excluded from viable); (compacted prisma emitter) |
| examples/autonomous_ops/lead_quality_audit.lang | non-strict-only | 1417 | 4.573 | — | — | — | — | — | 99 | 99 | 0.07x | cron | (legacy excluded from viable) |
| examples/autonomous_ops/lead_score_drift.lang | non-strict-only | 642 | 1.029 | — | — | 66 | — | — | — | 66 | 0.10x | prisma | (legacy excluded from viable); (compacted prisma emitter) |
| examples/autonomous_ops/memory_prune.lang | non-strict-only | 220 | 0.452 | — | — | — | — | — | 99 | 99 | 0.45x | cron |  |
| examples/autonomous_ops/meta_monitor.lang | non-strict-only | 498 | 1.122 | — | — | — | — | — | 98 | 98 | 0.20x | cron | (legacy excluded from viable) |
| examples/autonomous_ops/missing_fields.lang | non-strict-only | 631 | 1.599 | — | — | 68 | — | — | — | 68 | 0.11x | prisma | (legacy excluded from viable); (compacted prisma emitter) |
| examples/autonomous_ops/monitor_system.lang | non-strict-only | 2117 | 15.347 | — | — | 127 | — | — | 0 | 127 | 0.06x | prisma, cron | (legacy excluded from viable) |
| examples/autonomous_ops/pipeline_readiness_snapshot.lang | non-strict-only | 216 | 1.295 | — | 34 | — | — | — | 0 | 34 | 0.16x | cron, python_api | (fallback stub); (legacy excluded from viable) |
| examples/autonomous_ops/revenue_forecast.lang | non-strict-only | 454 | 1.020 | — | — | 69 | — | — | — | 69 | 0.15x | prisma | (legacy excluded from viable); (compacted prisma emitter) |
| examples/autonomous_ops/service_health_trends.lang | non-strict-only | 1042 | 4.194 | — | 95 | 60 | — | — | — | 155 | 0.15x | python_api, prisma | (legacy excluded from viable); (compacted prisma emitter) |
| examples/autonomous_ops/session_continuity.lang | non-strict-only | 1026 | 2.312 | — | — | — | — | — | 99 | 99 | 0.10x | cron | (legacy excluded from viable) |
| examples/autonomous_ops/status_snapshot_to_queue.lang | non-strict-only | 214 | 1.216 | — | 34 | — | — | — | 0 | 34 | 0.16x | cron, python_api | (fallback stub); (legacy excluded from viable) |
| examples/autonomous_ops/tiktok_health.lang | non-strict-only | 293 | 0.654 | — | — | 65 | — | — | — | 65 | 0.22x | prisma | (compacted prisma emitter) |
| examples/autonomous_ops/tiktok_sla_monitor.lang | non-strict-only | 1019 | 3.710 | — | — | — | — | — | 98 | 98 | 0.10x | cron | (legacy excluded from viable) |
| examples/autonomous_ops/token_budget_tracker.lang | non-strict-only | 1089 | 2.257 | — | — | — | — | — | 98 | 98 | 0.09x | cron | (legacy excluded from viable) |
| examples/autonomous_ops/token_cost_tracker.lang | non-strict-only | 1266 | 2.719 | — | — | — | — | — | 98 | 98 | 0.08x | cron | (legacy excluded from viable) |
| examples/blog.lang | non-strict-only | 237 | 0.930 | 150 | 139 | 88 | — | — | — | 377 | 1.59x | react_ts, python_api, prisma | (compacted prisma emitter) |
| examples/cron/monitor_and_alert.ainl | non-strict-only | 73 | 0.521 | — | — | — | — | — | 98 | 98 | 1.34x | cron |  |
| examples/ecom.lang | non-strict-only | 238 | 0.880 | 186 | 128 | 80 | — | — | — | 394 | 1.66x | react_ts, python_api, prisma | (compacted prisma emitter) |
| examples/golden/01_web_server.ainl | non-strict-only | 595 | 2.227 | — | — | 81 | — | — | 0 | 81 | 0.14x | prisma, cron | (legacy excluded from viable); (compacted prisma emitter) |
| examples/golden/02_dashboard.ainl | non-strict-only | 710 | 2.891 | — | — | 78 | — | — | 0 | 78 | 0.11x | prisma, cron | (legacy excluded from viable); (compacted prisma emitter) |
| examples/golden/03_scraper.ainl | non-strict-only | 713 | 2.639 | — | — | 79 | — | — | 0 | 79 | 0.11x | prisma, cron | (legacy excluded from viable); (compacted prisma emitter) |
| examples/golden/04_alerting_monitor.ainl | non-strict-only | 714 | 2.848 | — | — | 79 | — | — | 0 | 79 | 0.11x | prisma, cron | (legacy excluded from viable); (compacted prisma emitter) |
| examples/golden/05_file_processor.ainl | non-strict-only | 838 | 2.648 | — | — | 82 | — | — | 0 | 82 | 0.10x | prisma, cron | (legacy excluded from viable); (compacted prisma emitter) |
| examples/integrations/executor_bridge_adapter_min.ainl | non-strict-only | 226 | 0.683 | — | 95 | — | — | — | — | 95 | 0.42x | python_api |  |
| examples/integrations/executor_bridge_min.ainl | non-strict-only | 241 | 0.787 | — | 95 | — | — | — | — | 95 | 0.39x | python_api |  |
| examples/internal_tool.lang | non-strict-only | 227 | 0.750 | 148 | 128 | 85 | — | — | 98 | 459 | 2.02x | react_ts, python_api, prisma, cron | (compacted prisma emitter) |
| examples/openclaw/agent_read_result.lang | non-strict-only | 109 | 0.227 | — | 95 | — | — | — | — | 95 | 0.87x | python_api | (legacy excluded from viable) |
| examples/openclaw/agent_send_task.lang | non-strict-only | 349 | 0.775 | — | 95 | — | — | — | — | 95 | 0.27x | python_api | (legacy excluded from viable) |
| examples/openclaw/backup_manager.lang | non-strict-only | 485 | 4.195 | — | — | 78 | — | — | 0 | 78 | 0.16x | prisma, cron | (legacy excluded from viable); (compacted prisma emitter) |
| examples/openclaw/daily_digest.lang | non-strict-only | 283 | 1.998 | — | — | 78 | — | — | 0 | 78 | 0.28x | prisma, cron | (compacted prisma emitter) |
| examples/openclaw/daily_digest.strict.lang | non-strict-only | 565 | 3.060 | — | — | 101 | — | — | 0 | 101 | 0.18x | prisma, cron | (legacy excluded from viable) |
| examples/openclaw/daily_lead_summary.lang | non-strict-only | 147 | 0.899 | — | — | 79 | — | — | 0 | 79 | 0.54x | prisma, cron | (compacted prisma emitter) |
| examples/openclaw/infrastructure_watchdog.lang | non-strict-only | 419 | 2.785 | — | — | 79 | — | — | 0 | 79 | 0.19x | prisma, cron | (legacy excluded from viable); (compacted prisma emitter) |
| examples/openclaw/lead_enrichment.lang | non-strict-only | 368 | 2.509 | — | 34 | — | — | — | 0 | 34 | 0.09x | cron, python_api | (fallback stub); (legacy excluded from viable) |
| examples/openclaw/memory_daily_log_note.lang | non-strict-only | 349 | 1.137 | — | 95 | — | — | — | — | 95 | 0.27x | python_api | (legacy excluded from viable) |
| examples/openclaw/memory_token_cost_state.lang | non-strict-only | 361 | 1.131 | — | 95 | — | — | — | — | 95 | 0.26x | python_api | (legacy excluded from viable) |
| examples/openclaw/monitor_status_advice_read.lang | non-strict-only | 121 | 0.380 | — | 95 | — | — | — | — | 95 | 0.79x | python_api | (legacy excluded from viable) |
| examples/openclaw/monitor_status_advice_request.lang | non-strict-only | 626 | 1.290 | — | 95 | — | — | — | — | 95 | 0.15x | python_api | (legacy excluded from viable) |
| examples/openclaw/token_cost_advice_read.lang | non-strict-only | 119 | 0.239 | — | 95 | — | — | — | — | 95 | 0.80x | python_api | (legacy excluded from viable) |
| examples/openclaw/token_cost_advice_request.lang | non-strict-only | 418 | 0.887 | — | 95 | — | — | — | — | 95 | 0.23x | python_api | (legacy excluded from viable) |
| examples/openclaw/webhook_handler.lang | non-strict-only | 306 | 1.573 | — | 107 | 62 | — | — | — | 169 | 0.55x | python_api, prisma | (compacted prisma emitter) |
| examples/ticketing.lang | non-strict-only | 274 | 1.098 | 183 | 152 | 84 | — | — | — | 419 | 1.53x | react_ts, python_api, prisma | (compacted prisma emitter) |

*Token counts via tiktoken **cl100k_base**. Minimal_emit **fallback** stubs are typically ~20–30 tk.*

## Including Legacy Artifacts

Legacy files (pure-cron shells, OpenClaw micro-wrappers, aggregate emit below the viable threshold, or paths marked `viable_for_aggregate: false`) are **still compiled and listed** in the per-artifact tables; they are **excluded only** from the **viable** summary rows above for `public_mixed` and `compatibility_only`. Canonical strict-valid profile totals are unchanged (all viable).

### full_multitarget — legacy-inclusive totals

| Profile | Artifact count | AINL source total (tk) | Aggregate total (tk) | Ratio (tk) |
|---|---:|---:|---:|---:|
| canonical_strict_valid | 10 | 506 | 4507 | 8.91x |
| public_mixed | 59 | 28065 | 28824 | 1.03x |
| compatibility_only | 49 | 27559 | 24317 | 0.88x |

*Legacy-inclusive totals above: all artifacts in profile, **tiktoken** sums.*

### minimal_emit — legacy-inclusive totals

| Profile | Artifact count | AINL source total (tk) | Aggregate total (tk) | Ratio (tk) |
|---|---:|---:|---:|---:|
| canonical_strict_valid | 10 | 506 | 1122 | 2.22x |
| public_mixed | 59 | 28065 | 6787 | 0.24x |
| compatibility_only | 49 | 27559 | 5665 | 0.21x |

*Legacy-inclusive totals above: all artifacts in profile, **tiktoken** sums.*

## Supported vs Unsupported Claims

- Supported: profile- and mode-scoped compactness comparisons for this benchmark setup.
- Supported: canonical strict-valid as primary headline profile.
- Unsupported: universal compactness claims versus Python/TypeScript/Rust/Go.
- Unsupported: treating **approx_chunks** or **nonempty_lines** JSON runs as exact OpenAI billing without cross-checking tiktoken.
- Note: source-text fallback remains as temporary legacy support for older IRs missing capability metadata.

## Recommended Next Benchmark Improvements

- Handwritten baselines live under `benchmarks/handwritten_baselines/`; use `--compare-baselines` on size/runtime scripts for tables vs mapped AINL artifacts.
- Add CI trend snapshots for both full and minimal modes.
- Optional: snapshot secondary `--metric` lanes (e.g. `nonempty_lines`) for structure-only regressions.

Conclusion: strongest current claim is compactness in canonical multi-target examples; language-surface changes are not required for these benchmark gains.

Selection source: `tooling/artifact_profiles.json`; planning source: `tooling/benchmark_manifest.json`.
