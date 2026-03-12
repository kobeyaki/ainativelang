# AI Native Lang Size Benchmark

This benchmark measures AINL source compactness against generated implementation artifacts.
It is segmented by profile and mode; it is not a universal compactness claim across programming languages.

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

- Active metric: `approx_chunks`.
- `approx_chunks` is a lexical-size proxy, not tokenizer-accurate pricing.

## How To Read These Results

- Ratio `> 1`: generated output is larger than AINL source.
- Ratio `~ 1`: near parity.
- Ratio `< 1`: generated output is smaller than AINL source.
- `approx_chunks` is a useful lexical proxy, not exact LLM token billing.

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
- They are not guaranteed tokenizer-cost or LLM pricing results in `approx_chunks` mode.
- They are not a proxy for runtime performance or product quality by themselves.

## Mode Comparison (Headline + Mixed)

| Profile | Full aggregate ratio | Minimal aggregate ratio |
|---|---:|---:|
| canonical_strict_valid | 10.98x | 1.97x |
| public_mixed | 1.74x | 0.46x |
| compatibility_only | 1.36x | 0.40x |

Compatibility/non-strict artifacts are segmented and not used as the primary benchmark headline.

## Size Drivers (Actionable Diagnosis)

### full_multitarget
- `canonical_strict_valid` top targets: mt5=750, prisma=480, python_api=383
- `canonical_strict_valid` top artifacts: examples/scraper/basic_scraper.ainl=283, examples/monitor_escalation.ainl=271, examples/web/basic_web_api.ainl=234
- `public_mixed` top targets: mt5=2992, prisma=2076, react_ts=1664
- `public_mixed` top artifacts: examples/internal_tool.lang=414, examples/ticketing.lang=401, examples/ecom.lang=391
- `compatibility_only` top targets: mt5=2242, prisma=1596, react_ts=1294
- `compatibility_only` top artifacts: examples/internal_tool.lang=414, examples/ticketing.lang=401, examples/ecom.lang=391

### minimal_emit
- `canonical_strict_valid` top targets: python_api=307, cron=80, scraper=45
- `canonical_strict_valid` top artifacts: examples/scraper/basic_scraper.ainl=85, examples/web/basic_web_api.ainl=41, examples/monitor_escalation.ainl=40
- `public_mixed` top targets: prisma=1116, python_api=592, react_ts=480
- `public_mixed` top artifacts: examples/internal_tool.lang=270, examples/ticketing.lang=257, examples/ecom.lang=251
- `compatibility_only` top targets: prisma=1116, react_ts=480, python_api=285
- `compatibility_only` top artifacts: examples/internal_tool.lang=270, examples/ticketing.lang=257, examples/ecom.lang=251

## Residual Overhead Audit (minimal_emit)

### canonical_strict_valid
- `python_api` total=307; structure: decorator_chunks=1, function_def_chunks=2, imports_chunks=32, return_chunks=2, total_chunks=307
- `cron` total=80; structure: function_def_chunks=4, pass_chunks=2, schedule_comment_chunks=74, total_chunks=80
- `scraper` total=45; structure: function_def_chunks=2, imports_chunks=8, request_call_chunks=1, return_chunks=1, selector_chunks=3, total_chunks=45

### public_mixed
- `prisma` total=1116; structure: total_chunks=1116
- `python_api` total=592; structure: decorator_chunks=20, function_def_chunks=40, imports_chunks=56, return_chunks=40, total_chunks=592
- `react_ts` total=480; structure: total_chunks=480

### compatibility_only
- `prisma` total=1116; structure: total_chunks=1116
- `react_ts` total=480; structure: total_chunks=480
- `python_api` total=285; structure: decorator_chunks=19, function_def_chunks=38, imports_chunks=24, return_chunks=38, total_chunks=285

## Details (full_multitarget)

| Profile | Artifact count | AINL source total | Aggregate generated output total | Aggregate ratio |
|---|---:|---:|---:|---:|
| canonical_strict_valid | 10 | 219 | 2405 | 10.98x |
| public_mixed | 36 | 5590 | 9720 | 1.74x |
| compatibility_only | 26 | 5371 | 7315 | 1.36x |

