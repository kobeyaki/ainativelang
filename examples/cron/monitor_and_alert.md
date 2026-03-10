# Example: Monitor and Alert

This program runs every 5 minutes, checks metrics, and posts an alert when needed.

```text
S core cron
Cr L_monitor "*/5 * * * *"   # every 5 minutes

L_monitor:
  R db.F Metric * ->metrics
  If metrics ->L_alert ->L_ok

L_alert:
  R http.Post "https://hook.example.com/alert" metrics ->ack
  J ack

L_ok:
  J metrics
```

### Explanation

- `Cr L_monitor "*/5 * * * *"` schedules the `L_monitor` label.
- In `L_monitor`:
  - `R db.F Metric * ->metrics` reads all metrics.
  - `If metrics ->L_alert ->L_ok` branches on whether `metrics` is non‑empty.
- `L_alert` posts an alert webhook with `metrics` as the payload, then returns the acknowledgment.
- `L_ok` simply returns `metrics` (for logging or introspection).

This pattern demonstrates **monitor → condition → alert** using only the v0.9 core ops.

