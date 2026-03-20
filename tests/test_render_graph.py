from scripts import render_graph


def test_render_dot_minimal_ir():
  ir = {
      "labels": {
          "1": {
              "nodes": [
                  {
                      "id": "n1",
                      "op": "R",
                      "data": {"adapter": "http.Get"},
                  },
                  {
                      "id": "n2",
                      "op": "J",
                      "data": {},
                  },
              ],
              "edges": [
                  {
                      "from": "n1",
                      "to": "n2",
                      "to_kind": "node",
                      "port": "next",
                  }
              ],
          }
      }
  }

  dot = render_graph._render_dot(ir, name="test_graph")

  assert "digraph test_graph" in dot
  # Nodes are grouped under cluster_1
  assert "subgraph cluster_1" in dot
  # Node labels include op and adapter prefix
  assert '"L1_n1" [label="R (http)"];' in dot
  assert '"L1_n2" [label="J"];' in dot
  # Edge includes the port label
  assert '"L1_n1" -> "L1_n2" [label="next"];' in dot
