#!/usr/bin/env bash
set -euo pipefail

ROOT="/Users/clawdbot/.openclaw/workspace/AI_Native_Lang"
VENV="$ROOT/.venv-ci-smoke"
PY_BIN="${PYTHON_BIN:-python3}"

echo "Setting up fine-tune environment..."
if [ ! -d "$VENV" ]; then
  "$PY_BIN" -m venv "$VENV"
fi

"$VENV/bin/python" -m pip install --upgrade pip
"$VENV/bin/python" -m pip install datasets transformers accelerate peft sentencepiece pytest

echo "Running corpus pipeline preflight..."
"$VENV/bin/python" "$ROOT/scripts/generate_corpus.py"
"$VENV/bin/python" "$ROOT/scripts/generate_negative_examples.py"
"$VENV/bin/python" "$ROOT/scripts/curate_corpus.py"
"$VENV/bin/python" "$ROOT/scripts/evaluate_corpus.py" --mode dual
"$VENV/bin/python" "$ROOT/scripts/convert_to_training.py"
"$VENV/bin/python" "$ROOT/scripts/validate_corpus.py" --include-negatives
"$VENV/bin/python" "$ROOT/scripts/finetune_ainl.py" --dry-run

echo "Environment ready."
echo "Run training with:"
echo "  $VENV/bin/python $ROOT/scripts/finetune_ainl.py --epochs 1"
