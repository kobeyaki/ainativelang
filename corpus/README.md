# AI Native Lang (AINL) Training Corpus Skeleton

This directory is reserved for a **small, clean training corpus** aimed at 3B–7B parameter models learning AINL.

Each example lives in its own subdirectory:

```text
corpus/
  example_name/
    prompt.txt            # natural language description
    program.ainl          # canonical valid program
    corrected_program.ainl# corrected version of invalid program
    invalid_program.ainl  # intentionally flawed program
    ir.json               # compiled IR for canonical program (optional but recommended)
    errors.json           # expected compiler/tooling errors for invalid program
```

Guidelines:

- Keep the entire corpus under **~100MB**.
- Prefer high‑signal, well‑commented examples over breadth.
- Include:
  - Valid programs (prompt → program → IR).
  - Invalid programs (invalid_program → errors.json explaining issues).
  - Corrected programs (corrected_program) that fix invalid patterns.

The intent is that small models can be fine‑tuned or instruction‑tuned on this corpus to become reliable AINL co‑programmers.

Current seeds:

- `example_basic_web_api`
- `example_scraper_daily`
- `example_monitor_alert`

## Compile-profile classification

Corpus artifacts are explicitly profiled in `tooling/artifact_profiles.json`:

- `strict-valid`: intended to compile under strict mode
- `non-strict-only`: intentional compatibility examples
- `legacy-compat`: retained for training/repair context; not strict conformance targets

Important: `invalid_program.ainl` files are training artifacts and may still parse/compile depending on strictness and evolving compiler checks; treat them as supervised repair inputs, not release-surface conformance samples.