### canonical_strict_valid
| Artifact | Class | AINL source | React/TS | Python API | Prisma | MT5 | Scraper | Cron | Aggregate generated output | Aggregate ratio | Included targets |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| examples/crud_api.ainl | strict-valid | 20 | 37 | 38 | 48 | 75 | 33 | 0 | 231 | 11.55x | react_ts, python_api, prisma, mt5, scraper, cron |
| examples/hello.ainl | strict-valid | 8 | 37 | 38 | 48 | 75 | 33 | 0 | 231 | 28.88x | react_ts, python_api, prisma, mt5, scraper, cron |
| examples/if_call_workflow.ainl | strict-valid | 34 | 37 | 38 | 48 | 75 | 33 | 0 | 231 | 6.79x | react_ts, python_api, prisma, mt5, scraper, cron |
| examples/monitor_escalation.ainl | strict-valid | 32 | 37 | 38 | 48 | 75 | 33 | 40 | 271 | 8.47x | react_ts, python_api, prisma, mt5, scraper, cron |
| examples/rag_pipeline.ainl | strict-valid | 14 | 37 | 38 | 48 | 75 | 33 | 0 | 231 | 16.50x | react_ts, python_api, prisma, mt5, scraper, cron |
| examples/retry_error_resilience.ainl | strict-valid | 20 | 37 | 38 | 48 | 75 | 33 | 0 | 231 | 11.55x | react_ts, python_api, prisma, mt5, scraper, cron |
| examples/scraper/basic_scraper.ainl | strict-valid | 29 | 37 | 38 | 48 | 75 | 45 | 40 | 283 | 9.76x | react_ts, python_api, prisma, mt5, scraper, cron |
| examples/status_branching.ainl | strict-valid | 20 | 37 | 38 | 48 | 75 | 33 | 0 | 231 | 11.55x | react_ts, python_api, prisma, mt5, scraper, cron |
| examples/web/basic_web_api.ainl | strict-valid | 17 | 37 | 41 | 48 | 75 | 33 | 0 | 234 | 13.76x | react_ts, python_api, prisma, mt5, scraper, cron |
| examples/webhook_automation.ainl | strict-valid | 25 | 37 | 38 | 48 | 75 | 33 | 0 | 231 | 9.24x | react_ts, python_api, prisma, mt5, scraper, cron |

