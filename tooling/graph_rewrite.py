"""
Graph rewrite: apply structured patches to IR and validate. Returns (new_ir, None) or (None, error_struct).
Agents propose patches; we apply transactionally and reject if validation fails.
Unified contract: apply_patch_ok / insert_node_after / rewire_edge / wrap_r_with_retry / attach_err_handler
return {"ok": True, "ir": ir} or {"ok": False, "error": error_struct}.
"""
import copy
from typing import Any, Dict, List, Optional, Tuple

from compiler_v2 import AICodeCompiler
from tooling.graph_api import label_edges, label_nodes, successors
from tooling.graph_normalize import normalize_graph
from tooling.effect_analysis import annotate_ir_effect_analysis


def _validate_after_patch(ir: Dict[str, Any], strict: bool) -> List[str]:
    """Run compiler-owned strict graph validation invariants."""
    c = AICodeCompiler(strict_mode=bool(strict), strict_reachability=bool(strict))
    c.labels = copy.deepcopy(ir.get("labels") or {})
    c.services = copy.deepcopy(ir.get("services") or {})
    c._errors = []
    c._validate_graphs()
    # Patches should be rejected for structural graph contract violations. We do not
    # block on pre-existing dataflow "may be undefined" findings here.
    return [e for e in c._errors if "may be undefined on this path" not in str(e)]


def apply_patch(
    ir: Dict[str, Any],
    patch: Dict[str, Any],
    *,
    normalize: bool = True,
    re_annotate_effects: bool = True,
    strict_validate: bool = True,
) -> Tuple[Optional[Dict[str, Any]], Optional[Dict[str, Any]]]:
    """
    Apply a single patch to ir. Returns (new_ir, None) on success or (None, error_struct) on failure.
    error_struct: { "code": str, "message": str, "details": list }.
    """
    op = patch.get("op")
    if not op:
        return None, {"code": "PATCH_INVALID", "message": "patch missing 'op'", "details": []}

    try:
        ir = copy.deepcopy(ir)
    except Exception as e:
        return None, {"code": "PATCH_COPY", "message": str(e), "details": []}

    labels = ir.setdefault("labels", {})
    lid = str(patch.get("label_id", ""))
    if not lid or lid not in labels:
        return None, {"code": "PATCH_LABEL", "message": f"label_id {lid!r} not found", "details": [lid]}

    body = labels[lid]
    nodes = list(body.get("nodes") or [])
    edges = list(body.get("edges") or [])
    node_by_id = {n.get("id"): n for n in nodes if n.get("id")}

    if op == "add_node":
        new_node = patch.get("node")
        if not new_node or not new_node.get("id"):
            return None, {"code": "PATCH_ADD_NODE", "message": "node must have id", "details": []}
        nid = new_node["id"]
        if nid in node_by_id:
            return None, {"code": "PATCH_ADD_NODE", "message": f"node {nid} already exists", "details": [nid]}
        nodes.append(new_node)
        body["nodes"] = nodes
        # Optional: after_node_id + new_edges to wire in
        after = patch.get("after_node_id")
        if after and after in node_by_id:
            new_edges = patch.get("new_edges") or [{"from": after, "to": nid, "to_kind": "node", "port": "next"}]
            for e in new_edges:
                edges.append(e)
            body["edges"] = edges

    elif op == "rewire_edge":
        from_id = patch.get("from_node_id")
        port = patch.get("port")
        to_id = patch.get("to")  # node id or label id
        to_kind = patch.get("to_kind", "node")
        if not from_id or not port:
            return None, {"code": "PATCH_REWIRE", "message": "from_node_id and port required", "details": []}
        for e in edges:
            if e.get("from") == from_id and (e.get("port") or "next") == port:
                e["to"] = to_id
                e["to_kind"] = to_kind
                break
        else:
            edges.append({"from": from_id, "to": to_id, "to_kind": to_kind, "port": port})
            body["edges"] = edges

    elif op == "remove_node":
        nid = patch.get("node_id")
        if not nid or nid not in node_by_id:
            return None, {"code": "PATCH_REMOVE", "message": f"node {nid!r} not found", "details": [nid or ""]}
        body["nodes"] = [n for n in nodes if n.get("id") != nid]
        body["edges"] = [e for e in edges if e.get("from") != nid and e.get("to") != nid]

    elif op == "set_node_data":
        nid = patch.get("node_id")
        data = patch.get("data")
        if not isinstance(data, dict) or not nid or nid not in node_by_id:
            return None, {
                "code": "PATCH_SET_NODE",
                "message": f"node_id {nid!r} not found or data is not a dict",
                "details": [nid or "", data],
            }
        node = node_by_id[nid]
        node_data = node.get("data") or {}
        if not isinstance(node_data, dict):
            node_data = {}
        node_data.update(data)
        node["data"] = node_data

    else:
        return None, {"code": "PATCH_OP", "message": f"unknown patch op {op!r}", "details": [op]}

    if normalize:
        ir = normalize_graph(ir)
    if re_annotate_effects:
        ir = annotate_ir_effect_analysis(ir)
    if strict_validate:
        errs = _validate_after_patch(ir, strict=True)
        if errs:
            return None, {"code": "PATCH_VALIDATE", "message": "validation failed after patch", "details": errs}
    return ir, None


