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
| canonical_strict_valid | 5.28x | 0.62x |
| public_mixed | 0.81x | 0.31x |
| compatibility_only | 0.70x | 0.30x |

Compatibility/non-strict artifacts are segmented and not used as the primary benchmark headline.

## Size Drivers (Actionable Diagnosis)

### full_multitarget
- `canonical_strict_valid` top targets: mt5=255, prisma=85, react_ts=55
- `canonical_strict_valid` top artifacts: examples/scraper/basic_scraper.ainl=110, examples/web/basic_web_api.ainl=91, examples/crud_api.ainl=88
- `public_mixed` top targets: mt5=1347, prisma=665, react_ts=563
- `public_mixed` top artifacts: examples/ticketing.lang=258, examples/ecom.lang=248, examples/blog.lang=240
- `compatibility_only` top targets: mt5=1092, prisma=580, react_ts=508
- `compatibility_only` top artifacts: examples/ticketing.lang=258, examples/ecom.lang=248, examples/blog.lang=240

### minimal_emit
- `canonical_strict_valid` top targets: python_api=31, scraper=15, cron=9
- `canonical_strict_valid` top artifacts: examples/scraper/basic_scraper.ainl=24, examples/web/basic_web_api.ainl=10, examples/crud_api.ainl=7
- `public_mixed` top targets: prisma=546, react_ts=376, python_api=130
- `public_mixed` top artifacts: examples/ticketing.lang=169, examples/ecom.lang=163, examples/internal_tool.lang=151
- `compatibility_only` top targets: prisma=546, react_ts=376, python_api=99
- `compatibility_only` top artifacts: examples/ticketing.lang=169, examples/ecom.lang=163, examples/internal_tool.lang=151

## Residual Overhead Audit (minimal_emit)

### canonical_strict_valid
- `python_api` total=31; structure: decorator_chunks=1, function_def_chunks=2, imports_chunks=16, return_chunks=2, total_chunks=31
- `scraper` total=15; structure: function_def_chunks=2, imports_chunks=8, request_call_chunks=1, return_chunks=1, selector_chunks=3, total_chunks=15
- `cron` total=9; structure: function_def_chunks=2, pass_chunks=1, schedule_comment_chunks=6, total_chunks=9

### public_mixed
- `prisma` total=546; structure: total_chunks=546
- `react_ts` total=376; structure: total_chunks=376
- `python_api` total=130; structure: decorator_chunks=20, function_def_chunks=40, imports_chunks=40, return_chunks=40, total_chunks=130

### compatibility_only
- `prisma` total=546; structure: total_chunks=546
- `react_ts` total=376; structure: total_chunks=376
- `python_api` total=99; structure: decorator_chunks=19, function_def_chunks=38, imports_chunks=24, return_chunks=38, total_chunks=99

## Details (full_multitarget)

| Profile | Artifact count | AINL source total | Aggregate generated output total | Aggregate ratio |
|---|---:|---:|---:|---:|
| canonical_strict_valid | 5 | 88 | 465 | 5.28x |
| public_mixed | 21 | 3516 | 2864 | 0.81x |
| compatibility_only | 16 | 3428 | 2399 | 0.70x |

### canonical_strict_valid
| Artifact | Class | AINL source | React/TS | Python API | Prisma | MT5 | Scraper | Cron | Aggregate generated output | Aggregate ratio | Included targets |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| examples/crud_api.ainl | strict-valid | 20 | 11 | 7 | 17 | 51 | 2 | 0 | 88 | 4.40x | react_ts, python_api, prisma, mt5, scraper, cron |
| examples/hello.ainl | strict-valid | 8 | 11 | 7 | 17 | 51 | 2 | 0 | 88 | 11.00x | react_ts, python_api, prisma, mt5, scraper, cron |
| examples/rag_pipeline.ainl | strict-valid | 14 | 11 | 7 | 17 | 51 | 2 | 0 | 88 | 6.29x | react_ts, python_api, prisma, mt5, scraper, cron |
| examples/scraper/basic_scraper.ainl | strict-valid | 29 | 11 | 7 | 17 | 51 | 15 | 9 | 110 | 3.79x | react_ts, python_api, prisma, mt5, scraper, cron |
| examples/web/basic_web_api.ainl | strict-valid | 17 | 11 | 10 | 17 | 51 | 2 | 0 | 91 | 5.35x | react_ts, python_api, prisma, mt5, scraper, cron |

