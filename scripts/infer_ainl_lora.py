#!/usr/bin/env python3
"""
Run inference with a trained AINL LoRA adapter.

This script uses a conservative load path to avoid known runtime issues on
small/mac machines:
- Normalizes Phi-3 rope_scaling config variants
- Uses eager attention implementation
- Loads base model without offload/meta sharding by default (CPU)
"""

import argparse
import re
import sys
from pathlib import Path
from typing import List


BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE))
DEFAULT_ADAPTER = BASE / "models" / "ainl-phi3-lora"
DEFAULT_BASE_MODEL = "microsoft/phi-3-mini-4k-instruct"
DEFAULT_PROMPT = (
    "Generate a tiny valid AINL workflow that checks weather in Seattle and "
    "emails a short summary to ops@example.com. Output only code."
)


def _normalize_phi_rope_scaling(config):
    """Normalize rope_scaling fields for remote phi3 config variants."""
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
    if has_read and (has_terminal or has_control):
        return True
    if len(lines) >= 3 and has_terminal:
        return True
    return False


def _build_constraint_resources(tokenizer):
    vocab_size = int(getattr(tokenizer, "vocab_size", 0) or 0)
    if vocab_size <= 0:
        return None
    id_to_piece = {}
    id_to_text = {}
    for tid in range(vocab_size):
        raw = tokenizer.decode([tid], skip_special_tokens=False, clean_up_tokenization_spaces=False)
        id_to_piece[tid] = (raw or "").replace("Ġ", " ").replace("▁", " ").strip()
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
        "id_to_piece": id_to_piece,
        "id_to_text": id_to_text,
        "eos_id": eos_id,
        "fallback_ids": fallback_ids,
    }


