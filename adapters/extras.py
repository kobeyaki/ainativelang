# ExtrasAdapter for AINL monitor
# Provides utility checks: file_exists, docker_image_exists, http_status, newest_backup_mtime

import os
import subprocess
from datetime import datetime
from typing import Any, List
from runtime.adapters.base import RuntimeAdapter, AdapterError

class ExtrasAdapter(RuntimeAdapter):
    def call(self, target: str, args: List[Any], context: dict) -> Any:
        if target == 'file_exists':
            if len(args) < 1:
                raise AdapterError('file_exists requires path')
            path = args[0]
            return 1 if os.path.exists(path) and os.access(path, os.X_OK) else 0
        elif target == 'docker_image_exists':
            if len(args) < 1:
                raise AdapterError('docker_image_exists requires image name')
            image = args[0]
            try:
                out = subprocess.check_output(['docker', 'images', '-q', image], text=True, timeout=5)
                return 1 if out.strip() else 0
            except (subprocess.CalledProcessError, FileNotFoundError):
                return 0
        elif target == 'http_status':
            if len(args) < 1:
                raise AdapterError('http_status requires url')
            url = args[0]
            try:
                out = subprocess.check_output(['curl', '-s', '-o', '/dev/null', '-w', '%{http_code}', url], text=True, timeout=5)
                code = int(out.strip())
                return code
            except (subprocess.CalledProcessError, FileNotFoundError):
                try:
                    import urllib.request
                    with urllib.request.urlopen(url, timeout=5) as resp:
                        return resp.status
                except Exception:
                    return 0
        elif target == 'newest_backup_mtime':
            if len(args) < 1:
                raise AdapterError('newest_backup_mtime requires backup directory')
            backup_dir = args[0]
            try:
                files = []
                for fname in os.listdir(backup_dir):
                    if fname.endswith('.bak'):
                        path = os.path.join(backup_dir, fname)
                        mtime = os.path.getmtime(path)
                        files.append((mtime, path))
                if not files:
                    return 0
                newest = max(files, key=lambda x: x[0])[0]
                return int(newest)
            except Exception:
                return 0
        else:
            raise AdapterError(f'extras unknown target: {target}')

# Register factory (the registry will call this)
def get_adapter():
    return ExtrasAdapter()
