# OpenClaw Adapter Quick Reference

This document provides a concise, model-friendly reference for using OpenClaw capabilities from AINL programs.

## Email (mail)

Check unread emails:
```
R mail check ->emails
```
Returns: `[ {id, from, subject, body, ts} ]`

Configuration: none needed; uses OpenClaw's configured mailbox.

## Calendar (calendar)

Fetch upcoming events:
```
R calendar get ->events
```
Returns: `[ {id, title, start, end, location} ]`

Optional filters (future): `calendar get --limit 10 --start ISO --end ISO`

## Social / Web Search (social)

Search for mentions:
```
R social G ->mentions
```
Returns: `[ {id, text, ts} ]`

Configuration: respects `SOCIAL_MONITOR_QUERY` env var (default: "Steven Hooley"). Edit in environment if needed.

## CRM Leads (db)

Fetch all leads:
```
R db F ->leads
```
Returns: `[ lead objects with fields: id, name, city, state, phone, email, website, vertical, service, rating, reviews, websiteAge, voiceSystem, priority, etc. ]`

Configuration: `LEADS_CSV` env var points to `workspace/leads/lead_output.csv` by default.

## Service Status (svc)

Check if infrastructure services are up:
```
X caddy_up (svc caddy)
X cloud_up (svc cloudflared)
X maddy_up (svc maddy)
```
Returns: `"up"` or `"down"` for each.

Logic: Caddy checks ports 80/443; others check process by name.

## Notification Queue (queue)

Send a notification to self:
```
R queue.Put "notify" { "email_count": 5, "cal_count": 3, "ts": now } ->status
```
`status` is `"sent"` if OpenClaw messaging worked, `"logged"` if fallback, `"error"` on failure.

Payload is free-form; the monitor system uses specific fields. For custom notifications, any JSON is accepted.

## Cache (cache)

Persistent key-value store:
```
R cache get "state" "last_run" ->last
R cache set "state" "last_run" now
```
Storage: `MONITOR_CACHE_JSON` env var, default `/tmp/monitor_state.json`.

Namespaces help organize keys. Values are any JSON-serializable AINL value.

## Tips for Models

- All OpenClaw adapters are read-only except `queue.Put` (writes to your own inbox) and `cache.set` (local disk).
- They do not require network access; they call the `openclaw` binary via subprocess. Ensure `OPENCLAW_BIN` is set or the binary is in PATH.
- Errors are caught and logged; most adapters return empty lists or default values on failure rather than raising. Check return values if critical.
- For the monitor system, the adapter registry `openclaw_monitor_registry` is pre-built. To use these adapters in your own AINL program, import and register that registry in the emitted server.

## Example: Simple Alert

```
S core cron "*/10 * * * *"
D Config threshold 5

L0: R email check ->emails
   X count (len emails)
   If (core.gt count Config.threshold) ->L1 ->L2
L1: R queue.Put "notify" { "email_count": count, "ts": (core.now) }
L2: J done
```

This checks email every 10 minutes and notifies if more than 5 unread.
