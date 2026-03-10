"""OpenClaw integration adapters for the monitor system."""
import os
import json
import subprocess
import time
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional
from runtime.adapters.base import RuntimeAdapter, AdapterError

logger = logging.getLogger(__name__)

# Resolve openclaw binary location
OPENCLAW_BIN = os.getenv('OPENCLAW_BIN', '/Users/clawdbot/.nvm/versions/node/v22.22.0/bin/openclaw')

def _run_openclaw(cmd: List[str], **kwargs) -> subprocess.CompletedProcess:
    full_cmd = [OPENCLAW_BIN] + cmd[1:]
    return subprocess.run(full_cmd, **kwargs)

class EmailAdapter(RuntimeAdapter):
    def call(self, target: str, args: List[Any], context: Dict[str, Any]) -> Any:
        if target != 'G':
            raise AdapterError('email only supports G')
        try:
            result = _run_openclaw(
                ['openclaw', 'mail', 'check', '--unread', '--json'],
                capture_output=True, text=True, timeout=10
            )
            if result.returncode != 0:
                logger.warning(f'mail check failed: {result.stderr}')
                return []
            return json.loads(result.stdout)
        except FileNotFoundError:
            logger.warning('openclaw binary not found; returning []')
            return []
        except Exception as e:
            logger.warning(f'email adapter error: {e}')
            return []

class CalendarAdapter(RuntimeAdapter):
    def call(self, target: str, args: List[Any], context: Dict[str, Any]) -> Any:
        if target != 'G':
            raise AdapterError('calendar only supports G')
        try:
            result = _run_openclaw(
                ['openclaw', 'gog', 'calendar', 'get', '--limit', '10', '--json'],
                capture_output=True, text=True, timeout=10
            )
            if result.returncode != 0:
                logger.warning(f'calendar get failed: {result.stderr}')
                return []
            return json.loads(result.stdout)
        except FileNotFoundError:
            logger.warning('openclaw binary not found for calendar; returning []')
            return []
        except Exception as e:
            logger.warning(f'calendar adapter error: {e}')
            return []

class SocialAdapter(RuntimeAdapter):
    def call(self, target: str, args: List[Any], context: Dict[str, Any]) -> Any:
        if target != 'G':
            raise AdapterError('social only supports G')
        query = os.getenv('SOCIAL_MONITOR_QUERY', '"Steven Hooley"')
        try:
            result = _run_openclaw(
                ['openclaw', 'web', 'search', '--query', query, '--count', '10', '--json'],
                capture_output=True, text=True, timeout=15
            )
            if result.returncode != 0:
                logger.warning(f'web search failed: {result.stderr}')
                return []
            results = json.loads(result.stdout)
            now = int(time.time())
            mentions = []
            for r in results:
                mentions.append({
                    'id': r.get('url', str(hash(r.get('title', '')))[:8]),
                    'text': r.get('title', '') + '\n' + r.get('snippet', ''),
                    'ts': now
                })
            return mentions
        except FileNotFoundError:
            logger.warning('openclaw binary not found for web search; returning []')
            return []
        except Exception as e:
            logger.warning(f'social adapter error: {e}')
            return []

class ServiceAdapter(RuntimeAdapter):
    """Adapter to check status of infrastructure services: caddy, cloudflared, maddy."""
    def call(self, target: str, args: List[Any], context: Dict[str, Any]) -> Any:
        if target not in ('caddy', 'cloudflared', 'maddy'):
            raise AdapterError(f'unknown service: {target}')
        try:
            if target == 'caddy':
                if self._port_listening(80) or self._port_listening(443):
                    return 'up'
                return 'down'
            else:
                return 'up' if self._process_running(target) else 'down'
        except Exception as e:
            logger.warning(f'service status error for {target}: {e}')
            return 'down'

    def _port_listening(self, port: int) -> bool:
        try:
            out = subprocess.check_output(['lsof', '-i', f':{port}', '-sTCP:LISTEN'], text=True)
            return 'LISTEN' in out
        except subprocess.CalledProcessError:
            return False
        except FileNotFoundError:
            try:
                out = subprocess.check_output(['netstat', '-an'], text=True)
                return f'.{port} ' in out or f'.{port}\n' in out
            except:
                return False

    def _process_running(self, name: str) -> bool:
        try:
            out = subprocess.check_output(['pgrep', '-f', name], text=True)
            return bool(out.strip())
        except subprocess.CalledProcessError:
            return False
        except FileNotFoundError:
            return False

class DBLeadsAdapter(RuntimeAdapter):
    def call(self, target: str, args: List[Any], context: Dict[str, Any]) -> Any:
        if target != 'F':
            raise AdapterError('db leads only supports F')
        leads_path = os.getenv('LEADS_CSV', '/Users/clawdbot/.openclaw/workspace/leads/lead_output.csv')
        try:
            import csv
            with open(leads_path, newline='') as f:
                reader = csv.DictReader(f)
                rows = list(reader)
            now = int(time.time())
            for r in rows:
                if 'updated_at' not in r or not r['updated_at']:
                    r['updated_at'] = now
                else:
                    try:
                        r['updated_at'] = int(r['updated_at'])
                    except:
                        r['updated_at'] = now
            return rows
        except Exception as e:
            logger.warning(f'DBLeadsAdapter error: {e}')
            return []

