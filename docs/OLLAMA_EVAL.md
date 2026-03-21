# Local Ollama Evaluation

Use this harness to measure whether a local model can generate valid AINL quickly and reliably.

## Prerequisites

- Ollama running locally (`http://127.0.0.1:11434`)
- A pulled model (example: `qwen2.5:7b`)
- Project installed (`pip install -e ".[dev]"`)

## Run evaluation

```bash
ainl-ollama-eval --model qwen2.5:7b --prompts data/evals/ollama_prompts.jsonl
```

With end-to-end viability checks enabled (compile + server boot + endpoint probes):

```bash
ainl-ollama-eval --model qwen2.5:7b --prompts data/evals/ollama_prompts.jsonl --with-viability
```

With deterministic retrieval playbooks + targeted retries:

```bash
ainl-ollama-eval --model qwen2.5:7b \
  --prompts data/evals/ollama_prompts.jsonl \
  --with-playbook --playbooks data/evals/playbooks/default.jsonl \
  --max-retries 1 \
  --with-viability
```

Output:

- Console JSON summary
- Report file: `data/evals/ollama_eval_report.json`

## Benchmark multiple models

```bash
ainl-ollama-benchmark --models qwen2.5:7b,llama3.1:8b --prompts data/evals/ollama_prompts.jsonl
```

`--models` can be omitted if you only run a cloud baseline (see below).

Output:

- Ranked report: `data/evals/ollama_benchmark_report.json`
- Ranking keys: pass rate (desc), avg error count (asc), elapsed time (asc)
- **Stderr:** markdown table “Model comparison (Ollama + optional cloud)” for quick diffs
- Optional summary CSV:

```bash
ainl-ollama-benchmark --models qwen2.5:7b,llama3.1:8b \
  --csv-out data/evals/ollama_benchmark_summary.csv \
  --with-viability
```

### Optional: Anthropic Claude (cloud baseline)

Run the **same** prompt suite through **Claude 3.5 Sonnet** (Messages API, `temperature=0`) alongside local Ollama models:

```bash
pip install -e ".[anthropic]"
export ANTHROPIC_API_KEY=...
ainl-ollama-benchmark --models qwen2.5:7b --cloud-model claude-3-5-sonnet --prompts data/evals/ollama_prompts.jsonl
```

- Alias `claude-3-5-sonnet` resolves to a pinned API model id; pass a full Anthropic model string to override.
- If the key is missing or `anthropic` is not installed, the cloud leg is **skipped** with a stderr warning; Ollama results still print.
- JSON field `cloud_model_comparison` holds the cloud summary (or `{ "skipped": true, "reason": ... }`).

Standalone viability check for one `.lang` file:

```bash
ainl-check-viability examples/hello.lang
```

## Metrics included

- `pass_rate`: strict compile success rate
- per-case `error_count` and sample `errors`
- generated character count and IR stats
- per-case `guidance_items`: normalized failure hints as `{code, message}`
- report-level `top_guidance`: most frequent guidance codes with counts

## Guidance code reference

Use `guidance_items[].code` and `top_guidance[].code` for stable analytics keys.

| Code | Meaning |
|---|---|
| `LABEL_SCOPE` | Top-level declarations were placed inside a label block. |
| `UNKNOWN_OP` | Generated op is not recognized by canonical AINL op set. |
| `ARITY` | Operation argument count/slot shape is invalid. |
| `LABEL_TARGET` | One or more `->L<n>` targets are missing or invalidly structured. |
| `STRING_UNTERMINATED` | Quoted string was not properly closed. |
| `STRICT_VALIDATION` | Generic strict-mode failure that did not match a specific code. |
| `CONTRACT_VIOLATION` | Declared Contract metadata mismatches available endpoints. |
| `POLICY_VIOLATION` | Policy gate failed (auth/role/policy invariant mismatch). |
| `COMPAT_BREAK` | Compatibility gate detected breaking endpoint/type changes. |
| `PATCH_CONFLICT` | Patch-mode merge conflict requires explicit replace. |

## JSON output example

```json
{
  "model": "qwen2.5:7b",
  "cases": 2,
  "pass_rate": 0.5,
  "top_guidance": [
    {
      "code": "LABEL_SCOPE",
      "message": "Avoid top-level ops (S/D/E/U/Role/Desc) inside label blocks. Start a new label after J/R steps, or move declarations above labels.",
      "count": 1
    }
  ],
  "results": [
    {
      "id": "case_ok",
      "ok": true,
      "error_count": 0,
      "guidance_items": []
    },
    {
      "id": "case_bad_label_scope",
      "ok": false,
      "error_count": 1,
      "errors": [
        "Line 9: auto-closed label L1 on top-level op 'E' inside label block"
      ],
      "guidance_items": [
        {
          "code": "LABEL_SCOPE",
          "message": "Avoid top-level ops (S/D/E/U/Role/Desc) inside label blocks. Start a new label after J/R steps, or move declarations above labels."
        }
      ]
    }
  ]
}
```

## Extend prompts

Add JSONL lines to `data/evals/ollama_prompts.jsonl`:

```json
{"id":"my_case","prompt":"Create AINL for ..."}
```

## Agent loop integration

Pair this with `ainl-tool-api` and the tool API schema at:

- `tooling/ainl_tool_api.schema.json`