### public_mixed
| Artifact | Class | AINL source | React/TS | Python API | Prisma | MT5 | Scraper | Cron | Aggregate generated output | Aggregate ratio | Included targets |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| examples/api_only.lang | non-strict-only | 62 | 37 | 47 | 70 | 103 | 33 | 0 | 290 | 4.68x | react_ts, python_api, prisma, mt5, scraper, cron |
| examples/autonomous_ops/backup_freshness_to_queue.lang | non-strict-only | 94 | 37 | 38 | 48 | 75 | 33 | 0 | 231 | 2.46x | react_ts, python_api, prisma, mt5, scraper, cron |
| examples/autonomous_ops/canary_sampler.lang | non-strict-only | 408 | 37 | 38 | 48 | 75 | 33 | 40 | 271 | 0.66x | react_ts, python_api, prisma, mt5, scraper, cron |
| examples/autonomous_ops/infrastructure_watchdog.lang | non-strict-only | 340 | 37 | 38 | 48 | 75 | 33 | 40 | 271 | 0.80x | react_ts, python_api, prisma, mt5, scraper, cron |
| examples/autonomous_ops/lead_quality_audit.lang | non-strict-only | 172 | 37 | 38 | 48 | 75 | 33 | 40 | 271 | 1.58x | react_ts, python_api, prisma, mt5, scraper, cron |
| examples/autonomous_ops/pipeline_readiness_snapshot.lang | non-strict-only | 102 | 37 | 38 | 48 | 75 | 33 | 0 | 231 | 2.26x | react_ts, python_api, prisma, mt5, scraper, cron |
| examples/autonomous_ops/status_snapshot_to_queue.lang | non-strict-only | 102 | 37 | 38 | 48 | 75 | 33 | 0 | 231 | 2.26x | react_ts, python_api, prisma, mt5, scraper, cron |
| examples/autonomous_ops/tiktok_sla_monitor.lang | non-strict-only | 184 | 37 | 38 | 48 | 75 | 33 | 40 | 271 | 1.47x | react_ts, python_api, prisma, mt5, scraper, cron |
| examples/autonomous_ops/token_cost_tracker.lang | non-strict-only | 235 | 37 | 38 | 48 | 75 | 33 | 40 | 271 | 1.15x | react_ts, python_api, prisma, mt5, scraper, cron |
| examples/blog.lang | non-strict-only | 135 | 109 | 50 | 76 | 115 | 33 | 0 | 383 | 2.84x | react_ts, python_api, prisma, mt5, scraper, cron |
| examples/cron/monitor_and_alert.ainl | non-strict-only | 35 | 37 | 38 | 48 | 75 | 33 | 40 | 271 | 7.74x | react_ts, python_api, prisma, mt5, scraper, cron |
| examples/crud_api.ainl | strict-valid | 20 | 37 | 38 | 48 | 75 | 33 | 0 | 231 | 11.55x | react_ts, python_api, prisma, mt5, scraper, cron |
| examples/ecom.lang | non-strict-only | 137 | 132 | 47 | 72 | 107 | 33 | 0 | 391 | 2.85x | react_ts, python_api, prisma, mt5, scraper, cron |
| examples/golden/01_web_server.ainl | non-strict-only | 304 | 37 | 38 | 69 | 87 | 33 | 0 | 264 | 0.87x | react_ts, python_api, prisma, mt5, scraper, cron |
| examples/golden/02_dashboard.ainl | non-strict-only | 335 | 37 | 38 | 68 | 83 | 33 | 0 | 259 | 0.77x | react_ts, python_api, prisma, mt5, scraper, cron |
| examples/golden/03_scraper.ainl | non-strict-only | 381 | 37 | 38 | 68 | 83 | 33 | 0 | 259 | 0.68x | react_ts, python_api, prisma, mt5, scraper, cron |
| examples/golden/04_alerting_monitor.ainl | non-strict-only | 373 | 37 | 38 | 68 | 83 | 33 | 0 | 259 | 0.69x | react_ts, python_api, prisma, mt5, scraper, cron |
| examples/golden/05_file_processor.ainl | non-strict-only | 481 | 37 | 38 | 69 | 87 | 33 | 0 | 264 | 0.55x | react_ts, python_api, prisma, mt5, scraper, cron |
| examples/hello.ainl | strict-valid | 8 | 37 | 38 | 48 | 75 | 33 | 0 | 231 | 28.88x | react_ts, python_api, prisma, mt5, scraper, cron |
| examples/if_call_workflow.ainl | strict-valid | 34 | 37 | 38 | 48 | 75 | 33 | 0 | 231 | 6.79x | react_ts, python_api, prisma, mt5, scraper, cron |
| examples/internal_tool.lang | non-strict-only | 127 | 109 | 47 | 74 | 111 | 33 | 40 | 414 | 3.26x | react_ts, python_api, prisma, mt5, scraper, cron |
| examples/monitor_escalation.ainl | strict-valid | 32 | 37 | 38 | 48 | 75 | 33 | 40 | 271 | 8.47x | react_ts, python_api, prisma, mt5, scraper, cron |
| examples/openclaw/backup_manager.lang | non-strict-only | 222 | 37 | 38 | 68 | 83 | 33 | 0 | 259 | 1.17x | react_ts, python_api, prisma, mt5, scraper, cron |
| examples/openclaw/daily_digest.lang | non-strict-only | 134 | 37 | 38 | 68 | 83 | 33 | 0 | 259 | 1.93x | react_ts, python_api, prisma, mt5, scraper, cron |
| examples/openclaw/daily_digest.strict.lang | non-strict-only | 254 | 37 | 38 | 76 | 99 | 33 | 0 | 283 | 1.11x | react_ts, python_api, prisma, mt5, scraper, cron |
| examples/openclaw/daily_lead_summary.lang | non-strict-only | 84 | 37 | 38 | 68 | 83 | 33 | 0 | 259 | 3.08x | react_ts, python_api, prisma, mt5, scraper, cron |
| examples/openclaw/infrastructure_watchdog.lang | non-strict-only | 189 | 37 | 38 | 68 | 83 | 33 | 0 | 259 | 1.37x | react_ts, python_api, prisma, mt5, scraper, cron |
| examples/openclaw/lead_enrichment.lang | non-strict-only | 178 | 37 | 38 | 48 | 75 | 33 | 0 | 231 | 1.30x | react_ts, python_api, prisma, mt5, scraper, cron |
| examples/openclaw/webhook_handler.lang | non-strict-only | 150 | 37 | 41 | 60 | 91 | 33 | 0 | 262 | 1.75x | react_ts, python_api, prisma, mt5, scraper, cron |
| examples/rag_pipeline.ainl | strict-valid | 14 | 37 | 38 | 48 | 75 | 33 | 0 | 231 | 16.50x | react_ts, python_api, prisma, mt5, scraper, cron |
| examples/retry_error_resilience.ainl | strict-valid | 20 | 37 | 38 | 48 | 75 | 33 | 0 | 231 | 11.55x | react_ts, python_api, prisma, mt5, scraper, cron |
| examples/scraper/basic_scraper.ainl | strict-valid | 29 | 37 | 38 | 48 | 75 | 45 | 40 | 283 | 9.76x | react_ts, python_api, prisma, mt5, scraper, cron |
| examples/status_branching.ainl | strict-valid | 20 | 37 | 38 | 48 | 75 | 33 | 0 | 231 | 11.55x | react_ts, python_api, prisma, mt5, scraper, cron |
| examples/ticketing.lang | non-strict-only | 153 | 130 | 53 | 74 | 111 | 33 | 0 | 401 | 2.62x | react_ts, python_api, prisma, mt5, scraper, cron |
| examples/web/basic_web_api.ainl | strict-valid | 17 | 37 | 41 | 48 | 75 | 33 | 0 | 234 | 13.76x | react_ts, python_api, prisma, mt5, scraper, cron |
| examples/webhook_automation.ainl | strict-valid | 25 | 37 | 38 | 48 | 75 | 33 | 0 | 231 | 9.24x | react_ts, python_api, prisma, mt5, scraper, cron |