class NotificationQueueAdapter(RuntimeAdapter):
    def push(self, queue: str, value: Any) -> str:
        status = self.call("Put", [queue, value], {})
        return str(status or "queued")

    def call(self, target: str, args: List[Any], context: Dict[str, Any]) -> Any:
        if str(target or "").lower() != 'put':
            raise AdapterError('queue only supports Put')
        if len(args) < 2:
            raise AdapterError('Queue.Put requires (queue, payload)')
        queue_name, payload = args[0], args[1]
        if queue_name != 'notify':
            return None
        msg = self._format_message(payload)
        try:
            _run_openclaw(
                ['openclaw', 'message', 'send', '--to', 'self', '--message', msg],
                check=True, timeout=10
            )
            return 'sent'
        except FileNotFoundError:
            logger.warning('openclaw binary not found for messaging; printing to stdout')
            print(f'[Notification] {msg}')
            return 'logged'
        except subprocess.CalledProcessError as e:
            logger.warning(f'message send failed: {e}')
            print(f'[Notification] {msg}')
            return 'logged'
        except Exception as e:
            logger.warning(f'notification adapter error: {e}')
            return 'error'

    def _format_message(self, payload: Dict[str, Any]) -> str:
        parts = []
        if 'email_count' in payload:
            parts.append(f"📧 Email: {payload['email_count']} new")
        if 'cal_count' in payload:
            parts.append(f"📅 Calendar: {payload['cal_count']} upcoming")
        if 'social_count' in payload:
            parts.append(f"💬 Social: {payload['social_count']} mentions")
        if 'leads_count' in payload:
            parts.append(f"📈 Leads: {payload['leads_count']} recent")
        if 'failed_services' in payload:
            failed = payload['failed_services']
            if failed:
                parts.append(f"⚠️ Services down: {failed}")
        if 'ts' in payload:
            ts = time.strftime('%Y-%m-%d %H:%M', time.localtime(payload['ts']))
            parts.append(f"🕒 {ts}")
        return ' | '.join(parts) if parts else 'Monitor check complete.'

class CacheAdapter(RuntimeAdapter):
    def __init__(self):
        self.store: Dict[str, Dict[str, Any]] = {}
        self.path = os.getenv('MONITOR_CACHE_JSON', '/tmp/monitor_state.json')
        self._load()

    def _load(self):
        try:
            with open(self.path) as f:
                self.store = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.store = {}

    def _save(self):
        try:
            with open(self.path, 'w') as f:
                json.dump(self.store, f)
        except Exception as e:
            logger.warning(f'Cache save error: {e}')

    def get(self, namespace: str, key: str) -> Any:
        return self.store.get(namespace, {}).get(key)

    def set(self, namespace: str, key: str, value: Any, ttl_s: int = 0) -> None:
        self.store.setdefault(namespace, {})[key] = value
        self._save()

    def call(self, target: str, args: List[Any], context: Dict[str, Any]) -> Any:
        verb = str(target or "").lower()
        if verb == 'get':
            ns, key = args[0], args[1]
            return self.get(str(ns), str(key))
        elif verb == 'set':
            ns, key, value = args[0], args[1], args[2]
            self.set(str(ns), str(key), value)
            return None
        else:
            raise AdapterError('cache supports get/set')

def openclaw_monitor_registry(ir_types: Optional[Dict] = None):
    from runtime.adapters.base import AdapterRegistry
    reg = AdapterRegistry(allowed=[
        'core', 'db', 'email', 'calendar', 'social',
        'svc', 'cache', 'queue', 'wasm'
    ])
    from runtime.adapters.builtins import CoreBuiltinAdapter
    reg.register('core', CoreBuiltinAdapter())
    reg.register('email', EmailAdapter())
    reg.register('calendar', CalendarAdapter())
    reg.register('social', SocialAdapter())
    reg.register('svc', ServiceAdapter())
    reg.register('db', DBLeadsAdapter())
    reg.register('cache', CacheAdapter())
    reg.register('queue', NotificationQueueAdapter())

    # Optional WASM adapter if wasmtime is available and demo modules exist
    try:
        from runtime.adapters.wasm import WasmAdapter
        base = Path(__file__).resolve().parent.parent
        modules = {
            'metrics': str(base / 'demo' / 'wasm' / 'metrics.wasm'),
            'health': str(base / 'demo' / 'wasm' / 'health.wasm')
        }
        # Only include modules that exist
        available = {k: v for k, v in modules.items() if Path(v).exists()}
        if available:
            reg.register('wasm', WasmAdapter(modules=available))
    except Exception as e:
        logger.warning(f'WASM adapter not registered: {e}')

    return reg
