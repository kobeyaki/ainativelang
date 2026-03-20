"""
Compact textual view over the AINL graph IR.

Design goals:
- **View only**: JSON IR remains the canonical semantic representation.
- **Deterministic**: encoding is stable given the same semantic graph.
- **Lossless for graph semantics**: entry/nodes/edges/exits/effects/data round‑trip.
- **Token efficient**: minimal keys, positional fields, no extra whitespace.
"""

from __future__ import annotations

import json
from typing import Any, Dict, List, Optional, Tuple

from tooling.ir_canonical import attach_label_and_node_hashes, canonicalize_ir, graph_semantic_checksum
from tooling.graph_slice import graph_slice


def _encode_list(names: Optional[List[str]]) -> str:
    if not names:
        return "-"
    return ",".join(sorted(str(n) for n in names))


def _decode_list(token: str) -> List[str]:
    if token == "-" or token == "":
        return []
    return [p for p in token.split(",") if p]


def encode_ir_compact(ir: Dict[str, Any]) -> str:
    """
    Encode the IR's label graphs into a compact textual form.

    Format (whitespace separated tokens, one statement per line):
      L <label_id> <entry_node_id_or_->
      N <node_id> <op> <effect_tier_or_-> <effect_or_-> <reads_or_-> <writes_or_-> <data_json_or_->
      E <from> <port> <to> <to_kind>
      X <node> <var>

    Labels are emitted in canonical id order; within each label, nodes/edges/exits
    are emitted in canonical order (via canonicalize_ir).
    """
    canon = canonicalize_ir(ir or {})
    labels = canon.get("labels") or {}
    lines: List[str] = ["V 1"]

    for lid in sorted(labels.keys(), key=str):
        body = labels.get(lid) or {}
        entry = body.get("entry") or "-"
        lines.append(f"L {lid} {entry}")

        for n in body.get("nodes") or []:
            if not isinstance(n, dict):
                continue
            nid = n.get("id", "")
            op = n.get("op", "") or ""
            effect_tier = n.get("effect_tier")
            eff_tier_tok = str(effect_tier) if effect_tier is not None else "-"
            effect = n.get("effect") or "-"
            reads_tok = _encode_list(n.get("reads"))
            writes_tok = _encode_list(n.get("writes"))
            data = n.get("data", None)
            if data is None:
                data_tok = "-"
            else:
                data_tok = json.dumps(data, separators=(",", ":"), sort_keys=True)
            lines.append(
                f"N {nid} {op} {eff_tier_tok} {effect} {reads_tok} {writes_tok} {data_tok}"
            )

        for e in body.get("edges") or []:
            if not isinstance(e, dict):
                continue
            frm = e.get("from", "")
            port = e.get("port") or "next"
            to = e.get("to", "")
            to_kind = e.get("to_kind", "node")
            lines.append(f"E {frm} {port} {to} {to_kind}")

        for ex in body.get("exits") or []:
            if not isinstance(ex, dict):
                continue
            node = ex.get("node", "")
            var = ex.get("var", "")
            lines.append(f"X {node} {var}")

    return ("\n".join(lines) + "\n") if lines else ""