def main():
    parser = argparse.ArgumentParser(description="Run LoRA inference sanity check.")
    parser.add_argument(
        "--adapter-path",
        type=Path,
        default=DEFAULT_ADAPTER,
        help="Path to trained LoRA adapter directory.",
    )
    parser.add_argument(
        "--base-model",
        default=DEFAULT_BASE_MODEL,
        help="Hugging Face base model id used for training.",
    )
    parser.add_argument(
        "--prompt",
        default=DEFAULT_PROMPT,
        help="User prompt for generation.",
    )
    parser.add_argument(
        "--max-new-tokens",
        type=int,
        default=120,
        help="Maximum number of generated tokens.",
    )
    parser.add_argument(
        "--device",
        choices=["cpu", "mps"],
        default="cpu",
        help="Execution device. Use cpu for stability; mps may be faster.",
    )
    parser.add_argument(
        "--constrained-decoding",
        action="store_true",
        help="Enable grammar-constrained next-token filtering for AINL generation.",
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
        help="Extract only canonical AINL-like lines before printing.",
    )
    parser.add_argument(
        "--canonicalize-chunk-lines",
        type=int,
        default=256,
        help="Chunk size (lines) for host-side canonicalization.",
    )
    parser.add_argument(
        "--canonicalize-max-lines",
        type=int,
        default=512,
        help="Maximum canonical lines retained from model output.",
    )
    parser.add_argument(
        "--quantization-mode",
        choices=["none", "dynamic-int8"],
        default="none",
        help="Optional inference quantization mode.",
    )
    args = parser.parse_args()

    if not args.adapter_path.exists():
        raise SystemExit(f"Adapter path does not exist: {args.adapter_path}")

    from peft import PeftModel
    from transformers import AutoConfig, AutoModelForCausalLM, AutoTokenizer, LogitsProcessor
    from transformers.cache_utils import DynamicCache
    import torch
    from grammar_constraint import next_valid_tokens, is_valid_ainl_prefix_strict
    from compiler_v2 import AICodeCompiler

    # Phi-3 remote code may expect DynamicCache.seen_tokens on some
    # transformers/remote-code combinations.
    if not hasattr(DynamicCache, "seen_tokens"):
        DynamicCache.seen_tokens = property(lambda self: self.get_seq_length())
    if not hasattr(DynamicCache, "get_max_length"):
        DynamicCache.get_max_length = DynamicCache.get_max_cache_shape

    tokenizer = AutoTokenizer.from_pretrained(args.base_model, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    config = AutoConfig.from_pretrained(args.base_model, trust_remote_code=True)
    config = _normalize_phi_rope_scaling(config)

    # Keep model loading simple and explicit; this avoids meta-device/offload
    # pathways that were causing adapter attachment failures.
    model = AutoModelForCausalLM.from_pretrained(
        args.base_model,
        config=config,
        trust_remote_code=True,
        attn_implementation="eager",
        torch_dtype="auto",
    )
    model = PeftModel.from_pretrained(model, str(args.adapter_path))
    model.eval()
    model.config.use_cache = False

    if args.device == "mps":
        if not torch.backends.mps.is_available():
            raise SystemExit("MPS is not available on this machine/runtime.")
        model = model.to("mps")
        device = "mps"
    else:
        model = model.to("cpu")
        device = "cpu"

    if args.quantization_mode == "dynamic-int8":
        if device == "cpu":
            try:
                import torch.nn as nn

                model = torch.quantization.quantize_dynamic(model, {nn.Linear}, dtype=torch.qint8)
            except Exception:
                pass

    messages = [{"role": "user", "content": args.prompt}]
    prompt_text = tokenizer.apply_chat_template(
        messages, tokenize=False, add_generation_prompt=True
    )
    inputs = tokenizer(prompt_text, return_tensors="pt")
    inputs = {k: v.to(device) for k, v in inputs.items()}

    logits_processor = None
    constraint_resources = _build_constraint_resources(tokenizer) if args.constrained_decoding else None
    if args.constrained_decoding and constraint_resources:
        id_to_piece = constraint_resources["id_to_piece"]
        id_to_text = constraint_resources["id_to_text"]
        eos_id = constraint_resources["eos_id"]
        prompt_len = inputs["input_ids"].shape[-1]
        fallback_ids = constraint_resources["fallback_ids"]

        def _can_finish(prefix: str) -> bool:
            return _has_min_ainl_structure(prefix) and is_valid_ainl_prefix_strict(prefix)

        class AINLConstraintProcessor(LogitsProcessor):
            def __call__(self, input_ids, scores):
                for row in range(scores.shape[0]):
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
                        token_allowed = (
                            piece in allowed_tokens
                            or any(a.startswith(piece) for a in allowed_tokens)
                            or (id_to_text.get(tid, "") == "\n" and "\n" in allowed_tokens)
                        )
                        if not token_allowed:
                            continue
                        next_prefix = prefix + id_to_text.get(tid, "")
                        if not is_valid_ainl_prefix_strict(next_prefix):
                            continue
                        allowed_ids.append(tid)
                    if eos_id is not None and _can_finish(prefix):
                        allowed_ids.append(eos_id)
                    if not allowed_ids and fallback_ids:
                        allowed_ids = list(fallback_ids)
                    if allowed_ids:
                        mask = torch.full_like(scores[row], float("-inf"))
                        idx = torch.tensor(sorted(set(allowed_ids)), device=scores.device, dtype=torch.long)
                        mask[idx] = 0.0
                        scores[row] = scores[row] + mask
                return scores

        logits_processor = [AINLConstraintProcessor()]

    with torch.no_grad():
        output_ids = model.generate(
            **inputs,
            max_new_tokens=args.max_new_tokens,
            do_sample=False,
            use_cache=False,
            logits_processor=logits_processor,
        )

    generated_ids = output_ids[0][inputs["input_ids"].shape[-1] :]
    answer = tokenizer.decode(generated_ids, skip_special_tokens=True).strip()

    def _extract_ainl_lines(text: str, *, chunk_lines: int, max_lines: int) -> str:
        line_re = (
            r"^(S|D|E|L[\w-]*:|R|J|U|T|Q|Sc|Cr|P|C|A|Rt|Lay|Fm|Tbl|Ev|"
            r"If|Err|Retry|Call|Set|Filt|Sort|X|Loop|While|CacheGet|CacheSet|QueuePut|Tx|Enf)(\b|\s|$)"
        )
        raw_lines = (text or "").splitlines()
        out: List[str] = []
        step = max(16, int(chunk_lines))
        limit = max(32, int(max_lines))
        for i in range(0, len(raw_lines), step):
            chunk = raw_lines[i : i + step]
            for ln in chunk:
                s = ln.strip()
                if not s:
                    continue
                if re.match(line_re, s):
                    out.append(s)
                    if len(out) >= limit:
                        return "\n".join(out).strip()
        return "\n".join(out).strip()

    strict_compiler = AICodeCompiler(strict_mode=True)

    def _compile_ok(text: str) -> bool:
        ir = strict_compiler.compile(text, emit_graph=False)
        return not bool(ir.get("errors"))

    if args.canonicalize_output:
        answer = _extract_ainl_lines(
            answer,
            chunk_lines=args.canonicalize_chunk_lines,
            max_lines=args.canonicalize_max_lines,
        )

    for _ in range(max(0, args.repair_attempts)):
        if answer and _compile_ok(answer):
            break
        repair_prompt = (
            "Rewrite into strict canonical AINL only. "
            "Output only AINL lines (S/D/E/L:/R/If/X/J...), no markdown/yaml/prose.\n"
            f"Task:\n{args.prompt}\n"
            f"Current output:\n{answer}\n"
        )
        repair_messages = [{"role": "user", "content": repair_prompt}]
        repair_text = tokenizer.apply_chat_template(
            repair_messages, tokenize=False, add_generation_prompt=True
        )
        repair_inputs = tokenizer(repair_text, return_tensors="pt")
        repair_inputs = {k: v.to(device) for k, v in repair_inputs.items()}
        with torch.no_grad():
            repair_ids = model.generate(
                **repair_inputs,
                max_new_tokens=args.max_new_tokens,
                do_sample=False,
                use_cache=False,
                logits_processor=logits_processor,
            )
        new_ids = repair_ids[0][repair_inputs["input_ids"].shape[-1] :]
        answer = tokenizer.decode(new_ids, skip_special_tokens=True).strip()
        if args.canonicalize_output:
            answer = _extract_ainl_lines(
                answer,
                chunk_lines=args.canonicalize_chunk_lines,
                max_lines=args.canonicalize_max_lines,
            )
    print(answer)


if __name__ == "__main__":
    main()
