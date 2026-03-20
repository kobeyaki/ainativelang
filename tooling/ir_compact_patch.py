"""
Patch DSL operating in compact graph space.

Format (one patch per line):

  P REWIRE label=1 from=n3 port=err to=n9 kind=node
  P SETNODE label=1 node=n2 data={"var":"quote"}

These map to structured graph_rewrite operations and are applied
sequentially against a full JSON IR. Agents typically obtain node ids
from the compact encoding, then emit these minimal patches.
"""

from __future__ import annotations

import json
from typing import Any, Dict, List

from tooling.graph_rewrite import apply_patch
from tooling.ir_canonical import attach_label_and_node_hashes, graph_semantic_checksum


def _parse_kv_tokens(tokens: List[str]) -> Dict[str, str]:
    out: Dict[str, str] = {}
    for t in tokens:
        if "=" not in t:
            continue
        k, v = t.split("=", 1)
        out[k] = v
    return out


def _parse_single_patch(line: str) -> Dict[str, Any]:
    parts = line.strip().split()
    if not parts or parts[0] != "P":
        raise ValueError(f"Invalid patch line (must start with 'P'): {line!r}")
    if len(parts) < 2:
        raise ValueError(f"Patch line missing op: {line!r}")
    op = parts[1].upper()
    kv = _parse_kv_tokens(parts[2:])

    if op == "REWIRE":
        label = kv.get("label")
        from_id = kv.get("from")
        from_hash = kv.get("from_hash")
        port = kv.get("port")
        to = kv.get("to")
        to_hash = kv.get("to_hash")
        kind = kv.get("kind", "node")
        if not (label and port and (from_id or from_hash) and (to or to_hash)):
            raise ValueError(f"REWIRE patch missing required fields: {line!r}")
        patch: Dict[str, Any] = {
            "op": "rewire_edge",
            "label_id": label,
            "port": port,
            "to_kind": kind,
        }
        if from_id:
            patch["from_node_id"] = from_id
        if from_hash:
            patch["from_hash"] = from_hash
        if to:
            patch["to"] = to
        if to_hash:
            patch["to_hash"] = to_hash
        if "requires_checksum" in kv:
            patch["requires_checksum"] = kv["requires_checksum"]
        if "requires_label_hash" in kv:
            patch["requires_label_hash"] = kv["requires_label_hash"]
        return patch

    if op == "SETNODE":
        label = kv.get("label")
        node_id = kv.get("node")
        node_hash = kv.get("node_hash")
        data_raw = kv.get("data", "{}")
        if not (label and (node_id or node_hash)):
            raise ValueError(f"SETNODE patch missing required fields: {line!r}")
        try:
            data = json.loads(data_raw)
        except json.JSONDecodeError as e:
            raise ValueError(f"SETNODE data is not valid JSON: {data_raw!r}") from e
        if not isinstance(data, dict):
            raise ValueError(f"SETNODE data must be JSON object: {data_raw!r}")
        patch = {
            "op": "set_node_data",
            "label_id": label,
            "data": data,
        }
        if node_id:
            patch["node_id"] = node_id
        if node_hash:
            patch["node_hash"] = node_hash
        if "requires_checksum" in kv:
            patch["requires_checksum"] = kv["requires_checksum"]
        if "requires_label_hash" in kv:
            patch["requires_label_hash"] = kv["requires_label_hash"]
        return patch

    raise ValueError(f"Unknown patch op {op!r} in line: {line!r}")


def parse_compact_patches(text: str) -> List[Dict[str, Any]]:
    """Parse a multi-line compact patch string into a list of patch dicts."""
    patches: List[Dict[str, Any]] = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        patches.append(_parse_single_patch(line))
    return patches


