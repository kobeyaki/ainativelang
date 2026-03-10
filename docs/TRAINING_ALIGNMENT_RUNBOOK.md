# Training Alignment Runbook

This runbook documents the end-to-end AINL model alignment pipeline currently used
in this repository.

## Purpose

Run one command that:

1. builds supervision datasets,
2. trains LoRA,
3. sweeps checkpoints by task metrics,
4. runs final constrained eval gate,
5. computes trends + pass/fail gate,
6. writes machine-readable run health.

Entrypoint: `scripts/run_alignment_cycle.sh`

## Command Shape

```bash
bash scripts/run_alignment_cycle.sh \
  [ADAPTER_OUT] \
  [VARIANTS_PER_PROMPT] \
  [EPOCHS] \
  [MAX_NEW_TOKENS] \
  [DISTILL_MODE] \
  [SAMPLES_PER_PROMPT] \
  [TOP_K] \
  [BOOST_EVAL_REPORT] \
  [MIN_STRICT_RATE] \
  [MIN_RUNTIME_RATE] \
  [MIN_NONEMPTY_RATE] \
  [MAX_REGRESSION_STRICT] \
  [MAX_REGRESSION_RUNTIME] \
  [MAX_REGRESSION_NONEMPTY] \
  [QUANTIZATION_MODE] \
  [CANONICALIZE_CHUNK_LINES] \
  [CANONICALIZE_MAX_LINES]
```

## Argument Reference

- `ADAPTER_OUT` (default `models/ainl-phi3-lora-v5-aligned`): output adapter root
- `VARIANTS_PER_PROMPT` (default `24`): prompt variant count for dataset builders
- `EPOCHS` (default `2`): fine-tune epochs
- `MAX_NEW_TOKENS` (default `40`): generation budget for sweep/final gate
- `DISTILL_MODE` (default `1`): include teacher-distill dataset stage (`1` on)
- `SAMPLES_PER_PROMPT` (default `40`): distill mix target size
- `TOP_K` (default `3`): checkpoints to retain after sweep
- `BOOST_EVAL_REPORT` (default empty): optional eval report path for failure-focused boost dataset
- `MIN_STRICT_RATE` (default `0.60`): trend gate minimum strict AINL rate
- `MIN_RUNTIME_RATE` (default `0.75`): trend gate minimum runtime compile rate
- `MIN_NONEMPTY_RATE` (default `0.70`): trend gate minimum nonempty output rate
- `MAX_REGRESSION_STRICT` (default `0.05`): allowed strict rate drop vs previous report
- `MAX_REGRESSION_RUNTIME` (default `0.05`): allowed runtime compile drop vs previous report
- `MAX_REGRESSION_NONEMPTY` (default `0.05`): allowed nonempty drop vs previous report
- `QUANTIZATION_MODE` (`none|dynamic-int8`, default `none`): eval/infer quantization mode
- `CANONICALIZE_CHUNK_LINES` (default `256`): chunk size for host-side canonicalization
- `CANONICALIZE_MAX_LINES` (default `512`): cap retained canonicalized lines

## Stage-by-Stage Flow

### Stage 1: Regression supervision build

Script: `scripts/build_regression_supervision.py`

Key behavior:
- generates canonical paired supervision
- enforces minimum complexity (`--min-lines 3`)

### Stage 2: Teacher distillation build (optional)

Script: `scripts/teacher_distill_dataset.py`

Mix used by cycle:
- `50% gold`
- `35% repair`
- `15% check-rewrite`

### Stage 3: Optional failure-family boost build

Script: `scripts/build_failure_boost_dataset.py`

If `BOOST_EVAL_REPORT` is provided, failing prompt IDs from that report get targeted
extra supervision.

### Stage 4: Fine-tuning

Script: `scripts/finetune_ainl.py`

Cycle default profile:
- balanced profile
- MPS device
- frequent save/eval checkpoints for sweep selection

### Stage 5: Checkpoint sweep

Script: `scripts/sweep_checkpoints.py`

Ranking priority:
1. `strict_ainl_rate`
2. `runtime_compile_rate`
3. `nonempty_rate`

Configured with:
- constrained decoding
- repair attempts
- canonicalization
- prompt length bucketing
- diagnostics emission
- optional quantization mode forwarding

### Stage 6: Final eval gate (selected checkpoint)

Script: `scripts/eval_finetuned_model.py`

Configured with:
- constrained decoding
- repair loop
- canonicalization with chunk bounds
- prompt-length bucketing
- timing + constraint diagnostics
- optional quantization mode

### Stage 7: Trend analysis + quality gate

Script: `scripts/analyze_eval_trends.py`

Gate behavior:
- enforces absolute minimum quality thresholds
- enforces regression limits vs previous report
- exits non-zero on gate failure

### Stage 8: Run health summary

Writes: `corpus/curated/alignment_run_health.json`

Contains:
- pass/fail status
- selected adapter
- top metrics
- gate details
- artifact pointers

## Artifacts to Inspect After a Run

- `corpus/curated/checkpoint_sweep_report_v5_aligned.json`
- `corpus/curated/model_eval_report_v5_aligned.json`
- `corpus/curated/model_eval_trends.json`
- `corpus/curated/alignment_run_health.json`

## Quick Validation Commands

```bash
python scripts/analyze_eval_trends.py --help
python scripts/eval_finetuned_model.py --help
python scripts/sweep_checkpoints.py --help
```

## Troubleshooting

- **High fallback rate / EOS never allowed**
  - inspect `constraint_health` alerts in eval diagnostics
  - adjust grammar/strict-prefix rules or EOS minimum-structure gating

- **Gate fails despite low eval loss**
  - this is expected if structure/compile metrics regress
  - select checkpoints by strict/runtime metrics (already sweep default)

- **Long eval runtimes**
  - reduce prompt set size for sweeps (`--limit`)
  - reduce `MAX_NEW_TOKENS`
  - keep prompt-length bucketing enabled

- **Quantization instability**
  - use `QUANTIZATION_MODE=none`
  - dynamic-int8 is safe only on CPU path; scripts fall back automatically
