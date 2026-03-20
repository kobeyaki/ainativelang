# Backup Manager Implementation

This program implements an automated backup system using available AINL adapters.

## Available Adapters

Based on the registry analysis, the available adapters are:
- **core**: Arithmetic, string, date/time utilities
- **db**: Leads database (CSV source, target F)
- **cache**: Key-value store (get/set, JSON file)
- **queue**: Notification system (Put, sends to self)
- **email**: Email check (G target)
- **calendar**: Calendar check (G target)
- **social**: Web search for mentions (G target)
- **svc**: Service status checks (caddy, cloudflared, maddy, crm)
- **wasm**: WebAssembly execution (CALL)

**Not available:**
- **fs** adapter (file system operations)
- **sqlite** adapter (direct SQL queries)
- **http** adapter (web requests)

## Program Flow

1. **Schedule**: Runs every 6 hours via cron
2. **State Check**: Reads last backup timestamp from cache
3. **Service Health**: Checks CRM, email, and db services
4. **Data Collection**:
   - Reads leads data from CSV via db adapter (target F)
   - Gets recent email count via email adapter (target G)
   - Gets recent calendar events via calendar adapter (target G)
5. **Backup Creation**:
   - Creates JSON payload with all collected data
   - Stores in cache under backup namespace (no fs available)
6. **Cleanup**: Removes old backups from cache based on retention
7. **Notification**: Sends backup completion notification via queue

## Limitations

- Cannot perform actual file system operations (fs adapter not available)
- Backups stored in cache rather than files
- No direct SQL queries (must use db adapter with target F)
- Service status checks limited to predefined targets

## Configuration

- **retention_days**: How long to keep backups in cache (default: 30)
- **backup_count**: Counter for backup iterations (stored in cache)
