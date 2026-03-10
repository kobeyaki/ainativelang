# OpenClaw Adapter Enhancement Plan

Current adapter (`openclaw_integration.py`) covers the monitor use case well but can be generalized for broader agent workflows.

## Goals

- Expose OpenClaw's capabilities as first-class AINL adapters.
- Keep adapter definitions simple and discoverable.
- Support both “pull” (check email) and “push” (send message) operations.
- Allow policy-based gating (e.g., only allow sending to self, only allow read-only ops).

## Proposed Adapter Namespace

| Adapter | Target | Args | Returns | Side effects |
|---------|--------|------|---------|--------------|
| **mail** | `check` | `--unread`, `--limit N`, `--json` | `[email]` | reads mailbox |
| | `send` | `to`, `subject`, `body` | `{ok, message_id}` | sends email |
| **calendar** | `get` | `--limit N`, `--start ISO`, `--end ISO`, `--json` | `[event]` | reads calendar |
| | `create**` | `title`, `start`, `end`, `location?` | `{id}` | creates event |
| **crm** | `leads.list` | `--limit N`, `--filter JSON` | `[lead]` | reads CRM |
| | `lead.get` | `lead_id` | `lead` | reads single |
| | `lead.update**` | `lead_id`, `fields JSON` | `{ok}` | updates lead |
| **message** | `send` | `to`, `text` | `{ok}` | sends Signal/Telegram/etc |
| **lead_ai** | `analyze` | `lead_id` | `{score, pitch, email}` | triggers Lead AI analysis (async polling) |
| **services** | `status` | `service_name` | `"up"`/`"down"` | checks tunnel/caddy/maddy |
| | `restart**` | `service_name` | `{ok}` | restarts service |

**Note:** Write operations marked with ** may be disabled by policy.

## Adapter Implementation Strategy

- Reuse the existing `_run_openclaw` subprocess pattern.
- Parse JSON output from OpenClaw CLI into native AINL values.
- For long-running ops (Lead AI analyze), return a task ID and provide `lead_ai.result task_id` to poll.
- Keep error handling consistent: return empty list or error object rather than raising; let AINL program decide.

## Configuration via Environment

```
OPENCLAW_BIN=/path/to/openclaw
OPENCLAW_ALLOW_SEND=false   # disable message.send
OPENCLAW_ALLOW_WRITE=false # disable any write operations
OPENCLAW_SEND_TO=self       # restrict send to self (monitor use)
```

## Registry Registration

In `openclaw_integration.py` add:

```python
class MailAdapter(RuntimeAdapter):
    def call(self, target, args, context):
        if target == 'check':
            # build openclaw mail check command with filters from args
            ...
        elif target == 'send':
            if not os.getenv('OPENCLAW_ALLOW_SEND'):
                raise AdapterError('send disabled by policy')
            ...
```

Then extend `openclaw_monitor_registry` to include `'mail'`, `'crm'`, `'message'`, `'lead_ai'` as needed.

## Benefits

- Models can write programs that directly interact with OpenClaw's ecosystem without leaving AINL.
- The monitor system becomes a special case of a general integration.
- Opens the door to “AINL-native” agent workflows: “Every day, check new leads, analyze with Lead AI, and send personalized outreach.”
