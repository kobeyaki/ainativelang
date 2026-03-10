"""
Non-authoritative sampling priors for constrained decoding.

This module intentionally contains decoder UX hints only.
Formal admissibility remains in `compiler_grammar.py`.
"""

from typing import Dict, Optional, Protocol, Sequence, Set

from compiler_v2 import (
    GRAMMAR_CLASS_ARROW_CONT,
    GRAMMAR_CLASS_LABEL_ARROW_CONT,
    GRAMMAR_CLASS_LABEL_DECL,
    GRAMMAR_CLASS_LINE_STARTER,
    GRAMMAR_CLASS_MODULE_OP,
    GRAMMAR_CLASS_NEWLINE,
    GRAMMAR_CLASS_QUOTE_CLOSE,
    MODULE_ALIASES,
    OP_REGISTRY,
)

METHODS = {"G", "P", "U", "D"}
TOP_LEVEL_OPS = {op for op, spec in OP_REGISTRY.items() if op != "L:" and spec.get("scope") in ("top", "any")}
ACTIVE_LABEL_LINE_STARTERS = {op for op, spec in OP_REGISTRY.items() if op != "L:" and spec.get("scope") in ("label", "any")}

TOKEN_CLASS_PRIOR_SAMPLES: Dict[str, Set[str]] = {
    "SERVICE_NAME": {"core", "fe", "api", "svc"},
    "SERVICE_MODE": {"web", "api"},
    "PATH": {"/", "/api", "/v1", "/users", "/products", "/orders", "/health", "/ready"},
    "METHOD": METHODS,
    "LABEL_REF": {"->L1", "->L2", "->L3", "->L4"},
    "OUT_VAR": {"->data", "->res", "->users", "->products", "->orders", "->rows", "->resp", "->ok"},
    "VAR_NAME": {"data", "res", "ok", "name", "id", "status"},
    "FREE_ARG": {"*", "id", "name", "status", "/users", "/orders", "payload", "data"},
    "DESC_TOKEN": {"desc", "summary", "list", "details", "response"},
    "TYPE_REF": {"I", "i", "F", "S", "s", "B", "D", "J", "A[User]", "E[Status]", "User"},
    "ENTITY_NAME": {"User", "Product", "Order", "Task", "Event", "Invoice"},
    "FIELD_TYPE": {"id:I", "name:S", "status:S", "created:D", "payload:J"},
    "COND": {"cond", "ok", "allow", "empty"},
    "UI_NAME": {"Dashboard", "ProductList", "OrderTable", "UserList", "Form", "Detail"},
    "ADAPTER_OP": {"db.F", "http.G", "http.P", "sqlite.query", "sqlite.exec", "fs.read", "fs.write", "queue.pop"},
    "TARGET": {"User", "Product", "Order", "*", "/users", "/orders", "payload", "data"},
}


class LexStateProtocol(Protocol):
    partial_module_prefix: bool
    token_in_progress: str
    tokens: Sequence[str]


class PrefixStateProtocol(Protocol):
    lex: LexStateProtocol
    in_label_scope: bool
    current_op: Optional[str]
    slots: Sequence[str]


def sample_tokens_for_classes(classes: Set[str]) -> Set[str]:
    out: Set[str] = set()
    for cls in classes:
        if cls == GRAMMAR_CLASS_NEWLINE:
            out.add("\n")
        elif cls == GRAMMAR_CLASS_QUOTE_CLOSE:
            out.add('"')
        elif cls == GRAMMAR_CLASS_ARROW_CONT:
            out.add(">")
        elif cls == GRAMMAR_CLASS_LABEL_ARROW_CONT:
            out.add("L")
        elif cls == GRAMMAR_CLASS_LABEL_DECL:
            out |= {"L1:", "L2:", "L12:"}
        elif cls == GRAMMAR_CLASS_MODULE_OP:
            out |= set(MODULE_ALIASES.values())
        elif cls == GRAMMAR_CLASS_LINE_STARTER:
            out |= TOP_LEVEL_OPS | ACTIVE_LABEL_LINE_STARTERS | {"L"}
        elif cls in TOKEN_CLASS_PRIOR_SAMPLES:
            out |= TOKEN_CLASS_PRIOR_SAMPLES[cls]
    return out


def default_prior_candidates_from_state(state: PrefixStateProtocol, classes: Set[str]) -> Set[str]:
    """
    Build non-authoritative prior candidates from formal state/classes.
    This function does not parse prefixes or apply formal pruning.
    """
    lex = state.lex
    cands = sample_tokens_for_classes(classes)

    if lex.partial_module_prefix:
        all_ops = set(TOP_LEVEL_OPS) | set(ACTIVE_LABEL_LINE_STARTERS) | set(MODULE_ALIASES.keys()) | set(MODULE_ALIASES.values())
        cands |= {op for op in all_ops if op.startswith(lex.token_in_progress)}
    if not cands:
        cands = {"\n"} if not state.in_label_scope else {"\n", "R", "J", "If", "X", "Err", "Retry", "Call", "Set"}

    # Small-model priors layered on top.
    if not lex.tokens:
        cands |= {"S", "D", "E", "L", "U"} if not state.in_label_scope else {"R", "J", "If", "X"}
    elif (state.current_op or "") == "E":
        if len(state.slots) == 0:
            cands |= {"/users", "/products", "/orders"}
        if len(state.slots) == 3:
            cands |= {"->data", "->users", "->products"}
    elif (state.current_op or "") == "D" and len(state.slots) == 0:
        cands |= {"User", "Product", "Order"}
    elif (state.current_op or "") == "U" and len(state.slots) == 0:
        cands |= {"Dashboard", "ProductList", "OrderTable"}

    return cands
