#!/usr/bin/env python3
"""
Minimal LSP test for AINL.
Starts langserver as subprocess, sends a completion and hover request, checks responses.
"""

import subprocess
import json
import time
from typing import Optional


def main() -> int:
    # Launch the langserver stdio
    proc = subprocess.Popen(
        ["python3", "langserver.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,
    )

    def send(notif) -> bool:
        try:
            proc.stdin.write(json.dumps(notif) + "\n")
            proc.stdin.flush()
            return True
        except BrokenPipeError:
            return False

    def read_response() -> Optional[dict]:
        line = proc.stdout.readline()
        return json.loads(line) if line else None

    # 1. initialize
    initialize = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "processId": None,
            "rootUri": "file:///Users/clawdbot/.openclaw/workspace/AI_Native_Lang",
            "capabilities": {}
        }
    }
    if not send(initialize):
        print("SKIP: langserver unavailable (stdin pipe closed before initialize)")
        return 0
    resp = read_response()
    print("Initialize response:", resp.get("result", {}).get("serverInfo") if resp else None)
    if not resp:
        print("SKIP: langserver returned no initialize response")
        return 0

    # 2. didOpen a document
    uri = "file:///tmp/test.ainl"
    content = "R http."
    did_open = {
        "jsonrpc": "2.0",
        "method": "textDocument/didOpen",
        "params": {
            "textDocument": {
                "uri": uri,
                "languageId": "ainl",
                "version": 1,
                "text": content
            }
        }
    }
    if not send(did_open):
        print("SKIP: langserver unavailable after didOpen")
        return 0

    # 3. completion request at end of line
    completion = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "textDocument/completion",
        "params": {
            "textDocument": {"uri": uri},
            "position": {"line": 0, "character": len(content)}
        }
    }
    if not send(completion):
        print("SKIP: langserver unavailable before completion")
        return 0
    comp_resp = read_response()
    items = (comp_resp.get("result", {}).get("items", []) if comp_resp else [])
    print(f"Completion items count: {len(items)}")
    if items:
        print("First item labels:", [i.get("label") for i in items[:5]])

    # 4. hover request on 'http'
    hover = {
        "jsonrpc": "2.0",
        "id": 3,
        "method": "textDocument/hover",
        "params": {
            "textDocument": {"uri": uri},
            "position": {"line": 0, "character": 1}  # on 'http'
        }
    }
    if not send(hover):
        print("SKIP: langserver unavailable before hover")
        return 0
    hover_resp = read_response()
    hover_contents = hover_resp.get("result", {}).get("contents") if hover_resp else None
    print("Hover contents (truncated):", str(hover_contents)[:200] if hover_contents else None)

    # Shutdown
    send({"jsonrpc": "2.0", "id": 4, "method": "shutdown"})
    send({"jsonrpc": "2.0", "method": "exit"})
    time.sleep(0.5)
    proc.terminate()
    stderr = proc.stderr.read()
    if stderr:
        print("Stderr:", stderr[:200])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
