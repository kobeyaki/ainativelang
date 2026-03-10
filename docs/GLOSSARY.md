# AI Native Lang (AINL) Glossary

## AINL
AI Native Lang. A language designed for AI-first authoring and execution workflows.

## Canonical AINL
The strict, line-oriented AINL form used for validation, training targets, and evaluation.

## IR (Intermediate Representation)
The compiler output graph/step structure used by runtimes and emitters.

## Graph-First Runtime
Execution mode that prioritizes graph semantics and uses step fallback only when needed.

## Adapter
A runtime integration surface for external capabilities (HTTP, DB, files, tools, etc.).

## LoRA
Low-Rank Adaptation fine-tuning strategy used to adapt base models efficiently.

## Strict AINL Rate
Share of prompts where output is non-empty, AINL-like, and passes strict compile checks.

## Runtime Compile Rate
Share of outputs that pass runtime (non-strict) compile validation.

## Nonempty Rate
Share of prompts producing non-empty output.

## Constraint Diagnostics
Telemetry emitted during constrained decoding (allowed/rejected tokens, fallback, EOS gating).

## Failure Family
A normalized category of generation failure (timeout, shape mismatch, compile failure, etc.).

## Prompt-Length Bucket
Grouping prompts by rendered token length to improve shape stability and analysis granularity.

## Checkpoint Sweep
Evaluating checkpoints and ranking them by task metrics instead of raw eval loss.

## Trend Gate
Cross-run quality gate enforcing minimum rates and maximum allowed regressions.

## Run Health Report
Machine-readable pass/fail summary artifact for automation:
`corpus/curated/alignment_run_health.json`.

## Distill Mix
Training-data composition strategy mixing gold examples and repair/check-rewrite supervision.

## Failure Boost Dataset
Targeted dataset generated from failing prompt IDs to improve weak families.
