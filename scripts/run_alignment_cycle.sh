#!/usr/bin/env bash
set -euo pipefail

# One-command alignment cycle:
# 1) build larger paired supervision set
# 2) optionally build teacher-distill supervision set
# 3) train adapter
# 4) run constrained+repair evaluation gate

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PY="${ROOT}/.venv/bin/python"

ADAPTER_OUT="${1:-models/ainl-phi3-lora-v5-aligned}"
VARIANTS_PER_PROMPT="${2:-24}"
EPOCHS="${3:-2}"
MAX_NEW_TOKENS="${4:-40}"
DISTILL_MODE="${5:-1}"
SAMPLES_PER_PROMPT="${6:-40}"
TOP_K="${7:-3}"
BOOST_EVAL_REPORT="${8:-}"
MIN_STRICT_RATE="${9:-0.60}"
MIN_RUNTIME_RATE="${10:-0.75}"
MIN_NONEMPTY_RATE="${11:-0.70}"
MAX_REGRESSION_STRICT="${12:-0.05}"
MAX_REGRESSION_RUNTIME="${13:-0.05}"
MAX_REGRESSION_NONEMPTY="${14:-0.05}"
QUANTIZATION_MODE="${15:-none}"
CANONICALIZE_CHUNK_LINES="${16:-256}"
CANONICALIZE_MAX_LINES="${17:-512}"

cd "${ROOT}"

echo "[cycle] Building regression supervision (variants=${VARIANTS_PER_PROMPT})"
"${PY}" scripts/build_regression_supervision.py --seed 42 --variants-per-prompt "${VARIANTS_PER_PROMPT}" --min-lines 3

TRAIN_DATA="corpus/train_chatml_regression_supervised_train.jsonl"
EVAL_DATA="corpus/train_chatml_regression_supervised_val.jsonl"

if [[ "${DISTILL_MODE}" == "1" ]]; then
  echo "[cycle] Building teacher distill dataset"
  "${PY}" scripts/teacher_distill_dataset.py \
    --seed 42 \
    --variants-per-prompt "${VARIANTS_PER_PROMPT}" \
    --samples-per-prompt "${SAMPLES_PER_PROMPT}" \
    --mix-gold 0.50 \
    --mix-repair 0.35 \
    --mix-check 0.15 \
    --min-lines 3
  TRAIN_DATA="corpus/train_chatml_distill_train.jsonl"
  EVAL_DATA="corpus/train_chatml_distill_val.jsonl"
fi

if [[ -n "${BOOST_EVAL_REPORT}" ]]; then
  echo "[cycle] Building failure-focused boost dataset from ${BOOST_EVAL_REPORT}"
  "${PY}" scripts/build_failure_boost_dataset.py \
    --eval-report "${BOOST_EVAL_REPORT}" \
    --seed 42 \
    --samples-per-failed-id 48 \
    --variants-per-prompt "${VARIANTS_PER_PROMPT}" \
    --mix-gold 0.50 \
    --mix-repair 0.35 \
    --mix-check 0.15
  TRAIN_DATA="corpus/train_chatml_distill_boost_train.jsonl"
  EVAL_DATA="corpus/train_chatml_distill_boost_val.jsonl"
fi

echo "[cycle] Training adapter -> ${ADAPTER_OUT}"
"${PY}" scripts/finetune_ainl.py \
  --profile balanced \
  --epochs "${EPOCHS}" \
  --seed 42 \
  --data-path "${TRAIN_DATA}" \
  --eval-data-path "${EVAL_DATA}" \
  --output-dir "${ADAPTER_OUT}" \
  --max-length 768 \
  --batch-size 1 \
  --grad-accum 1 \
  --logging-steps 10 \
  --eval-steps 20 \
  --save-steps 20 \
  --save-total-limit 12 \
  --train-device mps

SWEEP_REPORT="corpus/curated/checkpoint_sweep_report_v5_aligned.json"
echo "[cycle] Sweeping checkpoints by strict AINL metric -> ${SWEEP_REPORT}"
"${PY}" scripts/sweep_checkpoints.py \
  --adapter-root "${ADAPTER_OUT}" \
  --prompt-set corpus/curated/regression_prompts.jsonl \
  --output-json "${SWEEP_REPORT}" \
  --top-k "${TOP_K}" \
  --max-new-tokens "${MAX_NEW_TOKENS}" \
  --device mps \
  --heartbeat-seconds 5 \
  --generation-timeout-seconds 180 \
  --constrained-decoding \
  --repair-attempts 2 \
  --canonicalize-output \
  --emit-timing \
  --constraint-diagnostics \
  --bucket-by-prompt-length \
  --canonicalize-chunk-lines "${CANONICALIZE_CHUNK_LINES}" \
  --canonicalize-max-lines "${CANONICALIZE_MAX_LINES}" \
  --quantization-mode "${QUANTIZATION_MODE}" \
  --promote-best-link \
  --prune-non-topk

