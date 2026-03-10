# Policy Validator for AINL Programs

## Purpose

Prevent AINL programs from performing unauthorized actions before they run. Useful for:
- Allowing users to write their own AINL programs while restricting dangerous adapters.
- Enforcing corporate policies (no outbound network, no file writes outside /tmp).
- Sandboxing untrusted code in multi-tenant environments.

## Policy File Format (YAML)

```yaml
version: 1
allow_adapters:
  - core
  - cache
  - sqlite
  - fs
deny_adapters:
  - http
  - queue
fs_sandbox: /tmp/ainl-sandbox
max_memory_mb: 100
max_cpu_seconds: 10
allowed_sqlite_tables:
  - metrics
  - logs
allowed_http_hosts:
  - api.internal.example.com
deny_http_hosts:
  - 169.254.169.254  # block metadata service
require_approval_for:
  - db.execute
  - fs.delete
```

## Validation Rules

1. **Adapter allow/deny list**  
   - If `allow_adapters` is non-empty, only those adapters may be used.
   - `deny_adapters` always applied as a block list.
   - Special adapter `*` matches all.

2. **Filesystem sandbox**  
   - All `fs.read`, `fs.write`, `fs.list`, `fs.delete` paths must be within `fs_sandbox`.
   - Reject paths containing `..` or symlinks that escape.

3. **SQLite table allowlist**  
   - If `allowed_sqlite_tables` set, every table reference in SQL must be in the list.
   - Checked via regex parse of SQL statements.

4. **HTTP host allow/deny**  
   - For `http.*` calls, extract the hostname from the URL.
   - Must pass `allowed_http_hosts` (if set) and not match `deny_http_hosts`.
   - Blocked by default if no allowlist provided? Policy should choose default-deny or allow-all.

5. **Operation approval**  
   - Certain high-risk targets (e.g., `fs.delete`, `sqlite.execute` with non-SELECT, `queue.Put`) require manual approval flag in the policy or an explicit `approved: true` annotation in the program (rare).

6. **Resource limits**  
   - Runtime should enforce `max_memory_mb` and `max_cpu_seconds`. The validator checks that the program declares resource limits reasonably (e.g., no infinite loops, bounded iterations).

## Implementation

Validator walks the compiled IR graph:

```python
def validate_ir(ir: Dict, policy: Dict) -> List[str]:
    errors = []
    for label in ir['labels']:
        for node in label['nodes']:
            adapter = node['adapter']
            target = node['target']
            args = node['args']
            # 1. adapter allow/deny
            if policy.get('allow_adapters') and adapter not in policy['allow_adapters']:
                errors.append(f"adapter '{adapter}' not allowed")
            if adapter in policy.get('deny_adapters', []):
                errors.append(f"adapter '{adapter}' explicitly denied")
            # 2. fs sandbox check
            if adapter == 'fs':
                path = args[0]
                if not path.startswith(policy['fs_sandbox']):
                    errors.append(f"fs path outside sandbox: {path}")
            # 3. sqlite table allowlist
            if adapter == 'sqlite' and 'allowed_sqlite_tables' in policy:
                sql = args[0].lower()
                # extract table names via regex
                tables = extract_table_names(sql)
                blocked = [t for t in tables if t not in policy['allowed_sqlite_tables']]
                if blocked:
                    errors.append(f"sqlite table not allowed: {blocked}")
            # 4. http host checks
            if adapter == 'http':
                url = args[0]
                hostname = urlparse(url).hostname
                if 'allowed_http_hosts' in policy and hostname not in policy['allowed_http_hosts']:
                    errors.append(f"http host not allowed: {hostname}")
                if hostname in policy.get('deny_http_hosts', []):
                    errors.append(f"http host denied: {hostname}")
            # 5. require approval
            if f"{adapter}.{target}" in policy.get('require_approval_for', []):
                errors.append(f"operation {adapter}.{target} requires approval")
    return errors
```

## CLI Usage

```bash
ainl-validate --policy policy.yaml program.ainl
# for compiled IR validation, use the Python validator API in `tooling/policy_validator.py`
```

Exit code 0 if valid; non-zero with error messages if violations.

## Example Policies

- **Strict read-only**: allow only `core`, `cache`, `sqlite.query`, `fs.read`, `email` (read). Deny all writes and network.
- **Dev sandbox**: allow all adapters but restrict fs to `/tmp/ainl-dev` and http to `localhost:8080`.
- **Production monitor**: allow `core`, `email`, `calendar`, `svc`, `cache`, `queue`; deny `fs.*`, `sqlite.*`, `http.*`.

## Integration with OpenClaw

Place `policy.yaml` in workspace root. The monitor cron should run validation before executing any AINL program. If the program fails validation, log and abort.

This gives you defense-in-depth: even if a model hallucinates a dangerous operation, it gets caught at compile time.