### compatibility_only
| Artifact | Class | AINL source | React/TS | Python API | Prisma | MT5 | Scraper | Cron | Aggregate generated output | Aggregate ratio | Included targets |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| examples/api_only.lang | non-strict-only | 62 | 37 | 47 | 70 | 103 | 33 | 0 | 290 | 4.68x | react_ts, python_api, prisma, mt5, scraper, cron |
| examples/autonomous_ops/backup_freshness_to_queue.lang | non-strict-only | 94 | 37 | 38 | 48 | 75 | 33 | 0 | 231 | 2.46x | react_ts, python_api, prisma, mt5, scraper, cron |
| examples/autonomous_ops/canary_sampler.lang | non-strict-only | 408 | 37 | 38 | 48 | 75 | 33 | 40 | 271 | 0.66x | react_ts, python_api, prisma, mt5, scraper, cron |
| examples/autonomous_ops/infrastructure_watchdog.lang | non-strict-only | 340 | 37 | 38 | 48 | 75 | 33 | 40 | 271 | 0.80x | react_ts, python_api, prisma, mt5, scraper, cron |
| examples/autonomous_ops/lead_quality_audit.lang | non-strict-only | 172 | 37 | 38 | 48 | 75 | 33 | 40 | 271 | 1.58x | react_ts, python_api, prisma, mt5, scraper, cron |
| examples/autonomous_ops/pipeline_readiness_snapshot.lang | non-strict-only | 102 | 37 | 38 | 48 | 75 | 33 | 0 | 231 | 2.26x | react_ts, python_api, prisma, mt5, scraper, cron |
| examples/autonomous_ops/status_snapshot_to_queue.lang | non-strict-only | 102 | 37 | 38 | 48 | 75 | 33 | 0 | 231 | 2.26x | react_ts, python_api, prisma, mt5, scraper, cron |
| examples/autonomous_ops/tiktok_sla_monitor.lang | non-strict-only | 184 | 37 | 38 | 48 | 75 | 33 | 40 | 271 | 1.47x | react_ts, python_api, prisma, mt5, scraper, cron |
| examples/autonomous_ops/token_cost_tracker.lang | non-strict-only | 235 | 37 | 38 | 48 | 75 | 33 | 40 | 271 | 1.15x | react_ts, python_api, prisma, mt5, scraper, cron |
| examples/blog.lang | non-strict-only | 135 | 109 | 50 | 76 | 115 | 33 | 0 | 383 | 2.84x | react_ts, python_api, prisma, mt5, scraper, cron |
| examples/cron/monitor_and_alert.ainl | non-strict-only | 35 | 37 | 38 | 48 | 75 | 33 | 40 | 271 | 7.74x | react_ts, python_api, prisma, mt5, scraper, cron |
| examples/ecom.lang | non-strict-only | 137 | 132 | 47 | 72 | 107 | 33 | 0 | 391 | 2.85x | react_ts, python_api, prisma, mt5, scraper, cron |
| examples/golden/01_web_server.ainl | non-strict-only | 304 | 37 | 38 | 69 | 87 | 33 | 0 | 264 | 0.87x | react_ts, python_api, prisma, mt5, scraper, cron |
| examples/golden/02_dashboard.ainl | non-strict-only | 335 | 37 | 38 | 68 | 83 | 33 | 0 | 259 | 0.77x | react_ts, python_api, prisma, mt5, scraper, cron |
| examples/golden/03_scraper.ainl | non-strict-only | 381 | 37 | 38 | 68 | 83 | 33 | 0 | 259 | 0.68x | react_ts, python_api, prisma, mt5, scraper, cron |
| examples/golden/04_alerting_monitor.ainl | non-strict-only | 373 | 37 | 38 | 68 | 83 | 33 | 0 | 259 | 0.69x | react_ts, python_api, prisma, mt5, scraper, cron |
| examples/golden/05_file_processor.ainl | non-strict-only | 481 | 37 | 38 | 69 | 87 | 33 | 0 | 264 | 0.55x | react_ts, python_api, prisma, mt5, scraper, cron |
| examples/internal_tool.lang | non-strict-only | 127 | 109 | 47 | 74 | 111 | 33 | 40 | 414 | 3.26x | react_ts, python_api, prisma, mt5, scraper, cron |
| examples/openclaw/backup_manager.lang | non-strict-only | 222 | 37 | 38 | 68 | 83 | 33 | 0 | 259 | 1.17x | react_ts, python_api, prisma, mt5, scraper, cron |
| examples/openclaw/daily_digest.lang | non-strict-only | 134 | 37 | 38 | 68 | 83 | 33 | 0 | 259 | 1.93x | react_ts, python_api, prisma, mt5, scraper, cron |
| examples/openclaw/daily_digest.strict.lang | non-strict-only | 254 | 37 | 38 | 76 | 99 | 33 | 0 | 283 | 1.11x | react_ts, python_api, prisma, mt5, scraper, cron |
| examples/openclaw/daily_lead_summary.lang | non-strict-only | 84 | 37 | 38 | 68 | 83 | 33 | 0 | 259 | 3.08x | react_ts, python_api, prisma, mt5, scraper, cron |
| examples/openclaw/infrastructure_watchdog.lang | non-strict-only | 189 | 37 | 38 | 68 | 83 | 33 | 0 | 259 | 1.37x | react_ts, python_api, prisma, mt5, scraper, cron |
| examples/openclaw/lead_enrichment.lang | non-strict-only | 178 | 37 | 38 | 48 | 75 | 33 | 0 | 231 | 1.30x | react_ts, python_api, prisma, mt5, scraper, cron |
| examples/openclaw/webhook_handler.lang | non-strict-only | 150 | 37 | 41 | 60 | 91 | 33 | 0 | 262 | 1.75x | react_ts, python_api, prisma, mt5, scraper, cron |
| examples/ticketing.lang | non-strict-only | 153 | 130 | 53 | 74 | 111 | 33 | 0 | 401 | 2.62x | react_ts, python_api, prisma, mt5, scraper, cron |