### public_mixed
| Artifact | Class | AINL source | React/TS | Python API | Prisma | MT5 | Scraper | Cron | Aggregate generated output | Aggregate ratio | Included targets |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| examples/api_only.lang | non-strict-only | 62 | 11 | 16 | 39 | 79 | 2 | 0 | 147 | 2.37x | react_ts, python_api, prisma, mt5, scraper, cron |
| examples/blog.lang | non-strict-only | 135 | 83 | 19 | 45 | 91 | 2 | 0 | 240 | 1.78x | react_ts, python_api, prisma, mt5, scraper, cron |
| examples/cron/monitor_and_alert.ainl | non-strict-only | 35 | 11 | 7 | 17 | 51 | 2 | 9 | 97 | 2.77x | react_ts, python_api, prisma, mt5, scraper, cron |
| examples/crud_api.ainl | strict-valid | 20 | 11 | 7 | 17 | 51 | 2 | 0 | 88 | 4.40x | react_ts, python_api, prisma, mt5, scraper, cron |
| examples/ecom.lang | non-strict-only | 137 | 106 | 16 | 41 | 83 | 2 | 0 | 248 | 1.81x | react_ts, python_api, prisma, mt5, scraper, cron |
| examples/golden/01_web_server.ainl | non-strict-only | 304 | 11 | 7 | 38 | 63 | 2 | 0 | 121 | 0.40x | react_ts, python_api, prisma, mt5, scraper, cron |
| examples/golden/02_dashboard.ainl | non-strict-only | 335 | 11 | 7 | 37 | 59 | 2 | 0 | 116 | 0.35x | react_ts, python_api, prisma, mt5, scraper, cron |
| examples/golden/03_scraper.ainl | non-strict-only | 381 | 11 | 7 | 37 | 59 | 2 | 0 | 116 | 0.30x | react_ts, python_api, prisma, mt5, scraper, cron |
| examples/golden/04_alerting_monitor.ainl | non-strict-only | 373 | 11 | 7 | 37 | 59 | 2 | 0 | 116 | 0.31x | react_ts, python_api, prisma, mt5, scraper, cron |
| examples/golden/05_file_processor.ainl | non-strict-only | 481 | 11 | 7 | 38 | 63 | 2 | 0 | 121 | 0.25x | react_ts, python_api, prisma, mt5, scraper, cron |
| examples/hello.ainl | strict-valid | 8 | 11 | 7 | 17 | 51 | 2 | 0 | 88 | 11.00x | react_ts, python_api, prisma, mt5, scraper, cron |
| examples/internal_tool.lang | non-strict-only | 127 | 83 | 16 | 43 | 87 | 2 | 9 | 240 | 1.89x | react_ts, python_api, prisma, mt5, scraper, cron |
| examples/openclaw/daily_digest.lang | non-strict-only | 134 | 11 | 7 | 37 | 59 | 2 | 0 | 116 | 0.87x | react_ts, python_api, prisma, mt5, scraper, cron |
| examples/openclaw/daily_digest.strict.lang | non-strict-only | 254 | 11 | 7 | 45 | 75 | 2 | 0 | 140 | 0.55x | react_ts, python_api, prisma, mt5, scraper, cron |
| examples/openclaw/infrastructure_watchdog.lang | non-strict-only | 189 | 11 | 7 | 37 | 59 | 2 | 0 | 116 | 0.61x | react_ts, python_api, prisma, mt5, scraper, cron |
| examples/openclaw/lead_enrichment.lang | non-strict-only | 178 | 11 | 7 | 17 | 51 | 2 | 0 | 88 | 0.49x | react_ts, python_api, prisma, mt5, scraper, cron |
| examples/openclaw/webhook_handler.lang | non-strict-only | 150 | 11 | 10 | 29 | 67 | 2 | 0 | 119 | 0.79x | react_ts, python_api, prisma, mt5, scraper, cron |
| examples/rag_pipeline.ainl | strict-valid | 14 | 11 | 7 | 17 | 51 | 2 | 0 | 88 | 6.29x | react_ts, python_api, prisma, mt5, scraper, cron |
| examples/scraper/basic_scraper.ainl | strict-valid | 29 | 11 | 7 | 17 | 51 | 15 | 9 | 110 | 3.79x | react_ts, python_api, prisma, mt5, scraper, cron |
| examples/ticketing.lang | non-strict-only | 153 | 104 | 22 | 43 | 87 | 2 | 0 | 258 | 1.69x | react_ts, python_api, prisma, mt5, scraper, cron |
| examples/web/basic_web_api.ainl | strict-valid | 17 | 11 | 10 | 17 | 51 | 2 | 0 | 91 | 5.35x | react_ts, python_api, prisma, mt5, scraper, cron |

