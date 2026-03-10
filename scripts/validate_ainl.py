#!/usr/bin/env python3
"""
AINL Validator / REPL: compile .lang from file or stdin, print IR or errors.
Usage:
  python scripts/validate_ainl.py [file.lang]
  python scripts/validate_ainl.py --emit server [file.lang]
  echo "S core web /api" | python scripts/validate_ainl.py
"""
import argparse
import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from compiler_v2 import AICodeCompiler


def compile_and_validate(code: str, *, strict: bool = False, strict_reachability: bool = False):
    c = AICodeCompiler(strict_mode=strict, strict_reachability=strict_reachability)
    try:
        ir = c.compile(code, emit_graph=True)
        if ir.get("errors"):
            return {"ok": False, "errors": ir.get("errors", []), "ir": ir}
        return {"ok": True, "ir": ir}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def main():
    ap = argparse.ArgumentParser(description="Validate AINL and optionally emit artifacts")
    ap.add_argument("file", nargs="?", help="Path to .lang file (default: stdin)")
    ap.add_argument("--emit", choices=["ir", "server", "react", "openapi", "prisma", "sql"], default="ir",
                    help="Emit this artifact instead of IR JSON")
    ap.add_argument(
        "--lint-canonical",
        action="store_true",
        help="Print warning-only canonical-lint diagnostics to stderr without failing the compile",
    )
    ap.add_argument("--no-json", action="store_true", help="Print IR as Python repr (for debugging)")
    ap.add_argument("--strict", action="store_true", help="Enable strict compiler validation")
    ap.add_argument(
        "--strict-reachability",
        action="store_true",
        help="Enable strict reachability checks (implies --strict)",
    )
    args = ap.parse_args()

    if args.file:
        with open(args.file) as f:
            code = f.read()
    else:
        code = sys.stdin.read()

    strict = bool(args.strict or args.strict_reachability)
    result = compile_and_validate(code, strict=strict, strict_reachability=bool(args.strict_reachability))
    if not result["ok"]:
        if "errors" in result:
            for err in result["errors"]:
                print(err, file=sys.stderr)
        else:
            print(result["error"], file=sys.stderr)
        sys.exit(1)

    ir = result["ir"]

    if args.lint_canonical:
        warning_diags = [
            d for d in (ir.get("diagnostics") or [])
            if isinstance(d, dict) and d.get("severity") == "warning"
        ]
        for diag in warning_diags:
            code = diag.get("code") or "AINL_COMPILE_WARNING"
            lineno = diag.get("lineno")
            prefix = f"Line {lineno}: " if isinstance(lineno, int) else ""
            print(f"{prefix}{code}: {diag.get('message', '')}", file=sys.stderr)

    if args.emit == "ir":
        if args.no_json:
            print(ir)
        else:
            # JSON-serializable
            def to_jsonable(obj):
                if isinstance(obj, dict):
                    return {k: to_jsonable(v) for k, v in obj.items()}
                if isinstance(obj, (list, tuple)):
                    return [to_jsonable(x) for x in obj]
                return obj
            print(json.dumps(to_jsonable(ir), indent=2))
        return

    c = AICodeCompiler()
    if args.emit == "server":
        print(c.emit_server(ir))
    elif args.emit == "react":
        print(c.emit_react(ir))
    elif args.emit == "openapi":
        print(c.emit_openapi(ir))
    elif args.emit == "prisma":
        print(c.emit_prisma_schema(ir))
    elif args.emit == "sql":
        print(c.emit_sql_migrations(ir, dialect="postgres"))
    sys.exit(0)


if __name__ == "__main__":
    main()