## Details (minimal_emit)

| Profile | Artifact count | AINL source total | Aggregate generated output total | Aggregate ratio |
|---|---:|---:|---:|---:|
| canonical_strict_valid | 10 | 219 | 432 | 1.97x |
| public_mixed | 36 | 5590 | 2593 | 0.46x |
| compatibility_only | 26 | 5371 | 2161 | 0.40x |

### canonical_strict_valid
| Artifact | Class | AINL source | React/TS | Python API | Prisma | MT5 | Scraper | Cron | Aggregate generated output | Aggregate ratio | Included targets |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| examples/crud_api.ainl | strict-valid | 20 | - | 38 | - | - | - | - | 38 | 1.90x | python_api |
| examples/hello.ainl | strict-valid | 8 | - | 38 | - | - | - | - | 38 | 4.75x | python_api |
| examples/if_call_workflow.ainl | strict-valid | 34 | - | 38 | - | - | - | - | 38 | 1.12x | python_api |
| examples/monitor_escalation.ainl | strict-valid | 32 | - | - | - | - | - | 40 | 40 | 1.25x | cron |
| examples/rag_pipeline.ainl | strict-valid | 14 | - | 38 | - | - | - | - | 38 | 2.71x | python_api |
| examples/retry_error_resilience.ainl | strict-valid | 20 | - | 38 | - | - | - | - | 38 | 1.90x | python_api |
| examples/scraper/basic_scraper.ainl | strict-valid | 29 | - | - | - | - | 45 | 40 | 85 | 2.93x | scraper, cron |
| examples/status_branching.ainl | strict-valid | 20 | - | 38 | - | - | - | - | 38 | 1.90x | python_api |
| examples/web/basic_web_api.ainl | strict-valid | 17 | - | 41 | - | - | - | - | 41 | 2.41x | python_api |
| examples/webhook_automation.ainl | strict-valid | 25 | - | 38 | - | - | - | - | 38 | 1.52x | python_api |

