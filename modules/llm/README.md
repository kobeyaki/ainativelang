# `modules/llm`

Strict-safe **`.ainl` include** helpers for **LLM / chat-completion** shaped workflows (OpenAI-compatible APIs and similar).

Place `include` lines **before** any top-level `S` / `E` in the host program (same rule as [`modules/common/README.md`](../common/README.md)).

| File | Purpose |
|------|---------|
| **`json_array_system.ainl`** | Subgraph `ENTRY` → one string suitable for `messages[].role == "system"` when the assistant must emit **only a JSON array** (no markdown). Pair with a user message that specifies the array schema. |

Deployments that separate **LLM prose** from `.ainl` graphs typically keep **`.txt` prompt files** in a directory next to the gateway and point the gateway at that path via config or an env var (same idea as `PROMOTER_PROMPTS_DIR`).

**Consumers:** Any program under `demo/`, `examples/`, `intelligence/`, or apps that call `R bridge.POST` / `http.POST` to an LLM.

**Spec context:** [docs/language/AINL_CORE_AND_MODULES.md](../../docs/language/AINL_CORE_AND_MODULES.md) §8 (repository include libraries).
