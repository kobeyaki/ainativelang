"""Web server from AI-Native Lang: real runtime (R/P/Sc via adapters) + static + logging + rate limit."""
import json
import sys
import time
import uuid
import os
from pathlib import Path
from collections import defaultdict

# Allow importing runtime + adapters (same dir in Docker, else repo root)
_dir = Path(__file__).resolve().parent
_root = _dir
for _ in range(6):
    if (_root / 'runtime.py').exists() and (_root / 'adapters').exists():
        break
    _root = _root.parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import FileResponse

from runtime.engine import RuntimeEngine as ExecutionEngine
from adapters.mock import mock_registry

# Load IR (emitted with server); use real adapters by replacing mock_registry
_ir_path = Path(__file__).resolve().parent / "ir.json"
with open(_ir_path) as f:
    _ir = json.load(f)
_registry = mock_registry(_ir.get("types"))
_engine = ExecutionEngine(_ir, _registry)

_metrics = defaultdict(int)
_trace_enabled = False

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        req_id = str(uuid.uuid4())[:8]
        trace_id = req_id if _trace_enabled else None
        start = time.perf_counter()
        response = await call_next(request)
        duration_ms = (time.perf_counter() - start) * 1000
        # Never log Authorization or other secret headers (fix #11).
        log = {"request_id": req_id, "method": request.method, "path": request.url.path, "status": response.status_code, "duration_ms": round(duration_ms, 2)}
        if trace_id:
            log["trace_id"] = trace_id
        _metrics["requests_total"] += 1
        print(json.dumps(log))
        return response

class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, requests_per_minute: int = 0):
        super().__init__(app)
        self.rpm = requests_per_minute
        self.window_start = defaultdict(float)
        self.count = defaultdict(int)

    async def dispatch(self, request: Request, call_next):
        if self.rpm <= 0:
            return await call_next(request)
        client = request.client.host if request.client else "unknown"
        now = time.time()
        if now - self.window_start[client] > 60:
            self.window_start[client] = now
            self.count[client] = 0
        self.count[client] += 1
        if self.count[client] > self.rpm:
            from starlette.responses import JSONResponse
            return JSONResponse(status_code=429, content={"error": "rate limit exceeded"})
        return await call_next(request)

app = FastAPI(title="Lang Server")
_rate_limit = int(os.environ.get("RATE_LIMIT", "0"))
app.add_middleware(RateLimitMiddleware, requests_per_minute=_rate_limit)
app.add_middleware(LoggingMiddleware)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

def _run_label(lid, request: Request):
    ctx = {
        "_role": request.headers.get("X-Role"),
        "_auth_header": request.headers.get("Authorization") or request.headers.get("X-Auth"),
        "_auth_present": bool(request.headers.get("Authorization") or request.headers.get("X-Auth")),
    }
    r = _engine.run(lid, ctx)
    return {"data": r if r is not None else []}

api = FastAPI()

def _iter_eps(eps):
    out = []
    for path, val in eps.items():
        if not isinstance(val, dict): continue
        if "label_id" in val or "method" in val:
            out.append((path, val.get("method", "G"), val))
        else:
            for method, ep in val.items():
                if isinstance(ep, dict):
                    out.append((path, method, ep))
    return out

@api.get('/users')
def get_users(request: Request):
    return _run_label('1', request)

@api.get("/health")
def health():
    return {"status": "ok"}

@api.get("/ready")
def ready():
    return {"ready": True}

app.mount("/api", api)

# Static: serve index.html at / when present; else simple API-only landing
static_dir = Path(__file__).resolve().parent / "static"
static_dir.mkdir(exist_ok=True)
_index_html = static_dir / "index.html" if static_dir.exists() else None
if _index_html and _index_html.is_file():
    @app.get("/")
    def _serve_index():
        return FileResponse(_index_html)
else:
    @app.get("/")
    def _root():
        from starlette.responses import HTMLResponse
        return HTMLResponse("<html><body><h1>API</h1><p><a href=\"/api\">/api</a></p></body></html>")
if static_dir.exists():
    app.mount("/", StaticFiles(directory=str(static_dir), html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", "8765")))