### public_mixed
| Artifact | Class | AINL source | React/TS | Python API | Prisma | MT5 | Scraper | Cron | Aggregate generated output | Aggregate ratio | Included targets |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| examples/api_only.lang | non-strict-only | 62 | - | 47 | 70 | - | - | - | 117 | 1.89x | python_api, prisma |
| examples/autonomous_ops/backup_freshness_to_queue.lang | non-strict-only | 94 | - | - | - | - | - | 0 | 0 | 0.00x | cron |
| examples/autonomous_ops/canary_sampler.lang | non-strict-only | 408 | - | - | - | - | - | 40 | 40 | 0.10x | cron |
| examples/autonomous_ops/infrastructure_watchdog.lang | non-strict-only | 340 | - | - | - | - | - | 40 | 40 | 0.12x | cron |
| examples/autonomous_ops/lead_quality_audit.lang | non-strict-only | 172 | - | - | - | - | - | 40 | 40 | 0.23x | cron |
| examples/autonomous_ops/pipeline_readiness_snapshot.lang | non-strict-only | 102 | - | - | - | - | - | 0 | 0 | 0.00x | cron |
| examples/autonomous_ops/status_snapshot_to_queue.lang | non-strict-only | 102 | - | - | - | - | - | 0 | 0 | 0.00x | cron |
| examples/autonomous_ops/tiktok_sla_monitor.lang | non-strict-only | 184 | - | - | - | - | - | 40 | 40 | 0.22x | cron |
| examples/autonomous_ops/token_cost_tracker.lang | non-strict-only | 235 | - | - | - | - | - | 40 | 40 | 0.17x | cron |
| examples/blog.lang | non-strict-only | 135 | 109 | 50 | 76 | - | - | - | 235 | 1.74x | react_ts, python_api, prisma |
| examples/cron/monitor_and_alert.ainl | non-strict-only | 35 | - | - | - | - | - | 40 | 40 | 1.14x | cron |
| examples/crud_api.ainl | strict-valid | 20 | - | 38 | - | - | - | - | 38 | 1.90x | python_api |
| examples/ecom.lang | non-strict-only | 137 | 132 | 47 | 72 | - | - | - | 251 | 1.83x | react_ts, python_api, prisma |
| examples/golden/01_web_server.ainl | non-strict-only | 304 | - | - | 69 | - | - | 0 | 69 | 0.23x | prisma, cron |
| examples/golden/02_dashboard.ainl | non-strict-only | 335 | - | - | 68 | - | - | 0 | 68 | 0.20x | prisma, cron |
| examples/golden/03_scraper.ainl | non-strict-only | 381 | - | - | 68 | - | - | 0 | 68 | 0.18x | prisma, cron |
| examples/golden/04_alerting_monitor.ainl | non-strict-only | 373 | - | - | 68 | - | - | 0 | 68 | 0.18x | prisma, cron |
| examples/golden/05_file_processor.ainl | non-strict-only | 481 | - | - | 69 | - | - | 0 | 69 | 0.14x | prisma, cron |
| examples/hello.ainl | strict-valid | 8 | - | 38 | - | - | - | - | 38 | 4.75x | python_api |
| examples/if_call_workflow.ainl | strict-valid | 34 | - | 38 | - | - | - | - | 38 | 1.12x | python_api |
| examples/internal_tool.lang | non-strict-only | 127 | 109 | 47 | 74 | - | - | 40 | 270 | 2.13x | react_ts, python_api, prisma, cron |
| examples/monitor_escalation.ainl | strict-valid | 32 | - | - | - | - | - | 40 | 40 | 1.25x | cron |
| examples/openclaw/backup_manager.lang | non-strict-only | 222 | - | - | 68 | - | - | 0 | 68 | 0.31x | prisma, cron |
| examples/openclaw/daily_digest.lang | non-strict-only | 134 | - | - | 68 | - | - | 0 | 68 | 0.51x | prisma, cron |
| examples/openclaw/daily_digest.strict.lang | non-strict-only | 254 | - | - | 76 | - | - | 0 | 76 | 0.30x | prisma, cron |
| examples/openclaw/daily_lead_summary.lang | non-strict-only | 84 | - | - | 68 | - | - | 0 | 68 | 0.81x | prisma, cron |
| examples/openclaw/infrastructure_watchdog.lang | non-strict-only | 189 | - | - | 68 | - | - | 0 | 68 | 0.36x | prisma, cron |
| examples/openclaw/lead_enrichment.lang | non-strict-only | 178 | - | - | - | - | - | 0 | 0 | 0.00x | cron |
| examples/openclaw/webhook_handler.lang | non-strict-only | 150 | - | 41 | 60 | - | - | - | 101 | 0.67x | python_api, prisma |
| examples/rag_pipeline.ainl | strict-valid | 14 | - | 38 | - | - | - | - | 38 | 2.71x | python_api |
| examples/retry_error_resilience.ainl | strict-valid | 20 | - | 38 | - | - | - | - | 38 | 1.90x | python_api |
| examples/scraper/basic_scraper.ainl | strict-valid | 29 | - | - | - | - | 45 | 40 | 85 | 2.93x | scraper, cron |
| examples/status_branching.ainl | strict-valid | 20 | - | 38 | - | - | - | - | 38 | 1.90x | python_api |
| examples/ticketing.lang | non-strict-only | 153 | 130 | 53 | 74 | - | - | - | 257 | 1.68x | react_ts, python_api, prisma |
| examples/web/basic_web_api.ainl | strict-valid | 17 | - | 41 | - | - | - | - | 41 | 2.41x | python_api |
| examples/webhook_automation.ainl | strict-valid | 25 | - | 38 | - | - | - | - | 38 | 1.52x | python_api |