def apply_patch_ok(
    ir: Dict[str, Any],
    patch: Dict[str, Any],
    *,
    normalize: bool = True,
    re_annotate_effects: bool = True,
    strict_validate: bool = True,
) -> Dict[str, Any]:
    """Apply patch; return {"ok": True, "ir": ir} or {"ok": False, "error": error_struct}. Agent contract."""
    new_ir, err = apply_patch(ir, patch, normalize=normalize, re_annotate_effects=re_annotate_effects, strict_validate=strict_validate)
    if err:
        return {"ok": False, "error": err}
    return {"ok": True, "ir": new_ir}


def insert_node_after(
    ir: Dict[str, Any],
    label_id: str,
    after_node_id: str,
    new_node: Dict[str, Any],
    port: str = "next",
) -> Dict[str, Any]:
    """Insert new_node after after_node_id (wire with given port). Returns {ok, ir} or {ok: False, error}."""
    patch = {
        "op": "add_node",
        "label_id": label_id,
        "node": new_node,
        "after_node_id": after_node_id,
        "new_edges": [{"from": after_node_id, "to": new_node.get("id"), "to_kind": "node", "port": port}],
    }
    return apply_patch_ok(ir, patch)


def rewire_edge(
    ir: Dict[str, Any],
    label_id: str,
    from_node_id: str,
    new_to: str,
    port: str,
    to_kind: str = "node",
) -> Dict[str, Any]:
    """Rewire the edge from from_node_id with port to new_to. Returns {ok, ir} or {ok: False, error}."""
    patch = {"op": "rewire_edge", "label_id": label_id, "from_node_id": from_node_id, "port": port, "to": new_to, "to_kind": to_kind}
    return apply_patch_ok(ir, patch)


