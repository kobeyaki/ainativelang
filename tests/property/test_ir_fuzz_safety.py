import os
import sys
from typing import Any, Dict, List

from hypothesis import given, settings, strategies as st

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from runtime.engine import RuntimeEngine


def _node_strategy():
    op = st.sampled_from(["Set", "J", "X", "If", "Err", "Unknown"])
    return st.fixed_dictionaries(
        {
            "id": st.from_regex(r"n[1-6]", fullmatch=True),
            "op": op,
            "data": st.dictionaries(
                keys=st.sampled_from(["op", "name", "ref", "var", "dst", "fn", "args", "cond", "then", "else", "handler"]),
                values=st.one_of(
                    st.none(),
                    st.integers(min_value=-3, max_value=3),
                    st.booleans(),
                    st.text(min_size=0, max_size=8),
                    st.lists(st.text(min_size=0, max_size=4), max_size=3),
                ),
                max_size=6,
            ),
        }
    )


def _edge_strategy() -> st.SearchStrategy[Dict[str, Any]]:
    return st.fixed_dictionaries(
        {
            "from": st.from_regex(r"n[1-6]", fullmatch=True),
            "to": st.one_of(st.from_regex(r"n[1-6]", fullmatch=True), st.just("2"), st.just("3")),
            "to_kind": st.sampled_from(["node", "label"]),
            "port": st.one_of(st.none(), st.sampled_from(["next", "then", "else", "err", "retry", "body", "after", "alt"])),
        }
    )


@settings(max_examples=80, deadline=None)
@given(
    nodes=st.lists(_node_strategy(), min_size=1, max_size=6),
    edges=st.lists(_edge_strategy(), min_size=0, max_size=10),
    use_fallback=st.booleans(),
)
def test_property_random_ir_runtime_safety(nodes: List[Dict[str, Any]], edges: List[Dict[str, Any]], use_fallback: bool):
    # Ensure at least one entry node id exists.
    entry = nodes[0]["id"]
    ir = {
        "labels": {
            "1": {
                "entry": entry,
                "nodes": nodes,
                "edges": edges,
                "legacy": {"steps": [{"op": "J", "var": "data"}]},
            },
            "2": {"legacy": {"steps": [{"op": "J", "var": "data"}]}},
            "3": {"legacy": {"steps": [{"op": "J", "var": "data"}]}},
        },
        "source": {"lines": []},
        "cst": {"lines": []},
    }
    eng = RuntimeEngine(ir=ir, trace=False, step_fallback=use_fallback)
    try:
        eng.run_label("1", {"data": 0})
    except Exception as e:
        # Runtime should fail in a controlled RuntimeError-family shape,
        # not with accidental structural exceptions like KeyError/AttributeError leaks.
        assert isinstance(e, RuntimeError)
