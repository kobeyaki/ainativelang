#!/usr/bin/env python3
"""
Minimal end-to-end viability checks for generated AINL:
1) strict compile
2) emit server + ir.json
3) boot emitted server in temp dir
4) check /api/health
5) check one declared endpoint
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import socket
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Dict, List, Tuple

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from compiler_v2 import AICodeCompiler
from scripts.compat_gate import check_compat_gate
from scripts.contracts_gate import check_contracts
from scripts.policy_gate import check_policy_gate


def _iter_eps(eps: Dict[str, Any]) -> List[Tuple[str, str, Dict[str, Any]]]:
    out: List[Tuple[str, str, Dict[str, Any]]] = []
    for path, val in (eps or {}).items():
        if not isinstance(val, dict):
            continue
        if "label_id" in val or "method" in val:
            out.append((path, val.get("method", "G"), val))
        else:
            for method, ep in val.items():
                if isinstance(ep, dict):
                    out.append((path, method, ep))
    return out


def _http_method_upper(m: str) -> str:
    mm = (m or "G").upper()
    return {"G": "GET", "P": "POST", "U": "PUT", "D": "DELETE", "L": "GET"}.get(mm, mm)


def _free_port() -> int:
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    p = s.getsockname()[1]
    s.close()
    return p


def _http_json(url: str, method: str = "GET", timeout_s: float = 2.0) -> Tuple[int, Any]:
    req = urllib.request.Request(url=url, method=method)
    with urllib.request.urlopen(req, timeout=timeout_s) as resp:
        body = resp.read().decode("utf-8", errors="replace")
        try:
            return resp.status, json.loads(body)
        except Exception:
            return resp.status, body


def evaluate_viability(code: str, timeout_s: float = 20.0, base_ir: Dict[str, Any] | None = None) -> Dict[str, Any]:
    c = AICodeCompiler(strict_mode=True)
    try:
        ir = c.compile(code)
    except Exception as e:
        return {"ok": False, "stage": "compile_exception", "error": str(e)}
    if ir.get("errors"):
        return {"ok": False, "stage": "compile_strict", "errors": ir.get("errors", [])}
    contracts = check_contracts(ir)
    if not contracts.get("ok"):
        return {"ok": False, "stage": "contracts_gate", "contracts": contracts}
    policy = check_policy_gate(ir)
    if not policy.get("ok"):
        return {"ok": False, "stage": "policy_gate", "policy": policy}
    compat = check_compat_gate(base_ir, ir, mode=(ir.get("compat") or "add")) if base_ir else {"ok": True, "mode": "add", "breaks": [], "notes": []}
    if not compat.get("ok"):
        return {"ok": False, "stage": "compat_gate", "compat": compat}

    core = ir.get("services", {}).get("core", {})
    eps = _iter_eps(core.get("eps", {}))

    with tempfile.TemporaryDirectory(prefix="ainl_viability_") as td:
        tmp = Path(td)
        (tmp / "server.py").write_text(c.emit_server(ir), encoding="utf-8")
        (tmp / "ir.json").write_text(c.emit_ir_json(ir), encoding="utf-8")
        # runtime package + adapters are required by emitted server
        root = Path(__file__).resolve().parent.parent
        rt_src = root / "runtime"
        rt_dst = tmp / "runtime"
        if rt_dst.exists():
            shutil.rmtree(rt_dst)
        shutil.copytree(rt_src, rt_dst)
        ad_src = root / "adapters"
        ad_dst = tmp / "adapters"
        if ad_dst.exists():
            shutil.rmtree(ad_dst)
        shutil.copytree(ad_src, ad_dst)
        (tmp / "static").mkdir(exist_ok=True)
        (tmp / "static" / "index.html").write_text("<html><body>ok</body></html>", encoding="utf-8")

        port = _free_port()
        env = os.environ.copy()
        env["PORT"] = str(port)
        proc = subprocess.Popen(
            [sys.executable, str(tmp / "server.py")],
            cwd=str(tmp),
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        try:
            start = time.time()
            health_ok = False
            health_url = f"http://127.0.0.1:{port}/api/health"
            while time.time() - start < timeout_s:
                if proc.poll() is not None:
                    err = proc.stderr.read() if proc.stderr else ""
                    return {"ok": False, "stage": "server_boot", "error": err.strip() or "server exited"}
                try:
                    st, body = _http_json(health_url, method="GET", timeout_s=1.5)
                    if st == 200:
                        health_ok = True
                        break
                except Exception:
                    time.sleep(0.25)
            if not health_ok:
                return {"ok": False, "stage": "health_timeout", "error": "health endpoint not ready in time"}

            endpoint_check = {"checked": False}
            if eps:
                path, method, _ep = eps[0]
                m = _http_method_upper(method)
                url = f"http://127.0.0.1:{port}{core.get('path','/api')}{path}"
                try:
                    st, body = _http_json(url, method=m, timeout_s=3.0)
                    envelope_ok = isinstance(body, dict) and "data" in body
                    endpoint_check = {
                        "checked": True,
                        "url": url,
                        "method": m,
                        "status": st,
                        "body_type": type(body).__name__,
                        "envelope_ok": envelope_ok,
                    }
                    if st >= 400:
                        return {"ok": False, "stage": "endpoint_check", "endpoint": endpoint_check}
                    if not envelope_ok:
                        return {"ok": False, "stage": "endpoint_shape", "endpoint": endpoint_check}
                except urllib.error.HTTPError as e:
                    endpoint_check = {"checked": True, "url": url, "method": m, "status": e.code}
                    return {"ok": False, "stage": "endpoint_check", "endpoint": endpoint_check}
                except Exception as e:
                    endpoint_check = {"checked": True, "url": url, "method": m, "error": str(e)}
                    return {"ok": False, "stage": "endpoint_check", "endpoint": endpoint_check}

            return {
                "ok": True,
                "stage": "done",
                "health_url": health_url,
                "endpoint": endpoint_check,
                "contracts": contracts,
                "policy": policy,
                "compat": compat,
            }
        finally:
            if proc.poll() is None:
                proc.terminate()
                try:
                    proc.wait(timeout=3)
                except Exception:
                    proc.kill()


def main() -> None:
    ap = argparse.ArgumentParser(description="Run minimal end-to-end AINL viability checks")
    ap.add_argument("file", help="Path to .lang file")
    ap.add_argument("--timeout", type=float, default=20.0, help="Max seconds for server boot+checks")
    args = ap.parse_args()
    with open(args.file, "r", encoding="utf-8") as f:
        code = f.read()
    res = evaluate_viability(code=code, timeout_s=args.timeout)
    print(json.dumps(res, indent=2))
    raise SystemExit(0 if res.get("ok") else 1)


if __name__ == "__main__":
    main()
