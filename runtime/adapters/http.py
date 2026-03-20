from __future__ import annotations

import json
import socket
import ssl
import time
from typing import Any, Dict, Iterable, List, Optional
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from runtime.adapters.base import AdapterError, HttpAdapter

# Build a default SSL context that uses certifi's CA bundle when available.
# This fixes macOS environments where the system cert store isn't linked.
def _default_ssl_context() -> ssl.SSLContext:
    try:
        import certifi
        return ssl.create_default_context(cafile=certifi.where())
    except ImportError:
        return ssl.create_default_context()


class SimpleHttpAdapter(HttpAdapter):
    def __init__(
        self,
        *,
        default_timeout_s: float = 5.0,
        max_response_bytes: int = 1_000_000,
        allow_hosts: Optional[Iterable[str]] = None,
    ):
        self.default_timeout_s = float(default_timeout_s)
        self.max_response_bytes = int(max_response_bytes)
        self.allow_hosts = set(allow_hosts or [])

    def _validate_url(self, url: str) -> None:
        parsed = urlparse(url)
        if parsed.scheme not in ("http", "https"):
            raise AdapterError("http adapter requires http/https url")
        if not parsed.netloc:
            raise AdapterError("http adapter url missing host")
        if self.allow_hosts and parsed.hostname not in self.allow_hosts:
            raise AdapterError(f"http host blocked by allowlist: {parsed.hostname}")

    def _parse_response_body(self, headers: Dict[str, str], body: bytes) -> Any:
        ctype = (headers.get("content-type") or "").lower()
        if "application/json" in ctype:
            try:
                return json.loads(body.decode("utf-8"))
            except Exception:
                return body.decode("utf-8", errors="replace")
        return body.decode("utf-8", errors="replace")

    def call(self, target: str, args: List[Any], context: Dict[str, Any]) -> Any:
        method = str(target or "").strip().upper()
        if method not in {"GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"}:
            raise AdapterError(f"unsupported http method: {method}")
        if not args:
            raise AdapterError("http adapter missing url argument")

        url = str(args[0])
        self._validate_url(url)

        body_obj: Any = None
        headers: Dict[str, str] = {}
        timeout_s: float = self.default_timeout_s

        if method in {"POST", "PUT", "PATCH"}:
            body_obj = args[1] if len(args) > 1 else None
            if len(args) > 2 and isinstance(args[2], dict):
                headers = {str(k): str(v) for k, v in args[2].items()}
            if len(args) > 3:
                timeout_s = float(args[3])
        else:
            if len(args) > 1 and isinstance(args[1], dict):
                headers = {str(k): str(v) for k, v in args[1].items()}
            if len(args) > 2:
                timeout_s = float(args[2])

        data: Optional[bytes] = None
        if body_obj is not None and method in {"POST", "PUT", "PATCH"}:
            if isinstance(body_obj, (dict, list)):
                data = json.dumps(body_obj, ensure_ascii=False).encode("utf-8")
                headers.setdefault("Content-Type", "application/json")
            elif isinstance(body_obj, bytes):
                data = body_obj
            else:
                data = str(body_obj).encode("utf-8")
                headers.setdefault("Content-Type", "text/plain; charset=utf-8")

        req = Request(url=url, data=data, headers=headers, method=method)

        max_attempts = 3
        base_backoff_s = 0.1
        attempt = 0

        while attempt < max_attempts:
            try:
                with urlopen(req, timeout=timeout_s, context=_default_ssl_context()) as resp:
                    status = int(getattr(resp, "status", 200))
                    resp_headers = {k.lower(): v for k, v in dict(resp.headers).items()}
                    body = resp.read(self.max_response_bytes + 1)
                    if len(body) > self.max_response_bytes:
                        raise AdapterError("http response too large")
                    parsed_body = self._parse_response_body(resp_headers, body)
                    # Normalized monitoring envelope (additive; keeps legacy 'status' field for compatibility).
                    return {
                        "ok": 200 <= status < 300,
                        "status": status,
                        "status_code": status,
                        "error": None,
                        "body": parsed_body,
                        "headers": resp_headers,
                        "url": url,
                    }
            except HTTPError as e:
                status = getattr(e, "code", None)
                # Retry only on 5xx once or twice, not on 4xx client errors.
                if status is not None and 500 <= status < 600 and attempt < max_attempts - 1:
                    attempt += 1
                    time.sleep(base_backoff_s * (2 ** (attempt - 1)))
                    continue
                raise AdapterError(f"http status error: {e.code}") from e
            except (URLError, socket.timeout, TimeoutError) as e:
                if attempt < max_attempts - 1:
                    attempt += 1
                    time.sleep(base_backoff_s * (2 ** (attempt - 1)))
                    continue
                raise AdapterError(f"http transport error: {e}") from e