def decode_ir_compact(text: str) -> Dict[str, Any]:
    """
    Decode the compact textual form back into an IR fragment:

      {"labels": {<lid>: {"entry": ..., "nodes": [...], "edges": [...], "exits": [...]}}}

    This covers the semantic graph layer only; callers can merge this fragment
    back into a full IR if they want to preserve surrounding metadata.
    """
    labels: Dict[str, Dict[str, Any]] = {}
    current_lid: Optional[str] = None
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split(" ")
        tag = parts[0]
        if tag == "L":
            if len(parts) < 3:
                raise ValueError(f"Malformed L line: {line!r}")
            current_lid = str(parts[1])
            entry_tok = parts[2]
            entry = None if entry_tok == "-" else entry_tok
            labels[current_lid] = {
                "entry": entry,
                "nodes": [],
                "edges": [],
                "exits": [],
            }
        elif tag == "N":
            if current_lid is None:
                raise ValueError(f"N line before any L: {line!r}")
            if len(parts) < 8:
                raise ValueError(f"Malformed N line: {line!r}")
            _, nid, op, eff_tier_tok, eff_tok, reads_tok, writes_tok, data_tok, *extra = parts
            node: Dict[str, Any] = {"id": nid, "op": op}
            if eff_tier_tok != "-":
                try:
                    node["effect_tier"] = int(eff_tier_tok)
                except ValueError:
                    node["effect_tier"] = eff_tier_tok
            if eff_tok != "-":
                node["effect"] = eff_tok
            reads = _decode_list(reads_tok)
            if reads:
                node["reads"] = reads
            writes = _decode_list(writes_tok)
            if writes:
                node["writes"] = writes
            if data_tok != "-":
                try:
                    node["data"] = json.loads(data_tok)
                except json.JSONDecodeError:
                    # Fall back to raw string if somehow not valid JSON.
                    node["data"] = data_tok
            if extra:
                node["_extra"] = extra
            labels[current_lid]["nodes"].append(node)
        elif tag == "E":
            if current_lid is None:
                raise ValueError(f"E line before any L: {line!r}")
            if len(parts) < 5:
                raise ValueError(f"Malformed E line: {line!r}")
            _, frm, port, to, to_kind, *extra = parts
            edge: Dict[str, Any] = {"from": frm, "port": port, "to": to, "to_kind": to_kind}
            if extra:
                edge["_extra"] = extra
            labels[current_lid]["edges"].append(edge)
        elif tag == "X":
            if current_lid is None:
                raise ValueError(f"X line before any L: {line!r}")
            if len(parts) < 3:
                raise ValueError(f"Malformed X line: {line!r}")
            _, node, var, *extra = parts
            ex: Dict[str, Any] = {"node": node, "var": var}
            if extra:
                ex["_extra"] = extra
            labels[current_lid]["exits"].append(ex)
        elif tag == "V":
            # Version header; currently only V 1 is emitted. Ignore for now.
            continue
        else:
            raise ValueError(f"Unknown compact IR tag {tag!r} in line: {line!r}")
    return {"labels": labels}


def compact_diff(old_text: str, new_text: str) -> Dict[str, Any]:
    """
    Compute a structural diff between two compact encodings.

    Internally decodes to IR fragments and delegates to graph_diff.graph_diff.
    """
    from tooling.graph_diff import graph_diff

    old_ir = decode_ir_compact(old_text or "")
    new_ir = decode_ir_compact(new_text or "")
    return graph_diff(old_ir, new_ir)


def trace_compact_snapshot(
    ir: Dict[str, Any],
    label_id: str,
    traces: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """
    Build a compact snapshot for an executed label, suitable for agent prompts.

    Returns:
      {
        "graph_semantic_checksum": "...",
        "labels": {label_id: {"id_hash": "..."}},
        "compact": "<compact textual graph>",
        "trace_count": N,
      }
    """
    from copy import deepcopy

    ir_local = attach_label_and_node_hashes(deepcopy(ir or {}))
    lid = str(label_id)
    labels = ir_local.get("labels") or {}
    if lid not in labels:
        raise KeyError(f"label_id {lid!r} not found in IR")
    sub_ir = {"labels": {lid: labels[lid]}}
    checksum = graph_semantic_checksum(sub_ir)
    compact = encode_ir_compact(sub_ir)
    return {
        "graph_semantic_checksum": checksum,
        "labels": {lid: {"id_hash": labels[lid].get("id_hash")}},
        "compact": compact,
        "trace_count": len(traces or []),
    }


def compact_slice_snapshot(
    ir: Dict[str, Any],
    label_id: str,
    start_node_id: str,
    *,
    depth: int = 2,
    traces: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """
    Build a compact snapshot for a sliced subgraph around a node.

    Meant for debug envelopes:
      - error dict
      - trace events
      - compact slice
      - checksum/label hash
    """
    from copy import deepcopy

    slice_ir = graph_slice(ir, label_id, start_node_id, depth=depth)
    slice_ir = attach_label_and_node_hashes(deepcopy(slice_ir or {}))
    lids = list((slice_ir.get("labels") or {}).keys())
    if not lids:
        raise KeyError("No labels in sliced IR")
    lid = lids[0]
    labels = slice_ir["labels"]
    checksum = graph_semantic_checksum(slice_ir)
    compact = encode_ir_compact(slice_ir)
    return {
        "graph_semantic_checksum": checksum,
        "labels": {lid: {"id_hash": labels[lid].get("id_hash")}},
        "compact": compact,
        "trace_count": len(traces or []),
    }


__all__ = ["encode_ir_compact", "decode_ir_compact", "compact_diff", "trace_compact_snapshot", "compact_slice_snapshot"]
