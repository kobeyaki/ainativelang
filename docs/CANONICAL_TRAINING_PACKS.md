# Canonical Training Packs

This doc explains how to export the strict-valid canonical curriculum into portable
training/prompt/eval bundles for small-model workflows.

## Source Of Truth

- `tooling/canonical_curriculum.json` (teaching order + lesson ownership)
- `tooling/artifact_profiles.json` (`strict-valid` classification)

The pack generator derives from those files; it does not redefine canonical ownership.

## Generate Packs

```bash
python scripts/build_canonical_training_pack.py
```

Generated outputs:

- `tooling/canonical_training_pack.json` (canonical training manifest)
- `tooling/training_packs/full_ordered.fewshot.{jsonl,md}`
- `tooling/training_packs/starter.fewshot.{jsonl,md}`
- `tooling/training_packs/workflow.fewshot.{jsonl,md}`
- `tooling/training_packs/resilience.fewshot.{jsonl,md}`
- `tooling/training_packs/canonical.eval.{jsonl,json}`

## Which Pack To Use

- **Small finetunes**: `full_ordered.fewshot.jsonl`
- **Few-shot prompting quickstart**: `starter.fewshot.jsonl`
- **Agent builders / workflow prompting**: `workflow.fewshot.jsonl`
- **Retry/error hardening prompts**: `resilience.fewshot.jsonl`
- **Eval harness baselines**: `canonical.eval.jsonl`

## Notes

- Canonical packs are strict-valid only; non-strict/compatibility examples are excluded.
- These packs are portable exports, not semantic evaluators by themselves.
- Keep benchmark optimization paused while using this curriculum for training/prompting work.
