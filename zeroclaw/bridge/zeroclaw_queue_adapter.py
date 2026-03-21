"""Notify queue via ZeroClaw CLI (`zeroclaw message send`), parallel to OpenClaw NotificationQueueAdapter."""
from __future__ import annotations

import logging
import os
import subprocess
import time
from typing import Any, Dict, List

from runtime.adapters.base import RuntimeAdapter, AdapterError

logger = logging.getLogger(__name__)


def _zeroclaw_bin() -> str:
    return (os.getenv("ZEROCLAW_BIN") or "").strip() or "zeroclaw"


def _dry(context: Dict[str, Any]) -> bool:
    v = context.get("dry_run")
    if v in (True, 1, "1", "true", "True", "yes"):
        return True
    return os.environ.get("AINL_DRY_RUN", "").strip().lower() in ("1", "true", "yes")


class ZeroclawQueueAdapter(RuntimeAdapter):
    """Register as adapter name ``queue`` for ``R queue Put "notify" ...`` from bridge wrappers."""

    def call(self, target: str, args: List[Any], context: Dict[str, Any]) -> Any:
        if str(target or "").lower() != "put":
            raise AdapterError("queue only supports Put")
        if len(args) < 2:
            raise AdapterError("Queue.Put requires (queue, payload)")
        queue_name, payload = args[0], args[1]
        if queue_name != "notify":
            return None
        msg = self._format_message(payload)
        recipient = os.getenv("ZEROCLAW_TARGET", os.getenv("OPENCLAW_TARGET", "")).strip() or "unset-target"
        channel = os.getenv("ZEROCLAW_NOTIFY_CHANNEL", os.getenv("OPENCLAW_NOTIFY_CHANNEL", "telegram")).strip()
        if _dry(context):
            logger.info("[dry_run] zeroclaw_queue Put notify — no send")
            return "dry_run"
        logger.info("ZeroClaw queue sending %s to %s: %s", channel, recipient, msg[:120])
        try:
            subprocess.run(
                [
                    _zeroclaw_bin(),
                    "message",
                    "send",
                    "--channel",
                    channel,
                    "--target",
                    recipient,
                    "--message",
                    msg,
                ],
                check=True,
                timeout=30,
                capture_output=True,
                text=True,
            )
            return "sent"
        except FileNotFoundError:
            logger.warning("zeroclaw binary not found for messaging; printing to stdout")
            print(f"[ZeroClaw notify] {msg}")
            return "logged"
        except subprocess.CalledProcessError as e:
            logger.warning("zeroclaw message send failed: %s", e)
            print(f"[ZeroClaw notify] {msg}")
            return "logged"
        except Exception as e:
            logger.warning("zeroclaw notification adapter error: %s", e)
            return "error"

    def _format_message(self, payload: Any) -> str:
        if isinstance(payload, str):
            return payload
        if isinstance(payload, dict):
            if "text" in payload:
                return str(payload["text"])
            module = payload.get("module")
            ts = payload.get("ts")
            time_str = ""
            if ts:
                try:
                    time_str = time.strftime("%Y-%m-%d %H:%M", time.localtime(float(ts)))
                except Exception:
                    time_str = str(ts)
            if module:
                return str(payload.get("text") or f"{module} @ {time_str}")
            return str(payload)
        return str(payload)