### compatibility_only
| Artifact | Class | AINL source | React/TS | Python API | Prisma | MT5 | Scraper | Cron | Aggregate generated output | Aggregate ratio | Included targets |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| examples/api_only.lang | non-strict-only | 62 | - | 47 | 70 | - | - | - | 117 | 1.89x | python_api, prisma |
| examples/autonomous_ops/backup_freshness_to_queue.lang | non-strict-only | 94 | - | - | - | - | - | 0 | 0 | 0.00x | cron |
| examples/autonomous_ops/canary_sampler.lang | non-strict-only | 408 | - | - | - | - | - | 40 | 40 | 0.10x | cron |
| examples/autonomous_ops/infrastructure_watchdog.lang | non-strict-only | 340 | - | - | - | - | - | 40 | 40 | 0.12x | cron |
| examples/autonomous_ops/lead_quality_audit.lang | non-strict-only | 172 | - | - | - | - | - | 40 | 40 | 0.23x | cron |
| examples/autonomous_ops/pipeline_readiness_snapshot.lang | non-strict-only | 102 | - | - | - | - | - | 0 | 0 | 0.00x | cron |
| examples/autonomous_ops/status_snapshot_to_queue.lang | non-strict-only | 102 | - | - | - | - | - | 0 | 0 | 0.00x | cron |
| examples/autonomous_ops/tiktok_sla_monitor.lang | non-strict-only | 184 | - | - | - | - | - | 40 | 40 | 0.22x | cron |
| examples/autonomous_ops/token_cost_tracker.lang | non-strict-only | 235 | - | - | - | - | - | 40 | 40 | 0.17x | cron |
| examples/blog.lang | non-strict-only | 135 | 109 | 50 | 76 | - | - | - | 235 | 1.74x | react_ts, python_api, prisma |
| examples/cron/monitor_and_alert.ainl | non-strict-only | 35 | - | - | - | - | - | 40 | 40 | 1.14x | cron |
| examples/ecom.lang | non-strict-only | 137 | 132 | 47 | 72 | - | - | - | 251 | 1.83x | react_ts, python_api, prisma |
| examples/golden/01_web_server.ainl | non-strict-only | 304 | - | - | 69 | - | - | 0 | 69 | 0.23x | prisma, cron |
| examples/golden/02_dashboard.ainl | non-strict-only | 335 | - | - | 68 | - | - | 0 | 68 | 0.20x | prisma, cron |
| examples/golden/03_scraper.ainl | non-strict-only | 381 | - | - | 68 | - | - | 0 | 68 | 0.18x | prisma, cron |
| examples/golden/04_alerting_monitor.ainl | non-strict-only | 373 | - | - | 68 | - | - | 0 | 68 | 0.18x | prisma, cron |
| examples/golden/05_file_processor.ainl | non-strict-only | 481 | - | - | 69 | - | - | 0 | 69 | 0.14x | prisma, cron |
| examples/internal_tool.lang | non-strict-only | 127 | 109 | 47 | 74 | - | - | 40 | 270 | 2.13x | react_ts, python_api, prisma, cron |
| examples/openclaw/backup_manager.lang | non-strict-only | 222 | - | - | 68 | - | - | 0 | 68 | 0.31x | prisma, cron |
| examples/openclaw/daily_digest.lang | non-strict-only | 134 | - | - | 68 | - | - | 0 | 68 | 0.51x | prisma, cron |
| examples/openclaw/daily_digest.strict.lang | non-strict-only | 254 | - | - | 76 | - | - | 0 | 76 | 0.30x | prisma, cron |
| examples/openclaw/daily_lead_summary.lang | non-strict-only | 84 | - | - | 68 | - | - | 0 | 68 | 0.81x | prisma, cron |
| examples/openclaw/infrastructure_watchdog.lang | non-strict-only | 189 | - | - | 68 | - | - | 0 | 68 | 0.36x | prisma, cron |
| examples/openclaw/lead_enrichment.lang | non-strict-only | 178 | - | - | - | - | - | 0 | 0 | 0.00x | cron |
| examples/openclaw/webhook_handler.lang | non-strict-only | 150 | - | 41 | 60 | - | - | - | 101 | 0.67x | python_api, prisma |
| examples/ticketing.lang | non-strict-only | 153 | 130 | 53 | 74 | - | - | - | 257 | 1.68x | react_ts, python_api, prisma |

## Supported vs Unsupported Claims

- Supported: profile- and mode-scoped compactness comparisons for this benchmark setup.
- Supported: canonical strict-valid as primary headline profile.
- Unsupported: universal compactness claims versus Python/TypeScript/Rust/Go.
- Unsupported: guaranteed pricing impact from default lexical metrics.
- Note: source-text fallback remains as temporary legacy support for older IRs missing capability metadata.

## Recommended Next Benchmark Improvements

- Add optional handwritten baseline files under `benchmarks/handwritten_baselines/`.
- Add CI trend snapshots for both full and minimal modes.
- Add tokenizer-metric lane when dependency pinning is available.

Conclusion: strongest current claim is compactness in canonical multi-target examples; language-surface changes are not required for these benchmark gains.

Selection source: `tooling/artifact_profiles.json`; planning source: `tooling/benchmark_manifest.json`.
