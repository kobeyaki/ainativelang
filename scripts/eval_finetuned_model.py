#!/usr/bin/env python3
"""
Evaluate a fine-tuned AINL LoRA model against the base model.

Automates:
1) sanity generation
2) multi-prompt functional generation
3) compile validation (runtime + strict)
4) side-by-side baseline comparison
5) regression prompt-set scorecard output
"""

import argparse
import json
import gc
import copy
import sys
import time
import threading
import re
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional


BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE))
DEFAULT_ADAPTER = BASE / "models" / "ainl-phi3-lora"
DEFAULT_BASE_MODEL = "microsoft/phi-3-mini-4k-instruct"
DEFAULT_PROMPTS = BASE / "corpus" / "curated" / "regression_prompts.jsonl"
DEFAULT_OUT = BASE / "corpus" / "curated" / "model_eval_report.json"
AINL_LINE_RE = (
    r"^(S|D|E|L[\w-]*:|R|J|U|T|Q|Sc|Cr|P|C|A|Rt|Lay|Fm|Tbl|Ev|"
    r"If|Err|Retry|Call|Set|Filt|Sort|X|Loop|While|CacheGet|CacheSet|QueuePut|Tx|Enf)(\b|\s|$)"
)


def _log(msg: str) -> None:
    ts = time.strftime("%H:%M:%S")
    print(f"[eval {ts}] {msg}", flush=True)


def _normalize_phi_rope_scaling(config):
    rope_scaling = getattr(config, "rope_scaling", None)
    if not isinstance(rope_scaling, dict):
        return config
    rope = dict(rope_scaling)
    if "type" not in rope and "rope_type" in rope:
        rope["type"] = rope["rope_type"]
    if str(rope.get("type", "")).lower() in {"default", "none", "null"}:
        config.rope_scaling = None
    else:
        config.rope_scaling = rope
    return config


def _normalize_piece(piece: str) -> str:
    p = (piece or "").replace("Ġ", " ").replace("▁", " ").strip()
    return p


def _has_min_ainl_structure(prefix: str) -> bool:
    """Guard EOS so decoding does not stop at trivial stubs."""
    lines = [ln.strip() for ln in (prefix or "").splitlines() if ln.strip()]
    if len(lines) < 2:
        return False
    ops = []
    for ln in lines:
        head = ln.split()[0] if ln.split() else ""
        if head.endswith(":"):
            rest = ln[len(head) :].strip()
            head = rest.split()[0] if rest.split() else ""
        ops.append(head)
    has_read = any(op == "R" for op in ops)
    has_terminal = any(op in {"J", "Err"} for op in ops)
    has_control = any(op in {"If", "Retry", "Loop", "While"} for op in ops)
    # Precision tune: allow EOS once we have at least minimal useful structure:
    # - R + (terminal/control), OR
    # - explicit terminal with >=3 lines.
    if has_read and (has_terminal or has_control):
        return True
    if len(lines) >= 3 and has_terminal:
        return True
    return False


def _build_constraint_resources(tokenizer) -> Optional[Dict[str, Any]]:
    vocab_size = int(getattr(tokenizer, "vocab_size", 0) or 0)
    if vocab_size <= 0:
        return None
    id_to_piece = {}
    id_to_text = {}
    for tid in range(vocab_size):
        raw = tokenizer.decode([tid], skip_special_tokens=False, clean_up_tokenization_spaces=False)
        id_to_piece[tid] = _normalize_piece(raw)
        id_to_text[tid] = (raw or "").replace("Ġ", " ").replace("▁", " ")
    eos_id = getattr(tokenizer, "eos_token_id", None)
    safe_fallback = {"S", "D", "E", "L", "R", "J", "If", "X", "Cr"}
    fallback_ids = sorted(
        {
            tid
            for tid, piece in id_to_piece.items()
            if piece in safe_fallback or id_to_text.get(tid, "") == "\n"
        }
    )
    return {
        "vocab_size": vocab_size,
        "id_to_piece": id_to_piece,
        "id_to_text": id_to_text,
        "eos_id": eos_id,
        "fallback_ids": fallback_ids,
    }


def _build_constraint_processor(tokenizer, prompt_len: int, constraint_resources: Optional[Dict[str, Any]] = None):
    from transformers import LogitsProcessor
    from grammar_constraint import next_valid_tokens, is_valid_ainl_prefix_strict

    res = constraint_resources or _build_constraint_resources(tokenizer)
    if not res:
        return None
    vocab_size = int(res["vocab_size"])
    id_to_piece = res["id_to_piece"]
    id_to_text = res["id_to_text"]
    eos_id = res["eos_id"]
    fallback_ids = res["fallback_ids"]

    def _can_finish(prefix: str) -> bool:
        return _has_min_ainl_structure(prefix) and is_valid_ainl_prefix_strict(prefix)

    diagnostics = {
        "steps_processed": 0,
        "tokens_considered": 0,
        "tokens_allowed": 0,
        "rejected_by_next_token": 0,
        "rejected_by_strict_prefix": 0,
        "eos_allowed": 0,
        "eos_blocked": 0,
        "fallback_used_steps": 0,
        "vocab_size": vocab_size,
        "fallback_size": len(fallback_ids),
    }

    class AINLConstraintProcessor(LogitsProcessor):
        def __call__(self, input_ids, scores):
            import torch

            for row in range(scores.shape[0]):
                diagnostics["steps_processed"] += 1
                gen_ids = input_ids[row, prompt_len:]
                prefix = tokenizer.decode(
                    gen_ids.tolist(),
                    skip_special_tokens=True,
                    clean_up_tokenization_spaces=False,
                )
                allowed_tokens = next_valid_tokens(prefix)
                allowed_ids = []
                for tid, piece in id_to_piece.items():
                    if not piece:
                        continue
                    diagnostics["tokens_considered"] += 1
                    token_allowed = (
                        piece in allowed_tokens
                        or any(a.startswith(piece) for a in allowed_tokens)
                        or (id_to_text.get(tid, "") == "\n" and "\n" in allowed_tokens)
                    )
                    if not token_allowed:
                        diagnostics["rejected_by_next_token"] += 1
                        continue
                    next_prefix = prefix + id_to_text.get(tid, "")
                    if not is_valid_ainl_prefix_strict(next_prefix):
                        diagnostics["rejected_by_strict_prefix"] += 1
                        continue
                    allowed_ids.append(tid)
                    diagnostics["tokens_allowed"] += 1
                if eos_id is not None and _can_finish(prefix):
                    allowed_ids.append(eos_id)
                    diagnostics["eos_allowed"] += 1
                elif eos_id is not None:
                    diagnostics["eos_blocked"] += 1
                if not allowed_ids and fallback_ids:
                    allowed_ids = list(fallback_ids)
                    diagnostics["fallback_used_steps"] += 1
                if allowed_ids:
                    mask = torch.full_like(scores[row], float("-inf"))
                    idx = torch.tensor(sorted(set(allowed_ids)), device=scores.device, dtype=torch.long)
                    mask[idx] = 0.0
                    scores[row] = scores[row] + mask
            return scores

    return AINLConstraintProcessor(), diagnostics


