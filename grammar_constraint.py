"""
Thin backward-compatible adapter over compiler-owned formal prefix grammar.

Formal admissibility and prefix viability live in `compiler_grammar.py`.
Small-model priors are provided there and exposed through this module for
historical API compatibility.
"""

from typing import Iterable, Set

from compiler_grammar import (
    admissible_token_classes,
    compiler_prefix_completable,
    filter_admissible_candidates,
    formal_next_token_classes,
    is_prefix_anti_drift_clean,
    is_structurally_plausible_prefix,
    parse_prefix_state,
)
from grammar_priors import default_prior_candidates_from_state, sample_tokens_for_classes


def next_token_priors(prefix: str) -> Set[str]:
    state = parse_prefix_state(prefix)
    classes = admissible_token_classes(state)
    raw = default_prior_candidates_from_state(state, classes)
    return filter_admissible_candidates(prefix, raw)


def next_token_mask(prefix: str, raw_candidates: Iterable[str]) -> Set[str]:
    return filter_admissible_candidates(prefix, raw_candidates)


def next_valid_tokens(prefix: str) -> Set[str]:
    """Backward-compatible alias for curated compiler-pruned priors."""
    return next_token_priors(prefix)


def is_valid_ainl_prefix(prefix: str) -> bool:
    """
    Backward-compatible coarse check. Uses formal prefix state.
    """
    st = parse_prefix_state(prefix)
    if not st.lex.line.strip():
        return True
    if not st.lex.tokens:
        return True
    return st.current_op is not None


def is_structurally_plausible_ainl_prefix(prefix: str) -> bool:
    return is_structurally_plausible_prefix(prefix)


def is_valid_ainl_prefix_strict(prefix: str) -> bool:
    """Historical name kept for compatibility; see structural alias above."""
    return is_structurally_plausible_ainl_prefix(prefix)


__all__ = [
    "next_valid_tokens",
    "next_token_priors",
    "next_token_mask",
    "formal_next_token_classes",
    "sample_tokens_for_classes",
    "is_valid_ainl_prefix",
    "is_valid_ainl_prefix_strict",
    "is_structurally_plausible_ainl_prefix",
    "is_prefix_anti_drift_clean",
    "compiler_prefix_completable",
]