### compatibility_only
| Artifact | Class | AINL source | React/TS | Python API | Prisma | MT5 | Scraper | Cron | Aggregate generated output | Aggregate ratio | Included targets |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| examples/api_only.lang | non-strict-only | 62 | 11 | 16 | 39 | 79 | 2 | 0 | 147 | 2.37x | react_ts, python_api, prisma, mt5, scraper, cron |
| examples/blog.lang | non-strict-only | 135 | 83 | 19 | 45 | 91 | 2 | 0 | 240 | 1.78x | react_ts, python_api, prisma, mt5, scraper, cron |
| examples/cron/monitor_and_alert.ainl | non-strict-only | 35 | 11 | 7 | 17 | 51 | 2 | 9 | 97 | 2.77x | react_ts, python_api, prisma, mt5, scraper, cron |
| examples/ecom.lang | non-strict-only | 137 | 106 | 16 | 41 | 83 | 2 | 0 | 248 | 1.81x | react_ts, python_api, prisma, mt5, scraper, cron |
| examples/golden/01_web_server.ainl | non-strict-only | 304 | 11 | 7 | 38 | 63 | 2 | 0 | 121 | 0.40x | react_ts, python_api, prisma, mt5, scraper, cron |
| examples/golden/02_dashboard.ainl | non-strict-only | 335 | 11 | 7 | 37 | 59 | 2 | 0 | 116 | 0.35x | react_ts, python_api, prisma, mt5, scraper, cron |
| examples/golden/03_scraper.ainl | non-strict-only | 381 | 11 | 7 | 37 | 59 | 2 | 0 | 116 | 0.30x | react_ts, python_api, prisma, mt5, scraper, cron |
| examples/golden/04_alerting_monitor.ainl | non-strict-only | 373 | 11 | 7 | 37 | 59 | 2 | 0 | 116 | 0.31x | react_ts, python_api, prisma, mt5, scraper, cron |
| examples/golden/05_file_processor.ainl | non-strict-only | 481 | 11 | 7 | 38 | 63 | 2 | 0 | 121 | 0.25x | react_ts, python_api, prisma, mt5, scraper, cron |
| examples/internal_tool.lang | non-strict-only | 127 | 83 | 16 | 43 | 87 | 2 | 9 | 240 | 1.89x | react_ts, python_api, prisma, mt5, scraper, cron |
| examples/openclaw/daily_digest.lang | non-strict-only | 134 | 11 | 7 | 37 | 59 | 2 | 0 | 116 | 0.87x | react_ts, python_api, prisma, mt5, scraper, cron |
| examples/openclaw/daily_digest.strict.lang | non-strict-only | 254 | 11 | 7 | 45 | 75 | 2 | 0 | 140 | 0.55x | react_ts, python_api, prisma, mt5, scraper, cron |
| examples/openclaw/infrastructure_watchdog.lang | non-strict-only | 189 | 11 | 7 | 37 | 59 | 2 | 0 | 116 | 0.61x | react_ts, python_api, prisma, mt5, scraper, cron |
| examples/openclaw/lead_enrichment.lang | non-strict-only | 178 | 11 | 7 | 17 | 51 | 2 | 0 | 88 | 0.49x | react_ts, python_api, prisma, mt5, scraper, cron |
| examples/openclaw/webhook_handler.lang | non-strict-only | 150 | 11 | 10 | 29 | 67 | 2 | 0 | 119 | 0.79x | react_ts, python_api, prisma, mt5, scraper, cron |
| examples/ticketing.lang | non-strict-only | 153 | 104 | 22 | 43 | 87 | 2 | 0 | 258 | 1.69x | react_ts, python_api, prisma, mt5, scraper, cron |