SELECTED_ADAPTER="${ADAPTER_OUT}"
if [[ -e "${ADAPTER_OUT}/best_by_strict_ainl" ]]; then
  SELECTED_ADAPTER="${ADAPTER_OUT}/best_by_strict_ainl"
fi

REPORT_PATH="corpus/curated/model_eval_report_v5_aligned.json"
echo "[cycle] Running constrained+repair gate on selected adapter -> ${REPORT_PATH}"
"${PY}" scripts/eval_finetuned_model.py \
  --adapter-path "${SELECTED_ADAPTER}" \
  --prompt-set corpus/curated/regression_prompts.jsonl \
  --output-json "${REPORT_PATH}" \
  --max-new-tokens "${MAX_NEW_TOKENS}" \
  --device mps \
  --heartbeat-seconds 5 \
  --generation-timeout-seconds 180 \
  --constrained-decoding \
  --repair-attempts 2 \
  --canonicalize-output \
  --emit-timing \
  --constraint-diagnostics \
  --bucket-by-prompt-length \
  --canonicalize-chunk-lines "${CANONICALIZE_CHUNK_LINES}" \
  --canonicalize-max-lines "${CANONICALIZE_MAX_LINES}" \
  --quantization-mode "${QUANTIZATION_MODE}"

TREND_REPORT="corpus/curated/model_eval_trends.json"
RUN_HEALTH_REPORT="corpus/curated/alignment_run_health.json"
echo "[cycle] Building eval trend view -> ${TREND_REPORT}"
"${PY}" scripts/analyze_eval_trends.py \
  --reports-dir corpus/curated \
  --glob "model_eval_report*.json" \
  --output-json "${TREND_REPORT}" \
  --latest-n 25 \
  --min-lora-strict-ainl-rate "${MIN_STRICT_RATE}" \
  --min-lora-runtime-rate "${MIN_RUNTIME_RATE}" \
  --min-lora-nonempty-rate "${MIN_NONEMPTY_RATE}" \
  --max-regression-strict "${MAX_REGRESSION_STRICT}" \
  --max-regression-runtime "${MAX_REGRESSION_RUNTIME}" \
  --max-regression-nonempty "${MAX_REGRESSION_NONEMPTY}" \
  --enforce-gate

echo "[cycle] Writing run health summary -> ${RUN_HEALTH_REPORT}"
"${PY}" - <<'PY'
import json
from pathlib import Path

root = Path(".")
report_path = root / "corpus/curated/model_eval_report_v5_aligned.json"
sweep_path = root / "corpus/curated/checkpoint_sweep_report_v5_aligned.json"
trend_path = root / "corpus/curated/model_eval_trends.json"
out_path = root / "corpus/curated/alignment_run_health.json"

def _load(path: Path):
    if not path.exists():
        return {}
    with open(path, encoding="utf-8") as f:
        return json.load(f)

rep = _load(report_path)
sweep = _load(sweep_path)
trend = _load(trend_path)
summary = (rep.get("summary") or {}).get("lora") or {}
gate = ((trend.get("summary") or {}).get("gate") or {})
selected = (sweep.get("selected") or [])
top1 = selected[0] if selected else {}

out = {
    "status": "pass" if gate.get("passed") else "fail",
    "artifacts": {
        "eval_report": str(report_path),
        "sweep_report": str(sweep_path),
        "trend_report": str(trend_path),
    },
    "selected_adapter": rep.get("adapter_path"),
    "metrics": {
        "strict_ainl_rate": float(summary.get("strict_ainl_rate", 0.0)),
        "runtime_compile_rate": float(summary.get("runtime_compile_rate", 0.0)),
        "nonempty_rate": float(summary.get("nonempty_rate", 0.0)),
    },
    "checkpoint_top1": {
        "adapter_path": top1.get("adapter_path"),
        "strict_ainl_rate": float(top1.get("strict_ainl_rate", 0.0)),
        "runtime_compile_rate": float(top1.get("runtime_compile_rate", 0.0)),
        "nonempty_rate": float(top1.get("nonempty_rate", 0.0)),
    },
    "gate": gate,
}
out_path.parent.mkdir(parents=True, exist_ok=True)
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(out, f, indent=2)
print(f"Run health written: {out_path}")
PY

echo "[cycle] Done. Reports: ${REPORT_PATH}, ${SWEEP_REPORT}, ${TREND_REPORT}, ${RUN_HEALTH_REPORT}"