def wrap_r_with_retry(
    ir: Dict[str, Any],
    label_id: str,
    r_node_id: str,
    retry_count: int = 3,
    backoff_ms: int = 0,
) -> Dict[str, Any]:
    """Attach retry policy to an R node while preserving its success `next` edge."""
    nodes = label_nodes(ir, label_id)
    if r_node_id not in nodes or (nodes[r_node_id].get("op") or (nodes[r_node_id].get("data") or {}).get("op")) != "R":
        return {"ok": False, "error": {"code": "WRAP_R", "message": f"node {r_node_id!r} is not an R node", "details": [r_node_id]}}
    nexts = successors(ir, label_id, r_node_id, port="next")
    if not nexts:
        return {"ok": False, "error": {"code": "WRAP_R", "message": f"R node {r_node_id!r} has no next successor", "details": [r_node_id]}}
    old_next_id = nexts[0][0]
    max_n = max((int(n["id"][1:]) for n in nodes.values() if n.get("id") and n["id"].startswith("n") and n["id"][1:].isdigit()), default=0)
    retry_nid = f"n{max_n + 1}"
    retry_node = {
        "id": retry_nid,
        "op": "Retry",
        "effect": "meta",
        "reads": [],
        "writes": [],
        "lineno": None,
        "data": {"op": "Retry", "count": retry_count, "backoff_ms": backoff_ms},
    }
    try:
        ir = copy.deepcopy(ir)
    except Exception as e:
        return {"ok": False, "error": {"code": "WRAP_R_COPY", "message": str(e), "details": []}}
    body = (ir.get("labels") or {}).get(label_id)
    if not body:
        return {"ok": False, "error": {"code": "WRAP_R_LABEL", "message": f"label {label_id!r} not found", "details": [label_id]}}
    nodes = list(body.get("nodes") or [])
    edges = list(body.get("edges") or [])
    node_by_id = {n.get("id"): n for n in nodes if n.get("id")}
    if r_node_id not in node_by_id:
        return {"ok": False, "error": {"code": "WRAP_R", "message": f"node {r_node_id!r} not found", "details": [r_node_id]}}
    r_node = node_by_id[r_node_id]
    if (r_node.get("op") or (r_node.get("data") or {}).get("op")) != "R":
        return {"ok": False, "error": {"code": "WRAP_R", "message": f"node {r_node_id!r} is not an R node", "details": [r_node_id]}}
    next_edges = [e for e in edges if e.get("from") == r_node_id and (e.get("port") or "next") == "next"]
    if not next_edges:
        return {"ok": False, "error": {"code": "WRAP_R", "message": f"R node {r_node_id!r} has no next edge", "details": [r_node_id]}}
    old_next_id = next_edges[0].get("to")
    max_n = max((int(n["id"][1:]) for n in nodes if n.get("id") and n["id"].startswith("n") and n["id"][1:].isdigit()), default=0)
    retry_nid = f"n{max_n + 1}"
    retry_node = {
        "id": retry_nid,
        "op": "Retry",
        "effect": "meta",
        "reads": [],
        "writes": [],
        "lineno": None,
        "data": {"op": "Retry", "count": retry_count, "backoff_ms": backoff_ms},
    }
    nodes.append(retry_node)
    # Preserve success flow through the existing next edge; retry is an auxiliary path.
    edges.append({"from": r_node_id, "to": retry_nid, "to_kind": "node", "port": "retry"})
    if not any(e.get("from") == retry_nid and (e.get("port") or "next") == "next" for e in edges):
        edges.append({"from": retry_nid, "to": old_next_id, "to_kind": "node", "port": "next"})
    body["nodes"] = nodes
    body["edges"] = edges
    ir = normalize_graph(ir)
    ir = annotate_ir_effect_analysis(ir)
    errs = _validate_after_patch(ir, strict=True)
    if errs:
        return {"ok": False, "error": {"code": "PATCH_VALIDATE", "message": "validation failed after wrap_r_with_retry", "details": errs}}
    return {"ok": True, "ir": ir}


def attach_err_handler(
    ir: Dict[str, Any],
    label_id: str,
    from_node_id: str,
    handler_label_id: str,
) -> Dict[str, Any]:
    """Insert Err node and wire from_node --err--> Err --handler--> handler_label_id. Returns {ok, ir} or {ok: False, error}."""
    try:
        ir = copy.deepcopy(ir)
    except Exception as e:
        return {"ok": False, "error": {"code": "ERR_COPY", "message": str(e), "details": []}}
    body = (ir.get("labels") or {}).get(label_id)
    if not body:
        return {"ok": False, "error": {"code": "ERR_LABEL", "message": f"label {label_id!r} not found", "details": [label_id]}}
    nodes = list(body.get("nodes") or [])
    edges = list(body.get("edges") or [])
    node_by_id = {n.get("id"): n for n in nodes if n.get("id")}
    if from_node_id not in node_by_id:
        return {"ok": False, "error": {"code": "ERR_FROM", "message": f"from node {from_node_id!r} not found", "details": [from_node_id]}}
    max_n = max((int(n["id"][1:]) for n in nodes if n.get("id") and n["id"].startswith("n") and n["id"][1:].isdigit()), default=0)
    err_nid = f"n{max_n + 1}"
    err_node = {
        "id": err_nid,
        "op": "Err",
        "effect": "meta",
        "reads": [],
        "writes": [],
        "lineno": None,
        "data": {"op": "Err", "handler": handler_label_id},
    }
    nodes.append(err_node)
    edges.append({"from": from_node_id, "to": err_nid, "to_kind": "node", "port": "err"})
    edges.append({"from": err_nid, "to": handler_label_id, "to_kind": "label", "port": "handler"})
    body["nodes"] = nodes
    body["edges"] = edges
    ir = normalize_graph(ir)
    ir = annotate_ir_effect_analysis(ir)
    errs = _validate_after_patch(ir, strict=True)
    if errs:
        return {"ok": False, "error": {"code": "PATCH_VALIDATE", "message": "validation failed after attach_err_handler", "details": errs}}
    return {"ok": True, "ir": ir}
