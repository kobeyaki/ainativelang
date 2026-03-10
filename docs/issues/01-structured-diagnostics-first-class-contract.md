# Title

Promote compiler structured diagnostics to first-class default contract

## Problem

Compiler diagnostics are partially structured and partially legacy-message-derived. This leaves language-server and tooling code with fallback heuristics that should become rare.

## Why It Matters

- Reduces diagnostic-location drift between compiler and editor integrations.
- Improves reliability for external contributors and downstream tooling.
- Lowers maintenance burden by reducing regex/message parsing paths.

## Acceptance Criteria

- Compiler emits structured diagnostics for the primary strict/conformance failure families by default.
- Structured fields include at least: severity, message, and one of `(span, lineno, label_id+node_id)`.
- Existing language-server/tests continue to pass with structured diagnostics preferred over fallback.
- Docs updated where diagnostic contract expectations are described.

## Non-Goals

- Redesigning language semantics.
- Removing all fallback logic in one step.
- UI redesign for editor diagnostics.