## Details (minimal_emit)

| Profile | Artifact count | AINL source total | Aggregate generated output total | Aggregate ratio |
|---|---:|---:|---:|---:|
| canonical_strict_valid | 5 | 88 | 55 | 0.62x |
| public_mixed | 21 | 3516 | 1094 | 0.31x |
| compatibility_only | 16 | 3428 | 1039 | 0.30x |

### canonical_strict_valid
| Artifact | Class | AINL source | React/TS | Python API | Prisma | MT5 | Scraper | Cron | Aggregate generated output | Aggregate ratio | Included targets |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| examples/crud_api.ainl | strict-valid | 20 | - | 7 | - | - | - | - | 7 | 0.35x | python_api |
| examples/hello.ainl | strict-valid | 8 | - | 7 | - | - | - | - | 7 | 0.88x | python_api |
| examples/rag_pipeline.ainl | strict-valid | 14 | - | 7 | - | - | - | - | 7 | 0.50x | python_api |
| examples/scraper/basic_scraper.ainl | strict-valid | 29 | - | - | - | - | 15 | 9 | 24 | 0.83x | scraper, cron |
| examples/web/basic_web_api.ainl | strict-valid | 17 | - | 10 | - | - | - | - | 10 | 0.59x | python_api |

### public_mixed
| Artifact | Class | AINL source | React/TS | Python API | Prisma | MT5 | Scraper | Cron | Aggregate generated output | Aggregate ratio | Included targets |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| examples/api_only.lang | non-strict-only | 62 | - | 16 | 39 | - | - | - | 55 | 0.89x | python_api, prisma |
| examples/blog.lang | non-strict-only | 135 | 83 | 19 | 45 | - | - | - | 147 | 1.09x | react_ts, python_api, prisma |
| examples/cron/monitor_and_alert.ainl | non-strict-only | 35 | - | - | - | - | - | 9 | 9 | 0.26x | cron |
| examples/crud_api.ainl | strict-valid | 20 | - | 7 | - | - | - | - | 7 | 0.35x | python_api |
| examples/ecom.lang | non-strict-only | 137 | 106 | 16 | 41 | - | - | - | 163 | 1.19x | react_ts, python_api, prisma |
| examples/golden/01_web_server.ainl | non-strict-only | 304 | - | - | 38 | - | - | 0 | 38 | 0.12x | prisma, cron |
| examples/golden/02_dashboard.ainl | non-strict-only | 335 | - | - | 37 | - | - | 0 | 37 | 0.11x | prisma, cron |
| examples/golden/03_scraper.ainl | non-strict-only | 381 | - | - | 37 | - | - | 0 | 37 | 0.10x | prisma, cron |
| examples/golden/04_alerting_monitor.ainl | non-strict-only | 373 | - | - | 37 | - | - | 0 | 37 | 0.10x | prisma, cron |
| examples/golden/05_file_processor.ainl | non-strict-only | 481 | - | - | 38 | - | - | 0 | 38 | 0.08x | prisma, cron |
| examples/hello.ainl | strict-valid | 8 | - | 7 | - | - | - | - | 7 | 0.88x | python_api |
| examples/internal_tool.lang | non-strict-only | 127 | 83 | 16 | 43 | - | - | 9 | 151 | 1.19x | react_ts, python_api, prisma, cron |
| examples/openclaw/daily_digest.lang | non-strict-only | 134 | - | - | 37 | - | - | 0 | 37 | 0.28x | prisma, cron |
| examples/openclaw/daily_digest.strict.lang | non-strict-only | 254 | - | - | 45 | - | - | 0 | 45 | 0.18x | prisma, cron |
| examples/openclaw/infrastructure_watchdog.lang | non-strict-only | 189 | - | - | 37 | - | - | 0 | 37 | 0.20x | prisma, cron |
| examples/openclaw/lead_enrichment.lang | non-strict-only | 178 | - | - | - | - | - | 0 | 0 | 0.00x | cron |
| examples/openclaw/webhook_handler.lang | non-strict-only | 150 | - | 10 | 29 | - | - | - | 39 | 0.26x | python_api, prisma |
| examples/rag_pipeline.ainl | strict-valid | 14 | - | 7 | - | - | - | - | 7 | 0.50x | python_api |
| examples/scraper/basic_scraper.ainl | strict-valid | 29 | - | - | - | - | 15 | 9 | 24 | 0.83x | scraper, cron |
| examples/ticketing.lang | non-strict-only | 153 | 104 | 22 | 43 | - | - | - | 169 | 1.10x | react_ts, python_api, prisma |
| examples/web/basic_web_api.ainl | strict-valid | 17 | - | 10 | - | - | - | - | 10 | 0.59x | python_api |

