# Integration examples

## HTTP external executor bridge

- **Program:** [`executor_bridge_min.ainl`](executor_bridge_min.ainl) — posts the [EXTERNAL_EXECUTOR_BRIDGE](../../docs/integrations/EXTERNAL_EXECUTOR_BRIDGE.md) JSON envelope via `http.Post`.
- **MCP-first:** For OpenClaw / NemoClaw agents, use **`ainl-mcp`**, not this pattern.

### Try it locally

1. Start the mock bridge (stdlib only):

   ```bash
   python3 scripts/mock_executor_bridge.py
   ```

2. In another terminal:

   ```bash
   ainl run examples/integrations/executor_bridge_min.ainl --enable-adapter http
   ```

3. Expect `result` **`bridge_ok`** when the mock returns HTTP 200 (`status` field in the program frame).

Point the `http.Post` URL at your own gateway when moving beyond the mock.

**CI:** `./.venv-py310/bin/python -m pytest tests/test_executor_bridge_integration.py` (or activate your 3.10 venv) exercises this program against an in-process mock (no manual server).

## Optional `bridge` adapter (Phase 3)

- **Program:** [`executor_bridge_adapter_min.ainl`](executor_bridge_adapter_min.ainl) — `R bridge.Post demo.echo req ->resp` with URLs supplied only on the host.
- **CLI:** `ainl run examples/integrations/executor_bridge_adapter_min.ainl --enable-adapter bridge --bridge-endpoint demo.echo=http://127.0.0.1:17300/v1/execute` (after starting the mock).
- **Tests:** `./.venv-py310/bin/python -m pytest tests/test_executor_bridge_adapter.py` (or your activated 3.10 venv)
