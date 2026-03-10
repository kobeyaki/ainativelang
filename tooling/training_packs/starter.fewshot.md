# Canonical Starter Pack

## 1. `examples/hello.ainl`
- Primary: `compute_return`
- Secondary: `none`

```ainl
L1:
  R core.ADD 2 3 ->x
  J x
```

## 2. `examples/crud_api.ainl`
- Primary: `if_branching`
- Secondary: `set_literals`

```ainl
L1: Set flag true If flag ->L2 ->L3
L2: Set out "ok" J out
L3: Set out "bad" J out
```

## 3. `examples/rag_pipeline.ainl`
- Primary: `call_return`
- Secondary: `label_modularity`

```ainl
L1: Call L9 ->out J out
L9:
  R core.ADD 40 2 ->v
  J v
```

## 4. `examples/if_call_workflow.ainl`
- Primary: `if_call_workflow`
- Secondary: `bound_call_result`

```ainl
L1:
  Call L8 ->has_payload
  If has_payload ->L2 ->L3
L8:
  Set v true
  J v
L2:
  Call L9 ->out
  J out
L3:
  Set out "missing_payload"
  J out
L9:
  R core.CONCAT "task_" "ready" ->res
  J res
```
