# TiktokAdapter for AINL monitor
# Provides access to TiktokReport and TiktokVideo from CRM SQLite DB

import sqlite3
from datetime import datetime, timezone
from typing import Any, List
from ainl_adapters import AdapterBase
import os

class TiktokAdapter(AdapterBase):
    group = 'tiktok'

    def _connect(self):
        db_path = '/Users/clawdbot/.openclaw/workspace/crm/prisma/dev.db'
        return sqlite3.connect(db_path)

    # --- TiktokReport ---
    async def F(self, args: List[Any], frame):
        """Fetch all TiktokReport records."""
        conn = self._connect()
        try:
            cur = conn.cursor()
            cur.execute("SELECT id, filename, path, videoCount, createdAt FROM TiktokReport ORDER BY createdAt DESC")
            rows = cur.fetchall()
            result = []
            for row in rows:
                rid, filename, path, videoCount, createdAt = row
                # Convert ISO to epoch seconds
                if createdAt:
                    try:
                        dt = datetime.fromisoformat(createdAt.replace('Z', '+00:00'))
                        ts = int(dt.timestamp())
                    except Exception:
                        ts = 0
                else:
                    ts = 0
                result.append({
                    'id': rid,
                    'filename': filename,
                    'path': path,
                    'videoCount': videoCount,
                    'createdAt': createdAt,
                    'createdAt_ts': ts,
                })
            return result
        finally:
            conn.close()

    async def recent(self, args: List[Any], frame):
        """Return number of TiktokReport created in the last N hours (default 24)."""
        hours_ago = 24
        if args and isinstance(args[0], (int, float)):
            hours_ago = args[0]
        cutoff_seconds = hours_ago * 3600
        cutoff_ts = int(datetime.now(timezone.utc).timestamp()) - cutoff_seconds
        conn = self._connect()
        try:
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM TiktokReport WHERE createdAt >= datetime(?,'unixepoch')", (cutoff_ts,))
            count = cur.fetchone()[0]
            return count
        finally:
            conn.close()

    # --- TiktokVideo ---
    async def videos(self, args: List[Any], frame):
        """Fetch all TiktokVideo records with processedAt and numeric timestamps."""
        conn = self._connect()
        try:
            cur = conn.cursor()
            cur.execute("""
                SELECT id, tiktokId, title, description, processedAt, createdAt
                FROM TiktokVideo
                ORDER BY processedAt DESC
            """)
            rows = cur.fetchall()
            result = []
            for row in rows:
                rid, tid, title, desc, processedAt, createdAt = row
                # Convert processedAt ISO to epoch
                if processedAt:
                    try:
                        dt = datetime.fromisoformat(processedAt.replace('Z', '+00:00'))
                        processed_ts = int(dt.timestamp())
                    except Exception:
                        processed_ts = 0
                else:
                    processed_ts = 0
                result.append({
                    'id': rid,
                    'tiktokId': tid,
                    'title': title,
                    'description': desc,
                    'processedAt': processedAt,
                    'processedAt_ts': processed_ts,
                })
            return result
        finally:
            conn.close()

# Register
adapter = TiktokAdapter()