### compatibility_only
| Artifact | Class | AINL source | React/TS | Python API | Prisma | MT5 | Scraper | Cron | Aggregate generated output | Aggregate ratio | Included targets |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| examples/api_only.lang | non-strict-only | 62 | - | 16 | 39 | - | - | - | 55 | 0.89x | python_api, prisma |
| examples/blog.lang | non-strict-only | 135 | 83 | 19 | 45 | - | - | - | 147 | 1.09x | react_ts, python_api, prisma |
| examples/cron/monitor_and_alert.ainl | non-strict-only | 35 | - | - | - | - | - | 9 | 9 | 0.26x | cron |
| examples/ecom.lang | non-strict-only | 137 | 106 | 16 | 41 | - | - | - | 163 | 1.19x | react_ts, python_api, prisma |
| examples/golden/01_web_server.ainl | non-strict-only | 304 | - | - | 38 | - | - | 0 | 38 | 0.12x | prisma, cron |
| examples/golden/02_dashboard.ainl | non-strict-only | 335 | - | - | 37 | - | - | 0 | 37 | 0.11x | prisma, cron |
| examples/golden/03_scraper.ainl | non-strict-only | 381 | - | - | 37 | - | - | 0 | 37 | 0.10x | prisma, cron |
| examples/golden/04_alerting_monitor.ainl | non-strict-only | 373 | - | - | 37 | - | - | 0 | 37 | 0.10x | prisma, cron |
| examples/golden/05_file_processor.ainl | non-strict-only | 481 | - | - | 38 | - | - | 0 | 38 | 0.08x | prisma, cron |
| examples/internal_tool.lang | non-strict-only | 127 | 83 | 16 | 43 | - | - | 9 | 151 | 1.19x | react_ts, python_api, prisma, cron |
| examples/openclaw/daily_digest.lang | non-strict-only | 134 | - | - | 37 | - | - | 0 | 37 | 0.28x | prisma, cron |
| examples/openclaw/daily_digest.strict.lang | non-strict-only | 254 | - | - | 45 | - | - | 0 | 45 | 0.18x | prisma, cron |
| examples/openclaw/infrastructure_watchdog.lang | non-strict-only | 189 | - | - | 37 | - | - | 0 | 37 | 0.20x | prisma, cron |
| examples/openclaw/lead_enrichment.lang | non-strict-only | 178 | - | - | - | - | - | 0 | 0 | 0.00x | cron |
| examples/openclaw/webhook_handler.lang | non-strict-only | 150 | - | 10 | 29 | - | - | - | 39 | 0.26x | python_api, prisma |
| examples/ticketing.lang | non-strict-only | 153 | 104 | 22 | 43 | - | - | - | 169 | 1.10x | react_ts, python_api, prisma |

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