def apply_compact_patches(
    ir: Dict[str, Any],
    text: str,
    *,
    normalize: bool = True,
    re_annotate_effects: bool = True,
    strict_validate: bool = True,
) -> Dict[str, Any]:
    """
    Apply one or more compact patches to ir.

    Returns:
      {"ok": True, "ir": new_ir}
    or:
      {"ok": False, "error": {code, message, details, patch_index, line}}
    """
    from copy import deepcopy

    try:
        patches = parse_compact_patches(text)
    except Exception as e:
        return {
            "ok": False,
            "error": {
                "code": "PATCH_PARSE",
                "message": str(e),
                "patch_index": -1,
                "line": "",
                "data": {},
            },
        }

    ir_cur = deepcopy(ir or {})
    lines = [l for l in text.splitlines() if l.strip() and not l.strip().startswith("#")]

    # Attach hashes/checksum for optimistic concurrency and hash-based addressing.
    ir_hashed = attach_label_and_node_hashes(deepcopy(ir_cur or {}))
    labels = ir_hashed.get("labels") or {}
    label_hashes = {str(lid): (body or {}).get("id_hash") for lid, body in labels.items()}
    graph_checksum = graph_semantic_checksum(ir_hashed)
    hash_index = {
        str(lid): {
            n.get("hash"): n.get("id")
            for n in (body or {}).get("nodes") or []
            if n.get("hash") and n.get("id")
        }
        for lid, body in labels.items()
    }

    for idx, patch in enumerate(patches):
        lid = str(patch.get("label_id", ""))

        # Preconditions: checksum / label hash.
        req_cs = patch.get("requires_checksum")
        if req_cs and req_cs != graph_checksum:
            return {
                "ok": False,
                "error": {
                    "code": "PATCH_PRECONDITION_FAILED",
                    "message": "graph_semantic_checksum mismatch",
                    "patch_index": idx,
                    "line": lines[idx] if idx < len(lines) else "",
                    "data": {
                        "actual_checksum": graph_checksum,
                        "expected_checksum": req_cs,
                    },
                },
            }
        req_label_hash = patch.get("requires_label_hash")
        if req_label_hash:
            cur_lh = label_hashes.get(lid)
            if cur_lh != req_label_hash:
                return {
                    "ok": False,
                    "error": {
                        "code": "PATCH_PRECONDITION_FAILED",
                        "message": "label hash mismatch",
                        "patch_index": idx,
                        "line": lines[idx] if idx < len(lines) else "",
                        "data": {
                            "label_id": lid,
                            "actual_label_hash": cur_lh,
                            "expected_label_hash": req_label_hash,
                        },
                    },
                }

        # Resolve hash-based addressing to node ids using snapshot index.
        if "node_hash" in patch and "node_id" not in patch:
            nh = patch["node_hash"]
            nid = hash_index.get(lid, {}).get(nh)
            if not nid:
                return {
                    "ok": False,
                    "error": {
                        "code": "PATCH_HASH_RESOLVE",
                        "message": f"node_hash {nh!r} not found for label {lid!r}",
                        "patch_index": idx,
                        "line": lines[idx] if idx < len(lines) else "",
                        "data": {"label_id": lid, "kind": "node_hash", "hash": nh},
                    },
                }
            patch["node_id"] = nid
        if "from_hash" in patch and "from_node_id" not in patch:
            fh = patch["from_hash"]
            fid = hash_index.get(lid, {}).get(fh)
            if not fid:
                return {
                    "ok": False,
                    "error": {
                        "code": "PATCH_HASH_RESOLVE",
                        "message": f"from_hash {fh!r} not found for label {lid!r}",
                        "patch_index": idx,
                        "line": lines[idx] if idx < len(lines) else "",
                        "data": {"label_id": lid, "kind": "from_hash", "hash": fh},
                    },
                }
            patch["from_node_id"] = fid
        if "to_hash" in patch and "to" not in patch:
            th = patch["to_hash"]
            tid = hash_index.get(lid, {}).get(th)
            if not tid:
                return {
                    "ok": False,
                    "error": {
                        "code": "PATCH_HASH_RESOLVE",
                        "message": f"to_hash {th!r} not found for label {lid!r}",
                        "patch_index": idx,
                        "line": lines[idx] if idx < len(lines) else "",
                        "data": {"label_id": lid, "kind": "to_hash", "hash": th},
                    },
                }
            patch["to"] = tid

        ir_next, err = apply_patch(
            ir_cur,
            patch,
            normalize=normalize,
            re_annotate_effects=re_annotate_effects,
            strict_validate=strict_validate,
        )
        if err is not None:
            return {
                "ok": False,
                "error": {
                    "code": err.get("code", "PATCH_APPLY"),
                    "message": err.get("message", "patch application failed"),
                    "patch_index": idx,
                    "line": lines[idx] if idx < len(lines) else "",
                    "data": {"details": err.get("details", [])},
                },
            }
        ir_cur = ir_next

    return {"ok": True, "ir": ir_cur}


__all__ = ["parse_compact_patches", "apply_compact_patches"]
