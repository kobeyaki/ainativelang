# AI Native Lang (AINL) Fine‑Tuning Quick Start

This guide trains a small model (<4GB) to generate correct AINL programs. Target hardware: MacBook Pro M2 (16GB RAM) or similar.

For full production-aligned train/eval orchestration, see:
- `docs/TRAINING_ALIGNMENT_RUNBOOK.md`
- `scripts/run_alignment_cycle.sh`

## 1. Prerequisites

```bash
# One-command setup (recommended)
bash scripts/setup_finetune_env.sh
```

Manual setup (if needed):

```bash
python -m venv .venv-ci-smoke
.venv-ci-smoke/bin/python -m pip install datasets transformers accelerate peft sentencepiece pytest
```

## 2. Dataset

- Positive examples: `corpus/curated/pos.jsonl` and `corpus/curated/full_workflows.jsonl`
- Combined (full): `corpus/train_chatml.jsonl`
- Training split used by default for fine-tuning: `corpus/train_chatml_train.jsonl`
- Holdout splits: `corpus/train_chatml_val.jsonl`, `corpus/train_chatml_test.jsonl`

Negative examples (invalid) are for evaluation only; they are *not* used during supervised fine‑tuning unless you employ contrastive learning.

## 3. Model Choice

Recommended small models (easy to fine‑tune on CPU/MPS):
- **Phi‑3 mini** (3.8B, ~2.5GB 4‑bit quantized) — excellent at code, small
- **Gemma 2B** (2B, ~1.5GB 4‑bit) — lightweight
- **TinyLlama 1.1B** (1.1B, ~0.7GB)

We'll use Phi‑3 mini as the example.

## 4. Training Script (LoRA)

Use the existing script: `scripts/finetune_ainl.py`.
It now supports:
- `--dry-run` for fast preflight without training
- `--profile fast|balanced|quality` for speed/quality presets
- `--epochs` to control epoch count
- `--max-length` to control sequence length
- `--seed` for reproducible runs
- `--data-path` to select train/val/test file explicitly
- `--max-train-samples` for quick iteration runs

## 5. Running

```bash
.venv-ci-smoke/bin/python scripts/finetune_ainl.py --dry-run
.venv-ci-smoke/bin/python scripts/finetune_ainl.py --profile fast --epochs 1 --seed 42
```

Expected time: ~30–60 minutes on M2 Pro (using CPU/MPS).

## 6. Evaluation

Run `scripts/evaluate_corpus.py --mode dual` to get strict and runtime metrics.
Run `scripts/validate_corpus.py --include-negatives` so negative rows are enforced as expected failures.

## 7. Post-Train Inference (Option A: Stable Loader)

Use the dedicated inference helper:

```bash
.venv/bin/python scripts/infer_ainl_lora.py \
  --adapter-path models/ainl-phi3-lora \
  --max-new-tokens 120 \
  --device cpu
```

Notes:
- `--device cpu` is the most stable path on mixed `transformers`/`peft` versions.
- You can try `--device mps` for speed on Apple Silicon after CPU sanity passes.
- Override prompt inline with `--prompt "..."`.

## 8. Next Steps

- Expand corpus to >1000 examples
- Include negative examples via contrastive loss
- Add adapter discovery and patterns to prompts
- Implement a small model LSP with autocomplete

## 9. Recommended One-Command Alignment Flow

If you want checkpoint selection, constrained eval gates, trend regression checks,
and machine-readable run health in one execution:

```bash
bash scripts/run_alignment_cycle.sh models/ainl-phi3-lora-vX 24 1 30 1 40 3
```

Then inspect:
- `corpus/curated/checkpoint_sweep_report_v5_aligned.json`
- `corpus/curated/model_eval_report_v5_aligned.json`
- `corpus/curated/model_eval_trends.json`
- `corpus/curated/alignment_run_health.json`
