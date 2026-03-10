import argparse
import json
import sys
from pathlib import Path

from compiler_v2 import AICodeCompiler


def _render_dot(ir: dict, name: str | None = None) -> str:
  """Render a minimal DOT representation of the IR graph."""
  lines: list[str] = []
  graph_name = (name or "ainl_graph").replace("-", "_").replace(".", "_")
  lines.append(f"digraph {graph_name} {{")

  labels: dict = ir.get("labels", {})
  for label_id, label_body in labels.items():
    nodes = {n["id"]: n for n in label_body.get("nodes", [])}
    lines.append(f'  subgraph cluster_{label_id} {{')
    lines.append(f'    label="L{label_id}";')

    # Nodes
    for node_id, node in nodes.items():
      op = node.get("op", "?")
      data = node.get("data") or {}
      adapter = data.get("adapter") or ""
      # Short adapter prefix (e.g. "http" from "http.Get")
      adapter_prefix = adapter.split(".", 1)[0] if adapter else ""
      label_parts = [f"{op}"]
      if adapter_prefix:
        label_parts.append(f"({adapter_prefix})")
      label_str = " ".join(label_parts)
      node_name = f"L{label_id}_{node_id}"
      lines.append(f'    "{node_name}" [label="{label_str}"];')

    # Edges
    for edge in label_body.get("edges", []):
      src = edge.get("from")
      dst = edge.get("to")
      port = edge.get("port", "")
      if not src or not dst:
        continue
      src_name = f"L{label_id}_{src}"
      dst_name = f"L{label_id}_{dst}"
      if port:
        lines.append(f'    "{src_name}" -> "{dst_name}" [label="{port}"];')
      else:
        lines.append(f'    "{src_name}" -> "{dst_name}";')

    lines.append("  }")

  lines.append("}")
  return "\n".join(lines) + "\n"


def _load_ir_from_source(path: Path, strict: bool) -> dict:
  compiler = AICodeCompiler(strict_mode=strict)
  source = path.read_text(encoding="utf-8")
  return compiler.compile(source, emit_graph=True)


def _load_ir_from_json(path: Path) -> dict:
  with path.open("r", encoding="utf-8") as f:
    return json.load(f)


def main(argv: list[str] | None = None) -> int:
  parser = argparse.ArgumentParser(
      description=(
          "Render a minimal DOT graph from an AINL source file or IR JSON.\n\n"
          "Examples:\n"
          "  python scripts/render_graph.py examples/hello.ainl > hello.dot\n"
          "  dot -Tpng hello.dot -o hello.png\n"
      )
  )
  parser.add_argument("path", help="AINL source file (.ainl/.lang) or IR JSON file")
  parser.add_argument(
      "--from-ir",
      action="store_true",
      help="Treat input path as IR JSON instead of compiling source.",
  )
  parser.add_argument(
      "--strict",
      action="store_true",
      help="Compile in strict mode when reading AINL source.",
  )
  args = parser.parse_args(argv)

  path = Path(args.path)
  if not path.exists():
    print(f"error: path does not exist: {path}", file=sys.stderr)
    return 1

  if args.from_ir:
    ir = _load_ir_from_json(path)
  else:
    ir = _load_ir_from_source(path, strict=bool(args.strict))

  dot = _render_dot(ir, name=path.stem)
  sys.stdout.write(dot)
  return 0


if __name__ == "__main__":
  raise SystemExit(main())