def _constraint_alerts(diag: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    if not diag:
        return {"alerts": [], "hints": [], "ratios": {}}
    steps = max(1, int(diag.get("steps_processed", 0)))
    considered = max(1, int(diag.get("tokens_considered", 0)))
    allowed = int(diag.get("tokens_allowed", 0))
    strict_reject = int(diag.get("rejected_by_strict_prefix", 0))
    fallback_steps = int(diag.get("fallback_used_steps", 0))
    eos_allowed = int(diag.get("eos_allowed", 0))
    eos_blocked = int(diag.get("eos_blocked", 0))

    fallback_rate = fallback_steps / steps
    allowed_rate = allowed / considered
    strict_reject_share = strict_reject / max(1, strict_reject + allowed)
    eos_block_rate = eos_blocked / steps

    alerts: List[str] = []
    hints: List[str] = []
    if fallback_rate > 0.25:
        alerts.append("high_fallback_rate")
        hints.append("Constraint may be too narrow; consider broadening next_valid_tokens for current prefix states.")
    if strict_reject_share > 0.60:
        alerts.append("high_strict_prefix_rejection")
        hints.append("Strict prefix guard rejects many grammar-allowed tokens; relax/adjust strict-prefix checks.")
    if allowed_rate < 0.0005:
        alerts.append("very_low_allowed_token_rate")
        hints.append("Very few tokens survive constraints; inspect token normalization and prefix-token matching.")
    if eos_allowed == 0 and eos_block_rate > 0.95:
        alerts.append("eos_never_allowed")
        hints.append("EOS gating is almost always blocked; reduce minimum structure threshold or improve prompt scaffolding.")

    return {
        "alerts": alerts,
        "hints": hints,
        "ratios": {
            "fallback_rate": fallback_rate,
            "allowed_token_rate": allowed_rate,
            "strict_reject_share": strict_reject_share,
            "eos_block_rate": eos_block_rate,
        },
    }


def _extract_ainl_lines(text: str, *, chunk_lines: int = 256, max_lines: int = 512) -> str:
    """
    Extract canonical AINL-like lines in bounded chunks to avoid heavy host-side
    processing on pathological long outputs.
    """
    raw_lines = (text or "").splitlines()
    out: List[str] = []
    step = max(16, int(chunk_lines))
    limit = max(32, int(max_lines))
    for i in range(0, len(raw_lines), step):
        chunk = raw_lines[i : i + step]
        for raw in chunk:
            line = raw.strip()
            if not line:
                continue
            if re.match(AINL_LINE_RE, line):
                out.append(line)
                if len(out) >= limit:
                    return "\n".join(out).strip()
    return "\n".join(out).strip()


def _load_prompts(path: Path) -> List[Dict[str, str]]:
    if not path.exists():
        raise SystemExit(f"Prompt set not found: {path}")
    rows: List[Dict[str, str]] = []
    with open(path, encoding="utf-8") as f:
        for i, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            prompt = str(row.get("prompt", "")).strip()
            pid = str(row.get("id", f"p{i}")).strip()
            if not prompt:
                continue
            rows.append({"id": pid, "prompt": prompt})
    if not rows:
        raise SystemExit(f"Prompt set is empty: {path}")
    return rows


def _load_generation_stack(
    base_model: str,
    adapter_path: Optional[Path],
    device: str,
    quantization_mode: str,
):
    import torch
    from peft import PeftModel
    from transformers import AutoConfig, AutoModelForCausalLM, AutoTokenizer
    from transformers.cache_utils import DynamicCache

    if not hasattr(DynamicCache, "seen_tokens"):
        DynamicCache.seen_tokens = property(lambda self: self.get_seq_length())
    if not hasattr(DynamicCache, "get_max_length"):
        DynamicCache.get_max_length = DynamicCache.get_max_cache_shape

    tokenizer = AutoTokenizer.from_pretrained(base_model, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    config = AutoConfig.from_pretrained(base_model, trust_remote_code=True)
    config = _normalize_phi_rope_scaling(config)

    model = AutoModelForCausalLM.from_pretrained(
        base_model,
        config=config,
        trust_remote_code=True,
        attn_implementation="eager",
        torch_dtype="auto",
    )
    if adapter_path is not None:
        model = PeftModel.from_pretrained(model, str(adapter_path))

    model.eval()
    model.config.use_cache = False

    if device == "mps":
        if not torch.backends.mps.is_available():
            raise SystemExit("MPS requested but not available in this runtime.")
        model = model.to("mps")
    else:
        model = model.to("cpu")

    quant_diag: Dict[str, Any] = {
        "requested_mode": quantization_mode,
        "applied_mode": "none",
        "enabled": False,
        "fallback_reason": None,
    }
    if quantization_mode == "dynamic-int8":
        if device != "cpu":
            quant_diag["fallback_reason"] = "dynamic_int8_supported_on_cpu_only"
        else:
            try:
                import torch.nn as nn

                model = torch.quantization.quantize_dynamic(model, {nn.Linear}, dtype=torch.qint8)
                quant_diag["applied_mode"] = "dynamic-int8"
                quant_diag["enabled"] = True
            except Exception as e:
                quant_diag["fallback_reason"] = f"quantize_dynamic_failed:{e}"

    return tokenizer, model, torch, quant_diag


def _generate(
    *,
    tokenizer,
    model,
    torch_mod,
    device: str,
    prompt: str,
    max_new_tokens: int,
    heartbeat_seconds: int,
    generation_timeout_seconds: int,
    constrained_decoding: bool,
    constraint_resources: Optional[Dict[str, Any]] = None,
    prepared_prompt_text: Optional[str] = None,
    background_hook: Optional[Callable[[], None]] = None,
) -> Dict[str, Any]:
    t_total0 = time.time()
    t_prepare0 = time.time()
    prompt_text = prepared_prompt_text
    if not prompt_text:
        messages = [{"role": "user", "content": f"{prompt}\nOutput only code."}]
        prompt_text = tokenizer.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True
        )
    inputs = tokenizer(prompt_text, return_tensors="pt")
    inputs = {k: v.to(device) for k, v in inputs.items()}
    t_prepare = time.time() - t_prepare0
    result: Dict[str, Any] = {"output_ids": None, "error": None}
    logits_processor = None
    constraint_diag = None
    t_constraint0 = time.time()
    if constrained_decoding:
        built = _build_constraint_processor(
            tokenizer, inputs["input_ids"].shape[-1], constraint_resources=constraint_resources
        )
        if built is not None:
            logits_processor, constraint_diag = built
    t_constraint = time.time() - t_constraint0

    def _worker() -> None:
        try:
            with torch_mod.no_grad():
                result["output_ids"] = model.generate(
                    **inputs,
                    max_new_tokens=max_new_tokens,
                    do_sample=False,
                    use_cache=False,
                    logits_processor=([logits_processor] if logits_processor is not None else None),
                )
        except Exception as e:
            result["error"] = e

    t = threading.Thread(target=_worker, daemon=True)
    t_generate0 = time.time()
    t.start()
    started = time.time()
    hook_ran = False
    while t.is_alive():
        elapsed = time.time() - started
        _log(f"generate() still running... {elapsed:.0f}s elapsed")
        if background_hook is not None and not hook_ran:
            try:
                background_hook()
            except Exception:
                pass
            hook_ran = True
        t.join(timeout=max(1, heartbeat_seconds))
        if generation_timeout_seconds > 0 and (time.time() - started) > generation_timeout_seconds:
            raise TimeoutError(
                f"Generation timed out after {generation_timeout_seconds}s "
                f"(max_new_tokens={max_new_tokens})."
            )
    if result["error"] is not None:
        raise result["error"]
    t_generate = time.time() - t_generate0
    output_ids = result["output_ids"]
    t_decode0 = time.time()
    generated_ids = output_ids[0][inputs["input_ids"].shape[-1] :]
    text = tokenizer.decode(generated_ids, skip_special_tokens=True).strip()
    t_decode = time.time() - t_decode0
    return {
        "text": text,
        "timing": {
            "prepare_seconds": t_prepare,
            "constraint_build_seconds": t_constraint,
            "generate_seconds": t_generate,
            "decode_seconds": t_decode,
            "total_seconds": time.time() - t_total0,
        },
        "constraint_diag": copy.deepcopy(constraint_diag) if constraint_diag is not None else None,
    }


def _compile_status_with_compilers(code: str, runtime_compiler, strict_compiler) -> Dict[str, Any]:
    runtime_errors: List[str] = []
    strict_errors: List[str] = []
    try:
        runtime_ir = runtime_compiler.compile(code, emit_graph=False)
        runtime_errors = list(runtime_ir.get("errors", []))
    except Exception as e:
        runtime_errors = [f"exception: {e}"]
    try:
        strict_ir = strict_compiler.compile(code, emit_graph=False)
        strict_errors = list(strict_ir.get("errors", []))
    except Exception as e:
        strict_errors = [f"exception: {e}"]
    return {
        "runtime_ok": not runtime_errors,
        "strict_ok": not strict_errors,
        "runtime_errors": runtime_errors,
        "strict_errors": strict_errors,
    }


def _compile_status(code: str) -> Dict[str, Any]:
    from compiler_v2 import AICodeCompiler

    runtime_compiler = AICodeCompiler(strict_mode=False)
    strict_compiler = AICodeCompiler(strict_mode=True)
    return _compile_status_with_compilers(code, runtime_compiler, strict_compiler)


def _ainl_shape_status(code: str) -> Dict[str, Any]:
    raw = (code or "").strip()
    if not raw:
        return {"ainl_like_ok": False, "ainl_like_reason": "empty_output"}
    if "```" in raw:
        return {"ainl_like_ok": False, "ainl_like_reason": "markdown_fence_detected"}
    lines = [ln.strip() for ln in raw.splitlines() if ln.strip()]
    if not lines:
        return {"ainl_like_ok": False, "ainl_like_reason": "empty_lines"}
    # Fast reject for common non-AINL code styles.
    if any(
        ln.startswith(prefix)
        for ln in lines[:5]
        for prefix in ("import ", "from ", "def ", "class ", "function ", "const ", "let ")
    ):
        return {"ainl_like_ok": False, "ainl_like_reason": "non_ainl_code_prefix"}
    match_count = sum(1 for ln in lines if re.match(AINL_LINE_RE, ln))
    ratio = match_count / len(lines)
    # Require at least one AINL line and >=35% AINL-op-style lines.
    if match_count < 1 or ratio < 0.35:
        return {
            "ainl_like_ok": False,
            "ainl_like_reason": f"low_ainl_line_ratio:{ratio:.2f}",
        }
    return {"ainl_like_ok": True, "ainl_like_reason": "ok"}


def _classify_failure(row: Dict[str, Any]) -> str:
    compile_info = (row or {}).get("compile", {})
    if compile_info.get("strict_ainl_ok"):
        return "ok"
    gen_error = str((row or {}).get("generation_error") or "").lower()
    if "timed out" in gen_error:
        return "generation_timeout"
    if "repair_failed" in gen_error:
        return "repair_generation_failure"
    if not (row or {}).get("nonempty"):
        return "empty_output"
    reason = str(compile_info.get("ainl_like_reason") or "").strip()
    if reason and reason != "ok":
        return f"shape:{reason}"
    if not compile_info.get("runtime_ok"):
        return "runtime_compile_failure"
    if not compile_info.get("strict_ok"):
        return "strict_compile_failure"
    return "unknown_failure"


def _failure_family_counts(records: List[Dict[str, Any]], key_prefix: str) -> Dict[str, int]:
    out: Dict[str, int] = {}
    for r in records:
        fam = _classify_failure(r.get(key_prefix, {}))
        out[fam] = out.get(fam, 0) + 1
    return dict(sorted(out.items(), key=lambda kv: (-kv[1], kv[0])))


def _length_bucket(n_tokens: int) -> str:
    n = int(max(0, n_tokens))
    if n <= 64:
        return "tok_000_064"
    if n <= 128:
        return "tok_065_128"
    if n <= 256:
        return "tok_129_256"
    if n <= 384:
        return "tok_257_384"
    if n <= 512:
        return "tok_385_512"
    return "tok_513_plus"


def _run_model_eval(
    *,
    model_name: str,
    base_model: str,
    adapter_path: Optional[Path],
    prompts: List[Dict[str, str]],
    max_new_tokens: int,
    device: str,
    heartbeat_seconds: int,
    generation_timeout_seconds: int,
    constrained_decoding: bool,
    repair_attempts: int,
    canonicalize_output: bool,
    emit_timing: bool,
    constraint_diagnostics: bool,
    bucket_by_prompt_length: bool,
    canonicalize_chunk_lines: int,
    canonicalize_max_lines: int,
    quantization_mode: str,
) -> Dict[str, Dict[str, Any]]:
    from compiler_v2 import AICodeCompiler

    _log(f"Loading {model_name} model...")
    model_t0 = time.time()
    tokenizer, model, torch_mod, quant_diag = _load_generation_stack(
        base_model,
        adapter_path,
        device,
        quantization_mode,
    )
    model_load_seconds = time.time() - model_t0
    constraint_resources = _build_constraint_resources(tokenizer) if constrained_decoding else None
    runtime_compiler = AICodeCompiler(strict_mode=False)
    strict_compiler = AICodeCompiler(strict_mode=True)
    _log(f"{model_name} model loaded. Starting prompt loop ({len(prompts)} prompts).")
    prompt_template_cache: Dict[str, str] = {}

    def _prepare_prompt_text_for(prompt_text: str) -> str:
        if prompt_text in prompt_template_cache:
            return prompt_template_cache[prompt_text]
        messages = [{"role": "user", "content": f"{prompt_text}\nOutput only code."}]
        rendered = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        prompt_template_cache[prompt_text] = rendered
        return rendered
    eval_items: List[Dict[str, Any]] = []
    for item in prompts:
        prepared = _prepare_prompt_text_for(item["prompt"])
        tokenized = tokenizer(prepared, add_special_tokens=False)
        tok_len = len(tokenized.get("input_ids", []))
        eval_items.append(
            {
                "id": item["id"],
                "prompt": item["prompt"],
                "prepared_prompt": prepared,
                "prompt_token_length": tok_len,
                "prompt_bucket": _length_bucket(tok_len),
            }
        )
    if bucket_by_prompt_length:
        eval_items.sort(key=lambda x: (int(x["prompt_token_length"]), x["id"]))
    ordered_prompt_ids = [str(x["id"]) for x in eval_items]
    model_diag: Dict[str, Any] = {
        "model_name": model_name,
        "model_load_seconds": model_load_seconds,
        "prompt_count": len(prompts),
        "prompt_ordering": {
            "bucket_by_prompt_length": bool(bucket_by_prompt_length),
            "ordered_prompt_ids": ordered_prompt_ids,
        },
        "canonicalize_config": {
            "chunk_lines": int(canonicalize_chunk_lines),
            "max_lines": int(canonicalize_max_lines),
        },
        "quantization": quant_diag,
        "timing_totals": {
            "generate_seconds": 0.0,
            "compile_seconds": 0.0,
            "repair_generate_seconds": 0.0,
            "canonicalize_seconds": 0.0,
            "prompt_total_seconds": 0.0,
        },
    }
    if constraint_diagnostics:
        model_diag["constraint_diagnostics"] = {
            "steps_processed": 0,
            "tokens_considered": 0,
            "tokens_allowed": 0,
            "rejected_by_next_token": 0,
            "rejected_by_strict_prefix": 0,
            "eos_allowed": 0,
            "eos_blocked": 0,
            "fallback_used_steps": 0,
        }
    model_diag["length_buckets"] = {}
    outputs: Dict[str, Dict[str, Any]] = {}
    for i, item in enumerate(eval_items, start=1):
        p0 = time.time()
        pid = item["id"]
        prompt = item["prompt"]
        prompt_bucket = str(item.get("prompt_bucket") or "tok_unknown")
        prompt_token_length = int(item.get("prompt_token_length") or 0)
        _log(
            f"[{model_name} {i}/{len(eval_items)}] {pid} - generating "
            f"(bucket={prompt_bucket}, prompt_tokens={prompt_token_length})"
        )
        generation_error = None
        text = ""
        prompt_diag: Dict[str, Any] = {
            "timing": {
                "generate_seconds": 0.0,
                "compile_seconds": 0.0,
                "repair_generate_seconds": 0.0,
                "canonicalize_seconds": 0.0,
                "prompt_total_seconds": 0.0,
            },
            "repair_attempts_used": 0,
            "prompt_token_length": prompt_token_length,
            "prompt_bucket": prompt_bucket,
        }
        if constraint_diagnostics:
            prompt_diag["constraint_diagnostics"] = []
        bucket_diag = model_diag["length_buckets"].setdefault(
            prompt_bucket,
            {
                "total_prompts": 0,
                "nonempty_outputs": 0,
                "runtime_compile_ok": 0,
                "strict_compile_ok": 0,
                "strict_ainl_ok": 0,
                "timing_totals": {
                    "generate_seconds": 0.0,
                    "compile_seconds": 0.0,
                    "repair_generate_seconds": 0.0,
                    "canonicalize_seconds": 0.0,
                    "prompt_total_seconds": 0.0,
                },
                "failure_families": {},
                "constraint_diagnostics": {
                    "steps_processed": 0,
                    "tokens_considered": 0,
                    "tokens_allowed": 0,
                    "rejected_by_next_token": 0,
                    "rejected_by_strict_prefix": 0,
                    "eos_allowed": 0,
                    "eos_blocked": 0,
                    "fallback_used_steps": 0,
                },
            },
        )
        try:
            t0 = time.time()
            prepared_current = item.get("prepared_prompt") or _prepare_prompt_text_for(prompt)

            def _background_prep() -> None:
                if i < len(eval_items):
                    _ = eval_items[i].get("prepared_prompt")

            gen = _generate(
                tokenizer=tokenizer,
                model=model,
                torch_mod=torch_mod,
                device=device,
                prompt=prompt,
                max_new_tokens=max_new_tokens,
                heartbeat_seconds=heartbeat_seconds,
                generation_timeout_seconds=generation_timeout_seconds,
                constrained_decoding=constrained_decoding,
                constraint_resources=constraint_resources,
                prepared_prompt_text=prepared_current,
                background_hook=_background_prep,
            )
            dt = time.time() - t0
            text = gen["text"]
            prompt_diag["timing"]["generate_seconds"] += float(gen["timing"]["total_seconds"])
            _log(f"[{model_name} {i}/{len(eval_items)}] {pid} - generated in {dt:.1f}s")
            if canonicalize_output:
                tc = time.time()
                text = _extract_ainl_lines(
                    text,
                    chunk_lines=canonicalize_chunk_lines,
                    max_lines=canonicalize_max_lines,
                )
                prompt_diag["timing"]["canonicalize_seconds"] += time.time() - tc
            if constraint_diagnostics and gen.get("constraint_diag"):
                prompt_diag["constraint_diagnostics"].append(gen["constraint_diag"])
        except Exception as e:
            prompt_diag["timing"]["generate_seconds"] += time.time() - t0
            generation_error = str(e)
            _log(f"[{model_name} {i}/{len(eval_items)}] {pid} - generation failed: {generation_error}")

        compile_seconds_accum = 0.0
        tc = time.time()
        compile_status = _compile_status_with_compilers(text, runtime_compiler, strict_compiler) if text.strip() else {
            "runtime_ok": False,
            "strict_ok": False,
            "runtime_errors": [f"no_output: {generation_error or 'empty output'}"],
            "strict_errors": [f"no_output: {generation_error or 'empty output'}"],
        }
        compile_seconds_accum += time.time() - tc
        # Repair loop: ask model to rewrite into strict canonical AINL using compiler feedback.
        for r_idx in range(repair_attempts):
            if compile_status["runtime_ok"] and compile_status["strict_ok"]:
                break
            err_lines = (compile_status.get("strict_errors") or compile_status.get("runtime_errors") or [])[:2]
            repair_prompt = (
                "Rewrite the program into strict canonical AINL only.\n"
                "Rules: output only AINL lines (S/D/E/L:/R/If/X/J...), no markdown, no YAML, no prose.\n"
                f"Original task: {prompt}\n"
                f"Compiler errors: {' | '.join(err_lines)}\n"
                f"Broken program:\n{text}\n"
            )
            _log(f"[{model_name} {i}/{len(eval_items)}] {pid} - repair attempt {r_idx + 1}/{repair_attempts}")
            try:
                t_repair = time.time()
                prepared_repair = _prepare_prompt_text_for(repair_prompt)
                gen = _generate(
                    tokenizer=tokenizer,
                    model=model,
                    torch_mod=torch_mod,
                    device=device,
                    prompt=repair_prompt,
                    max_new_tokens=max_new_tokens,
                    heartbeat_seconds=heartbeat_seconds,
                    generation_timeout_seconds=generation_timeout_seconds,
                    constrained_decoding=constrained_decoding,
                    constraint_resources=constraint_resources,
                    prepared_prompt_text=prepared_repair,
                )
                text = gen["text"]
                prompt_diag["timing"]["repair_generate_seconds"] += float(gen["timing"]["total_seconds"])
                prompt_diag["repair_attempts_used"] += 1
                if canonicalize_output:
                    tc = time.time()
                    text = _extract_ainl_lines(
                        text,
                        chunk_lines=canonicalize_chunk_lines,
                        max_lines=canonicalize_max_lines,
                    )
                    prompt_diag["timing"]["canonicalize_seconds"] += time.time() - tc
                if constraint_diagnostics and gen.get("constraint_diag"):
                    prompt_diag["constraint_diagnostics"].append(gen["constraint_diag"])
            except Exception as e:
                prompt_diag["timing"]["repair_generate_seconds"] += time.time() - t_repair
                generation_error = f"repair_failed: {e}"
                break
            tc = time.time()
            compile_status = _compile_status_with_compilers(text, runtime_compiler, strict_compiler) if text.strip() else {
                "runtime_ok": False,
                "strict_ok": False,
                "runtime_errors": [f"no_output: {generation_error or 'empty output'}"],
                "strict_errors": [f"no_output: {generation_error or 'empty output'}"],
            }
            compile_seconds_accum += time.time() - tc
        prompt_diag["timing"]["compile_seconds"] = compile_seconds_accum
        ainl_status = _ainl_shape_status(text)
        compile_status["ainl_like_ok"] = ainl_status["ainl_like_ok"]
        compile_status["ainl_like_reason"] = ainl_status["ainl_like_reason"]
        compile_status["strict_ainl_ok"] = bool(
            compile_status["runtime_ok"] and compile_status["strict_ok"] and compile_status["ainl_like_ok"]
        )
        cdt = compile_seconds_accum
        _log(
            f"[{model_name} {i}/{len(eval_items)}] {pid} - compile runtime_ok="
            f"{compile_status['runtime_ok']} strict_ok={compile_status['strict_ok']} "
            f"ainl_like={compile_status['ainl_like_ok']} ({cdt:.2f}s)"
        )
        row_for_failure = {
            "nonempty": bool(text.strip()),
            "generation_error": generation_error,
            "compile": compile_status,
        }
        bucket_diag["total_prompts"] += 1
        bucket_diag["nonempty_outputs"] += 1 if row_for_failure["nonempty"] else 0
        bucket_diag["runtime_compile_ok"] += 1 if compile_status.get("runtime_ok") else 0
        bucket_diag["strict_compile_ok"] += 1 if compile_status.get("strict_ok") else 0
        bucket_diag["strict_ainl_ok"] += 1 if compile_status.get("strict_ainl_ok") else 0
        fam = _classify_failure(row_for_failure)
        ff = bucket_diag["failure_families"]
        ff[fam] = int(ff.get(fam, 0)) + 1
        outputs[pid] = {
            "nonempty": row_for_failure["nonempty"],
            "output": text,
            "generation_error": generation_error,
            "compile": compile_status,
            "prompt_token_length": prompt_token_length,
            "prompt_bucket": prompt_bucket,
        }
        prompt_diag["timing"]["prompt_total_seconds"] = time.time() - p0
        for tk in ("generate_seconds", "compile_seconds", "repair_generate_seconds", "canonicalize_seconds", "prompt_total_seconds"):
            bucket_diag["timing_totals"][tk] += float(prompt_diag["timing"].get(tk, 0.0))
        model_diag["timing_totals"]["generate_seconds"] += prompt_diag["timing"]["generate_seconds"]
        model_diag["timing_totals"]["repair_generate_seconds"] += prompt_diag["timing"]["repair_generate_seconds"]
        model_diag["timing_totals"]["canonicalize_seconds"] += prompt_diag["timing"]["canonicalize_seconds"]
        model_diag["timing_totals"]["compile_seconds"] += prompt_diag["timing"]["compile_seconds"]
        model_diag["timing_totals"]["prompt_total_seconds"] += prompt_diag["timing"]["prompt_total_seconds"]
        if emit_timing:
            outputs[pid]["diagnostics"] = {"timing": prompt_diag["timing"], "repair_attempts_used": prompt_diag["repair_attempts_used"]}
        if constraint_diagnostics:
            entries = prompt_diag.get("constraint_diagnostics") or []
            per_prompt_agg = {
                "steps_processed": 0,
                "tokens_considered": 0,
                "tokens_allowed": 0,
                "rejected_by_next_token": 0,
                "rejected_by_strict_prefix": 0,
                "eos_allowed": 0,
                "eos_blocked": 0,
                "fallback_used_steps": 0,
                "vocab_size": None,
                "fallback_size": None,
                "attempts_recorded": len(entries),
            }
            for d in entries:
                for k in (
                    "steps_processed",
                    "tokens_considered",
                    "tokens_allowed",
                    "rejected_by_next_token",
                    "rejected_by_strict_prefix",
                    "eos_allowed",
                    "eos_blocked",
                    "fallback_used_steps",
                ):
                    per_prompt_agg[k] += int(d.get(k, 0))
                if per_prompt_agg["vocab_size"] is None and d.get("vocab_size") is not None:
                    per_prompt_agg["vocab_size"] = d.get("vocab_size")
                if per_prompt_agg["fallback_size"] is None and d.get("fallback_size") is not None:
                    per_prompt_agg["fallback_size"] = d.get("fallback_size")
            if "diagnostics" not in outputs[pid]:
                outputs[pid]["diagnostics"] = {}
            outputs[pid]["diagnostics"]["constraint"] = per_prompt_agg
            for k in (
                "steps_processed",
                "tokens_considered",
                "tokens_allowed",
                "rejected_by_next_token",
                "rejected_by_strict_prefix",
                "eos_allowed",
                "eos_blocked",
                "fallback_used_steps",
            ):
                model_diag["constraint_diagnostics"][k] += int(per_prompt_agg.get(k, 0))
                bucket_diag["constraint_diagnostics"][k] += int(per_prompt_agg.get(k, 0))
    del model
    del tokenizer
    gc.collect()
    if device == "mps":
        try:
            import torch

            torch.mps.empty_cache()
        except Exception:
            pass
    model_diag["timing_totals"]["loop_wall_seconds"] = model_diag["timing_totals"]["prompt_total_seconds"]
    model_diag["cleanup_seconds"] = max(0.0, time.time() - model_t0 - model_load_seconds - model_diag["timing_totals"]["loop_wall_seconds"])
    model_diag["prompt_template_cache_entries"] = len(prompt_template_cache)
    for bname, bdiag in model_diag["length_buckets"].items():
        bt = max(1, int(bdiag.get("total_prompts", 0)))
        bdiag["nonempty_rate"] = float(bdiag.get("nonempty_outputs", 0)) / bt
        bdiag["runtime_compile_rate"] = float(bdiag.get("runtime_compile_ok", 0)) / bt
        bdiag["strict_compile_rate"] = float(bdiag.get("strict_compile_ok", 0)) / bt
        bdiag["strict_ainl_rate"] = float(bdiag.get("strict_ainl_ok", 0)) / bt
        bdiag["failure_families"] = dict(sorted((bdiag.get("failure_families") or {}).items(), key=lambda kv: (-kv[1], kv[0])))
    if constraint_diagnostics:
        model_diag["constraint_health"] = _constraint_alerts(model_diag.get("constraint_diagnostics"))
        for bname, bdiag in model_diag["length_buckets"].items():
            bdiag["constraint_health"] = _constraint_alerts(bdiag.get("constraint_diagnostics"))
    return outputs, model_diag


def _aggregate(records: List[Dict[str, Any]], key_prefix: str) -> Dict[str, Any]:
    total = len(records)
    nonempty = sum(1 for r in records if r[key_prefix]["nonempty"])
    runtime_ok = sum(1 for r in records if r[key_prefix]["compile"]["runtime_ok"])
    strict_ok = sum(1 for r in records if r[key_prefix]["compile"]["strict_ok"])
    ainl_like_ok = sum(1 for r in records if r[key_prefix]["compile"].get("ainl_like_ok"))
    strict_ainl_ok = sum(1 for r in records if r[key_prefix]["compile"].get("strict_ainl_ok"))
    return {
        "total_prompts": total,
        "nonempty_outputs": nonempty,
        "nonempty_rate": (nonempty / total) if total else 0.0,
        "runtime_compile_ok": runtime_ok,
        "runtime_compile_rate": (runtime_ok / total) if total else 0.0,
        "strict_compile_ok": strict_ok,
        "strict_compile_rate": (strict_ok / total) if total else 0.0,
        "ainl_like_ok": ainl_like_ok,
        "ainl_like_rate": (ainl_like_ok / total) if total else 0.0,
        "strict_ainl_ok": strict_ainl_ok,
        "strict_ainl_rate": (strict_ainl_ok / total) if total else 0.0,
    }


def main():
    parser = argparse.ArgumentParser(description="Evaluate AINL fine-tuned LoRA model.")
    parser.add_argument("--adapter-path", type=Path, default=DEFAULT_ADAPTER)
    parser.add_argument("--base-model", default=DEFAULT_BASE_MODEL)
    parser.add_argument("--prompt-set", type=Path, default=DEFAULT_PROMPTS)
    parser.add_argument("--output-json", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--max-new-tokens", type=int, default=180)
    parser.add_argument(
        "--heartbeat-seconds",
        type=int,
        default=10,
        help="Print a progress heartbeat during long generation every N seconds.",
    )
    parser.add_argument(
        "--generation-timeout-seconds",
        type=int,
        default=0,
        help="If >0, fail a prompt if generation exceeds this many seconds.",
    )
    parser.add_argument(
        "--constrained-decoding",
        action="store_true",
        help="Enable grammar-constrained next-token filtering during generation.",
    )
    parser.add_argument(
        "--repair-attempts",
        type=int,
        default=0,
        help="Number of compile-repair rewrite attempts after initial generation.",
    )
    parser.add_argument(
        "--canonicalize-output",
        action="store_true",
        help="Extract only canonical AINL-like lines from generated text before compile checks.",
    )
    parser.add_argument("--device", choices=["cpu", "mps"], default="cpu")
    parser.add_argument(
        "--limit",
        type=int,
        default=0,
        help="If >0, only evaluate first N prompts.",
    )
    parser.add_argument(
        "--skip-base-eval",
        action="store_true",
        help="Skip base model generation pass (useful for checkpoint sweeps).",
    )
    parser.add_argument(
        "--emit-timing",
        action="store_true",
        help="Include per-prompt and model-level timing diagnostics in output JSON.",
    )
    parser.add_argument(
        "--constraint-diagnostics",
        action="store_true",
        help="Include constraint rejection diagnostics in output JSON.",
    )
    parser.add_argument(
        "--bucket-by-prompt-length",
        action="store_true",
        help="Sort prompt execution by rendered prompt-token length for more stable decode shapes.",
    )
    parser.add_argument(
        "--canonicalize-chunk-lines",
        type=int,
        default=256,
        help="Chunk size (lines) for host-side canonicalization passes.",
    )
    parser.add_argument(
        "--canonicalize-max-lines",
        type=int,
        default=512,
        help="Max canonicalized lines kept from model output.",
    )
    parser.add_argument(
        "--quantization-mode",
        choices=["none", "dynamic-int8"],
        default="none",
        help="Optional inference quantization mode for eval pass.",
    )
    args = parser.parse_args()

    if not args.adapter_path.exists():
        raise SystemExit(f"Adapter path does not exist: {args.adapter_path}")

    prompts = _load_prompts(args.prompt_set)
    if args.limit and args.limit > 0:
        prompts = prompts[: args.limit]

    _log(f"Loaded {len(prompts)} prompts from {args.prompt_set}")
    _log(
        f"Config: device={args.device} max_new_tokens={args.max_new_tokens} "
        f"base_model={args.base_model} heartbeat={args.heartbeat_seconds}s "
        f"timeout={args.generation_timeout_seconds or 'off'} "
        f"constrained={args.constrained_decoding} repair={args.repair_attempts} "
        f"canonicalize={args.canonicalize_output} bucket_by_len={args.bucket_by_prompt_length} "
        f"quant={args.quantization_mode}"
    )
    lora_outputs, lora_diag = _run_model_eval(
        model_name="LoRA",
        base_model=args.base_model,
        adapter_path=args.adapter_path,
        prompts=prompts,
        max_new_tokens=args.max_new_tokens,
        device=args.device,
        heartbeat_seconds=args.heartbeat_seconds,
        generation_timeout_seconds=args.generation_timeout_seconds,
        constrained_decoding=args.constrained_decoding,
        repair_attempts=args.repair_attempts,
        canonicalize_output=args.canonicalize_output,
        emit_timing=args.emit_timing,
        constraint_diagnostics=args.constraint_diagnostics,
        bucket_by_prompt_length=args.bucket_by_prompt_length,
        canonicalize_chunk_lines=args.canonicalize_chunk_lines,
        canonicalize_max_lines=args.canonicalize_max_lines,
        quantization_mode=args.quantization_mode,
    )
    base_outputs: Dict[str, Dict[str, Any]] = {}
    base_diag: Optional[Dict[str, Any]] = None
    if args.skip_base_eval:
        for item in prompts:
            base_outputs[item["id"]] = {
                "nonempty": False,
                "output": "",
                "generation_error": "skipped",
                "compile": {
                    "runtime_ok": False,
                    "strict_ok": False,
                    "runtime_errors": ["skipped"],
                    "strict_errors": ["skipped"],
                    "ainl_like_ok": False,
                    "ainl_like_reason": "skipped",
                    "strict_ainl_ok": False,
                },
            }
    else:
        base_outputs, base_diag = _run_model_eval(
            model_name="Base",
            base_model=args.base_model,
            adapter_path=None,
            prompts=prompts,
            max_new_tokens=args.max_new_tokens,
            device=args.device,
            heartbeat_seconds=args.heartbeat_seconds,
            generation_timeout_seconds=args.generation_timeout_seconds,
            constrained_decoding=args.constrained_decoding,
            repair_attempts=args.repair_attempts,
            canonicalize_output=args.canonicalize_output,
            emit_timing=args.emit_timing,
            constraint_diagnostics=args.constraint_diagnostics,
            bucket_by_prompt_length=args.bucket_by_prompt_length,
            canonicalize_chunk_lines=args.canonicalize_chunk_lines,
            canonicalize_max_lines=args.canonicalize_max_lines,
            quantization_mode=args.quantization_mode,
        )

    records: List[Dict[str, Any]] = []
    for item in prompts:
        pid = item["id"]
        prompt = item["prompt"]
        records.append(
            {
                "id": pid,
                "prompt": prompt,
                "lora": lora_outputs[pid],
                "base": base_outputs[pid],
            }
        )

    lora_summary = _aggregate(records, "lora")
    base_summary = _aggregate(records, "base") if not args.skip_base_eval else None
    lora_failure_families = _failure_family_counts(records, "lora")
    base_failure_families = _failure_family_counts(records, "base") if not args.skip_base_eval else None
    if not args.skip_base_eval:
        lora_wins_runtime = sum(
            1
            for r in records
            if r["lora"]["compile"]["runtime_ok"] and not r["base"]["compile"]["runtime_ok"]
        )
        base_wins_runtime = sum(
            1
            for r in records
            if r["base"]["compile"]["runtime_ok"] and not r["lora"]["compile"]["runtime_ok"]
        )
        ties_runtime = len(records) - lora_wins_runtime - base_wins_runtime
        lora_wins_strict_ainl = sum(
            1
            for r in records
            if r["lora"]["compile"].get("strict_ainl_ok") and not r["base"]["compile"].get("strict_ainl_ok")
        )
        base_wins_strict_ainl = sum(
            1
            for r in records
            if r["base"]["compile"].get("strict_ainl_ok") and not r["lora"]["compile"].get("strict_ainl_ok")
        )
        ties_strict_ainl = len(records) - lora_wins_strict_ainl - base_wins_strict_ainl
    else:
        lora_wins_runtime = None
        base_wins_runtime = None
        ties_runtime = None
        lora_wins_strict_ainl = None
        base_wins_strict_ainl = None
        ties_strict_ainl = None

    # Step 1 sanity check signal
    sanity = {
        "pass": bool(records and records[0]["lora"]["nonempty"]),
        "first_prompt_id": records[0]["id"] if records else None,
        "first_prompt_runtime_ok": records[0]["lora"]["compile"]["runtime_ok"] if records else False,
        "first_prompt_strict_ok": records[0]["lora"]["compile"]["strict_ok"] if records else False,
    }

    report = {
        "base_model": args.base_model,
        "adapter_path": str(args.adapter_path),
        "prompt_set": str(args.prompt_set),
        "max_new_tokens": args.max_new_tokens,
        "device": args.device,
        "constrained_decoding": bool(args.constrained_decoding),
        "repair_attempts": int(args.repair_attempts),
        "canonicalize_output": bool(args.canonicalize_output),
        "base_evaluated": not bool(args.skip_base_eval),
        "emit_timing": bool(args.emit_timing),
        "constraint_diagnostics": bool(args.constraint_diagnostics),
        "bucket_by_prompt_length": bool(args.bucket_by_prompt_length),
        "canonicalize_chunk_lines": int(args.canonicalize_chunk_lines),
        "canonicalize_max_lines": int(args.canonicalize_max_lines),
        "quantization_mode": str(args.quantization_mode),
        "sanity": sanity,
        "summary": {
            "lora": lora_summary,
            "base": base_summary,
            "failure_families": {
                "lora": lora_failure_families,
                "base": base_failure_families,
            },
            "comparison": {
                "lora_wins_runtime_compile": lora_wins_runtime,
                "base_wins_runtime_compile": base_wins_runtime,
                "ties_runtime_compile": ties_runtime,
                "lora_wins_strict_ainl": lora_wins_strict_ainl,
                "base_wins_strict_ainl": base_wins_strict_ainl,
                "ties_strict_ainl": ties_strict_ainl,
            },
        },
        "diagnostics": {
            "lora": lora_diag,
            "base": base_diag,
        },
        "results": records,
    }

    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    with open(args.output_json, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    _log("Evaluation complete.")
    _log(f"Sanity pass: {sanity['pass']}")
    _log(
        "LoRA runtime compile: "
        f"{lora_summary['runtime_compile_ok']}/{lora_summary['total_prompts']} "
        f"({lora_summary['runtime_compile_rate']:.1%})"
    )
    _log(f"LoRA failure families: {lora_failure_families}")
    if args.constraint_diagnostics and isinstance(lora_diag, dict):
        health = (lora_diag.get("constraint_health") or {})
        if health.get("alerts"):
            _log(f"LoRA constraint alerts: {health.get('alerts')}")
            _log(f"LoRA constraint hints: {health.get('hints')}")
    if base_summary is not None:
        _log(
            "Base runtime compile: "
            f"{base_summary['runtime_compile_ok']}/{base_summary['total_prompts']} "
            f"({base_summary['runtime_compile_rate']:.1%})"
        )
        _log(
            "Runtime wins (LoRA/Base/Tie): "
            f"{lora_wins_runtime}/{base_wins_runtime}/{ties_runtime}"
        )
        _log(
            "Strict AINL wins (LoRA/Base/Tie): "
            f"{lora_wins_strict_ainl}/{base_wins_strict_ainl}/{ties_strict_ainl}"
        )
        _log(f"Base failure families: {base_failure_families}")
        if args.constraint_diagnostics and isinstance(base_diag, dict):
            health = (base_diag.get("constraint_health") or {})
            if health.get("alerts"):
                _log(f"Base constraint alerts: {health.get('alerts')}")
                _log(f"Base constraint hints: {health.get('hints')}")
    _log(f"Report written to: {args.output_json}")


if __name__ == "__main__":
    main()
