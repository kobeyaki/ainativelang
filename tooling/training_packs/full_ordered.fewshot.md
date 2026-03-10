# Canonical Full Ordered Pack

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

## 5. `examples/retry_error_resilience.ainl`
- Primary: `retry_error`
- Secondary: `failure_fallback`

```ainl
L1:
  R ext.OP "unstable_task" ->resp
  Retry @n1 2 0
  Err @n1 ->L_fail
  J resp
L_fail:
  Set out "failed_after_retries"
  J out
```

## 6. `examples/web/basic_web_api.ainl`
- Primary: `web_endpoint`
- Secondary: `db_read`

```ainl
S core web /api
E /users G ->L_users ->users

L_users:
  R db.F User * ->users
  J users
```

## 7. `examples/webhook_automation.ainl`
- Primary: `webhook_automation`
- Secondary: `validate_act_return`

```ainl
L1:
  Set is_valid true
  R http.POST "https://example.com/automation" "event_webhook" ->resp
  If is_valid ->L2 ->L3
L2:
  Set out "accepted"
  J out
L3:
  Set out "ignored"
  J out
```

## 8. `examples/scraper/basic_scraper.ainl`
- Primary: `scraper_cron`
- Secondary: `http_to_storage`

```ainl
S core cron
Sc products "https://example.com/products" title=.product-title price=.product-price
Cr L_scrape "0 * * * *"   # hourly

L_scrape:
  R http.GET "https://example.com/products" ->resp
  R db.C Product * ->stored
  J stored
```

## 9. `examples/monitor_escalation.ainl`
- Primary: `monitoring_escalation`
- Secondary: `scheduled_branch`

```ainl
S core cron
Cr L_tick "*/5 * * * *"

L_tick:
  R core.MAX 7 3 ->metric
  If metric ->L_escalate ->L_noop
L_escalate:
  Set out "escalate"
  J out
L_noop:
  Set out "noop"
  J out
```
