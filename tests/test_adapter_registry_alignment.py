import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def _load_manifest():
    root = os.path.dirname(os.path.dirname(__file__))
    p = os.path.join(root, "tooling", "adapter_manifest.json")
    with open(p, "r", encoding="utf-8") as f:
        return json.load(f)


def _load_registry():
    root = os.path.dirname(os.path.dirname(__file__))
    p = os.path.join(root, "ADAPTER_REGISTRY.json")
    with open(p, "r", encoding="utf-8") as f:
        return json.load(f)


def test_registry_targets_align_with_manifest_verbs_for_overlapping_adapters():
    manifest = _load_manifest()["adapters"]
    registry = _load_registry().get("adapters", {})

    for name, reg_cfg in registry.items():
        if name not in manifest:
            continue
        manifest_verbs = {str(v).upper() for v in manifest[name].get("verbs", [])}
        targets = reg_cfg.get("targets", {}) or {}
        for tgt in targets.keys():
            # registry uses lowercase verbs/targets; compare case-insensitively.
            assert tgt.upper() in manifest_verbs, f"registry verb {name}.{tgt} missing from manifest verbs {sorted(manifest_verbs)}"
