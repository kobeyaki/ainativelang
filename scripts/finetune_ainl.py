#!/usr/bin/env python3
"""
Fine-tune a small model on AINL corpus using LoRA.
Designed for Mac M2 Pro (16GB) — uses CPU/MPS, small batches.
"""

import argparse
import json
import os
import random
import time
from pathlib import Path
BASE = Path(__file__).resolve().parents[1]
DATA_PATH = BASE / "corpus" / "train_chatml_train.jsonl"
EVAL_DATA_PATH = BASE / "corpus" / "train_chatml_val.jsonl"
OUTPUT_DIR = BASE / "models" / "ainl-phi3-lora"

MODEL_NAME = "microsoft/phi-3-mini-4k-instruct"

def load_chatml(path):
    with open(path, encoding="utf-8") as f:
        for line in f:
            yield {"messages": json.loads(line)["messages"]}

def main():
    t_session0 = time.time()
    stage_timing = {
        "dataset_preflight_seconds": 0.0,
        "model_load_seconds": 0.0,
        "dataset_build_seconds": 0.0,
        "tokenize_seconds": 0.0,
        "trainer_init_seconds": 0.0,
        "train_seconds": 0.0,
        "save_seconds": 0.0,
    }
    parser = argparse.ArgumentParser(description="Fine-tune AINL LoRA model.")
    parser.add_argument("--dry-run", action="store_true", help="Validate env/data and exit before training.")
    parser.add_argument("--epochs", type=int, default=1, help="Number of training epochs.")
    parser.add_argument("--max-length", type=int, default=1024, help="Max token length for each example.")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for reproducible training.")
    parser.add_argument("--data-path", type=Path, default=DATA_PATH, help="Path to ChatML JSONL dataset.")
    parser.add_argument("--eval-data-path", type=Path, default=EVAL_DATA_PATH, help="Path to ChatML validation dataset.")
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIR, help="Directory to store adapter checkpoints.")
    parser.add_argument(
        "--train-device",
        choices=["auto", "mps", "cpu"],
        default="auto",
        help="Training device strategy. auto uses HF device_map auto; mps/cpu forces a single device.",
    )
    parser.add_argument(
        "--profile",
        choices=["fast", "balanced", "quality"],
        default="balanced",
        help="Training profile preset. fast is quickest; quality is slower but broader.",
    )
    parser.add_argument("--batch-size", type=int, default=2, help="Per-device train batch size.")
    parser.add_argument("--grad-accum", type=int, default=2, help="Gradient accumulation steps.")
    parser.add_argument("--learning-rate", type=float, default=2e-4, help="Learning rate.")
    parser.add_argument("--logging-steps", type=int, default=50, help="Trainer logging frequency.")
    parser.add_argument("--save-steps", type=int, default=500, help="Checkpoint save frequency.")
    parser.add_argument("--save-total-limit", type=int, default=8, help="Maximum checkpoints to keep during training.")
    parser.add_argument("--eval-steps", type=int, default=250, help="Validation frequency in steps when eval set is provided.")
    parser.add_argument(
        "--select-best-by-loss",
        action="store_true",
        help="If set, load best checkpoint at end by eval_loss (not recommended for AINL quality selection).",
    )
    parser.add_argument(
        "--max-train-samples",
        type=int,
        default=0,
        help="If >0, train on only the first N examples after shuffle (quick iteration).",
    )
    args_ns = parser.parse_args()

    try:
        from datasets import Dataset
        from transformers import AutoConfig, AutoModelForCausalLM, AutoTokenizer, TrainingArguments, Trainer
        from transformers.cache_utils import DynamicCache
        from peft import LoraConfig, get_peft_model
    except Exception as e:
        raise SystemExit(
            "Missing fine-tune dependencies. Install with:\n"
            "pip install datasets transformers accelerate peft sentencepiece\n"
            f"Original error: {e}"
        )

    # Compatibility shims for phi3 remote code with older/newer transformers cache APIs.
    if not hasattr(DynamicCache, "seen_tokens"):
        DynamicCache.seen_tokens = property(lambda self: self.get_seq_length())
    if not hasattr(DynamicCache, "get_max_length"):
        DynamicCache.get_max_length = DynamicCache.get_max_cache_shape
    if not hasattr(DynamicCache, "get_usable_length"):
        DynamicCache.get_usable_length = lambda self, seq_length: self.get_seq_length()

    t0 = time.time()
    data_path = args_ns.data_path
    if not data_path.exists():
        raise SystemExit(
            f"Training dataset not found: {data_path}\n"
            "Run scripts/convert_to_training.py first."
        )
    with open(data_path, encoding="utf-8") as _f:
        line_count = sum(1 for _ in _f)
    if line_count == 0:
        raise SystemExit(f"Training dataset is empty: {data_path}")
    eval_data_path = args_ns.eval_data_path
    eval_line_count = 0
    if eval_data_path and eval_data_path.exists():
        with open(eval_data_path, encoding="utf-8") as _f:
            eval_line_count = sum(1 for _ in _f)
    stage_timing["dataset_preflight_seconds"] = time.time() - t0

    if args_ns.dry_run:
        print(
            "Preflight OK. "
            f"Train lines: {line_count} ({data_path}). "
            f"Eval lines: {eval_line_count} ({eval_data_path})."
        )
        return

    random.seed(args_ns.seed)

    t0 = time.time()
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, trust_remote_code=True)
    tokenizer.pad_token = tokenizer.eos_token

    config = AutoConfig.from_pretrained(MODEL_NAME, trust_remote_code=True)
    # Some Phi-3 configs expose rope_scaling["rope_type"] instead of ["type"].
    # Normalize for compatibility with remote model code variants.
    if isinstance(getattr(config, "rope_scaling", None), dict):
        rope_scaling = dict(config.rope_scaling)
        if "type" not in rope_scaling and "rope_type" in rope_scaling:
            rope_scaling["type"] = rope_scaling["rope_type"]
        # Remote phi3 implementations vary: "default" can mean "no scaling".
        if str(rope_scaling.get("type", "")).lower() in {"default", "none", "null"}:
            config.rope_scaling = None
        else:
            config.rope_scaling = rope_scaling

    # Profile tuning for speed/quality trade-offs on small machines.
    target_module_candidates = ["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"]
    if args_ns.profile == "fast":
        args_ns.max_length = min(args_ns.max_length, 768)
        args_ns.epochs = min(args_ns.epochs, 1)
        args_ns.batch_size = min(args_ns.batch_size, 2)
        args_ns.grad_accum = 1
        args_ns.logging_steps = max(args_ns.logging_steps, 50)
        args_ns.save_steps = max(args_ns.save_steps, 500)
        args_ns.eval_steps = max(args_ns.eval_steps, 250)
        target_module_candidates = ["q_proj", "v_proj", "qkv_proj", "o_proj"]
    elif args_ns.profile == "quality":
        args_ns.max_length = max(args_ns.max_length, 1536)
        args_ns.epochs = max(args_ns.epochs, 2)
        args_ns.grad_accum = max(args_ns.grad_accum, 2)
        args_ns.eval_steps = min(args_ns.eval_steps, 200)

    device_map = "auto"
    force_device = None
    if args_ns.train_device == "mps":
        device_map = None
        force_device = "mps"
    elif args_ns.train_device == "cpu":
        device_map = None
        force_device = "cpu"

    model = AutoModelForCausalLM.from_pretrained(
        MODEL_NAME,
        config=config,
        trust_remote_code=True,
        attn_implementation="eager",
        torch_dtype="auto",
        device_map=device_map,
    )
    model.config.use_cache = False
    if force_device is not None:
        try:
            import torch
            if force_device == "mps" and not torch.backends.mps.is_available():
                raise SystemExit("Requested --train-device mps but MPS is unavailable.")
        except Exception:
            if force_device == "mps":
                raise
        model = model.to(force_device)
    stage_timing["model_load_seconds"] = time.time() - t0

    available_leaf_names = {name.split(".")[-1] for name, _ in model.named_modules()}
    target_modules = [m for m in target_module_candidates if m in available_leaf_names]
    if not target_modules:
        raise SystemExit(
            "Could not find compatible LoRA target modules in the loaded model. "
            f"Candidates tried: {target_module_candidates}. "
            f"Available example modules: {sorted(list(available_leaf_names))[:25]}"
        )

    lora_cfg = LoraConfig(
        r=8,
        lora_alpha=16,
        target_modules=target_modules,
        lora_dropout=0.05,
        bias="none",
        task_type="CAUSAL_LM"
    )
    model = get_peft_model(model, lora_cfg)
    model.print_trainable_parameters()

    t0 = time.time()
    train_dataset = Dataset.from_generator(lambda: load_chatml(data_path))
    eval_dataset = None
    if eval_line_count > 0:
        eval_dataset = Dataset.from_generator(lambda: load_chatml(eval_data_path))
    stage_timing["dataset_build_seconds"] = time.time() - t0

    # Seed all frameworks available for reproducibility.
    try:
        import numpy as np
        np.random.seed(args_ns.seed)
    except Exception:
        pass
    try:
        import torch
        torch.manual_seed(args_ns.seed)
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(args_ns.seed)
    except Exception:
        pass
    try:
        from transformers import set_seed as hf_set_seed
        hf_set_seed(args_ns.seed)
    except Exception:
        pass

    if args_ns.max_train_samples and args_ns.max_train_samples > 0:
        train_dataset = train_dataset.select(range(min(args_ns.max_train_samples, len(train_dataset))))

    def tokenize_fn(ex):
        text = tokenizer.apply_chat_template(ex["messages"], tokenize=False, add_generation_prompt=False)
        # Dynamic padding via data collator is much faster than fixed max_length padding.
        tokenized = tokenizer(text, truncation=True, max_length=args_ns.max_length, padding=False)
        return tokenized

    t0 = time.time()
    train_dataset = train_dataset.map(tokenize_fn, remove_columns=["messages"])
    if eval_dataset is not None:
        eval_dataset = eval_dataset.map(tokenize_fn, remove_columns=["messages"])
    stage_timing["tokenize_seconds"] = time.time() - t0

    evaluation_strategy = "steps" if eval_dataset is not None else "no"
    use_bf16 = bool(os.environ.get("AINL_USE_BF16", "0") == "1")
    train_args_kwargs = dict(
        output_dir=str(args_ns.output_dir),
        num_train_epochs=args_ns.epochs,
        per_device_train_batch_size=args_ns.batch_size,
        gradient_accumulation_steps=args_ns.grad_accum,
        learning_rate=args_ns.learning_rate,
        fp16=False,
        bf16=use_bf16,  # enable via AINL_USE_BF16=1 when supported
        logging_steps=args_ns.logging_steps,
        save_steps=args_ns.save_steps,
        save_total_limit=args_ns.save_total_limit,
        report_to="none",
        seed=args_ns.seed,
        data_seed=args_ns.seed,
    )
    ta_vars = set(getattr(TrainingArguments.__init__, "__code__").co_varnames)
    if "save_strategy" in ta_vars:
        train_args_kwargs["save_strategy"] = "steps"
    if eval_dataset is not None:
        train_args_kwargs["eval_steps"] = args_ns.eval_steps
        # transformers naming differs across versions.
        if "evaluation_strategy" in ta_vars:
            train_args_kwargs["evaluation_strategy"] = "steps"
        elif "eval_strategy" in ta_vars:
            train_args_kwargs["eval_strategy"] = "steps"
        if args_ns.select_best_by_loss:
            if "load_best_model_at_end" in ta_vars:
                train_args_kwargs["load_best_model_at_end"] = True
            if "metric_for_best_model" in ta_vars:
                train_args_kwargs["metric_for_best_model"] = "eval_loss"
            if "greater_is_better" in ta_vars:
                train_args_kwargs["greater_is_better"] = False
    args = TrainingArguments(**train_args_kwargs)

    from transformers import DataCollatorForLanguageModeling
    data_collator = DataCollatorForLanguageModeling(tokenizer=tokenizer, mlm=False)

    t0 = time.time()
    trainer = Trainer(
        model=model,
        args=args,
        train_dataset=train_dataset,
        eval_dataset=eval_dataset,
        data_collator=data_collator,
    )
    stage_timing["trainer_init_seconds"] = time.time() - t0

    t0 = time.time()
    trainer.train()
    stage_timing["train_seconds"] = time.time() - t0
    t0 = time.time()
    model.save_pretrained(args_ns.output_dir)
    stage_timing["save_seconds"] = time.time() - t0
    stage_timing["session_total_seconds"] = time.time() - t_session0
    args_ns.output_dir.mkdir(parents=True, exist_ok=True)
    diag_path = args_ns.output_dir / "training_diagnostics.json"
    with open(diag_path, "w", encoding="utf-8") as f:
        json.dump(
            {
                "model_name": MODEL_NAME,
                "data_path": str(data_path),
                "eval_data_path": str(eval_data_path),
                "line_count_train": line_count,
                "line_count_eval": eval_line_count,
                "timing": stage_timing,
            },
            f,
            indent=2,
        )
    print(f"Model saved to {args_ns.output_dir}")
    print(f"Training diagnostics written to {diag_path}")

if __name__ == "__main__":
    main()
