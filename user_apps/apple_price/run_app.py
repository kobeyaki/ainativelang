#!/usr/bin/env python3
"""Standalone launcher for user_apps/apple_price without editing project files."""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

APP_DIR = Path(__file__).resolve().parent
ROOT = APP_DIR
for _ in range(6):
    if (ROOT / "runtime.py").exists() and (ROOT / "adapters").exists():
        break
    ROOT = ROOT.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from runtime import ExecutionEngine  # noqa: E402
from adapters import mock_registry  # noqa: E402


def _iter_eps(eps):
    out = []
    for path, val in eps.items():
        if not isinstance(val, dict):
            continue
        if "label_id" in val or "method" in val:
            out.append((path, val.get("method", "G"), val))
        else:
            for method, ep in val.items():
                if isinstance(ep, dict):
                    out.append((path, method, ep))
    return out


def _http_method_letter_to_name(m: str) -> str:
    return {"G": "get", "P": "post", "U": "put", "D": "delete", "L": "get"}.get((m or "G").upper(), "get")


def _ensure_static_index(static_dir: Path) -> None:
    static_dir.mkdir(exist_ok=True)
    idx = static_dir / "index.html"
    if idx.exists():
        return
    idx.write_text(
        """<!doctype html>
<html>
<head><meta charset="utf-8"/><meta name="viewport" content="width=device-width, initial-scale=1"/></head>
<body style="font-family: system-ui; margin: 2rem;">
  <h1>Apple Price</h1>
  <pre id="out">Loading...</pre>
  <script>
    fetch('/api/apple-price').then(r => r.json()).then(d => {
      document.getElementById('out').textContent = JSON.stringify(d, null, 2);
    }).catch(e => {
      document.getElementById('out').textContent = 'Error: ' + e.message;
    });
  </script>
</body>
</html>
""",
        encoding="utf-8",
    )


def main() -> None:
    ir_path = APP_DIR / "apple_price.ir.json"
    if not ir_path.exists():
        raise SystemExit("Missing apple_price.ir.json. Run: bash build_app.sh")
    with ir_path.open("r", encoding="utf-8") as f:
        ir = json.load(f)

    registry = mock_registry(ir.get("types"))
    engine = ExecutionEngine(ir, registry)

    app = FastAPI(title="Apple Price App")
    app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
    api = FastAPI()

    def _run_label(lid: str):
        r = engine.run(lid)
        return {"data": r if r is not None else []}

    core = ir.get("services", {}).get("core", {})
    for path, method, ep in _iter_eps(core.get("eps", {})):
        lid = str(ep.get("label_id", "")).lstrip("L")
        handler = (lambda label_id=lid: _run_label(label_id))
        getattr(api, _http_method_letter_to_name(method))(path)(handler)

    @api.get("/health")
    def health():
        return {"status": "ok"}

    app.mount("/api", api)
    static_dir = APP_DIR / "static"
    _ensure_static_index(static_dir)
    app.mount("/", StaticFiles(directory=str(static_dir), html=True), name="static")

    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=int(os.environ.get("PORT", "8765")))


if __name__ == "__main__":
    main()
