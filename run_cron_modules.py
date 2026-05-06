#!/usr/bin/env python3
"""
AINL Cron Supervisor
Orchestrates scheduled memory consolidation and other daily operational tasks.
Compiled graph execution handler.
"""

import sys
import os
import json
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any

# Workspace root
WORKSPACE = Path("/data/.openclaw/workspace")
MEMORY_DIR = WORKSPACE / "memory"
MEMORY_FILE = WORKSPACE / "MEMORY.md"
INTELLIGENCE_DIR = WORKSPACE / "intelligence"

class MemoryConsolidationTask:
    """Consolidates recent memory files into MEMORY.md"""
    
    HIGH_SIGNAL_KEYWORDS = {
        "important", "fixed", "config", "todo", "lesson", "setting", 
        "changed", "enabled", "disabled", "critical", "blocked", "resolved",
        "deployed", "issue", "error", "fixed", "updated", "configured"
    }
    
    TERSE_PREFIXES = {
        "important": "I:",
        "critical": "I:",
        "blocked": "B:",
        "todo": "T:",
        "lesson": "L:",
        "setting": "S:",
        "configured": "S:",
        "fixed": "F:",
        "resolved": "F:",
        "deployed": "D:",
        "changed": "C:",
        "enabled": "E:",
        "disabled": "D:",
    }
    
    def __init__(self, lookback_days: int = 7):
        self.lookback_days = lookback_days
        self.today = datetime.now()
        self.cutoff = self.today - timedelta(days=lookback_days)
    
    def scan_recent_files(self) -> List[Path]:
        """Find memory files from last N days"""
        if not MEMORY_DIR.exists():
            return []
        
        recent = []
        for fpath in MEMORY_DIR.glob("*.md"):
            try:
                mtime = datetime.fromtimestamp(fpath.stat().st_mtime)
                if mtime >= self.cutoff:
                    recent.append(fpath)
            except:
                pass
        
        return sorted(recent)
    
    def extract_signal_lines(self, files: List[Path]) -> Dict[str, List[str]]:
        """Extract lines matching high-signal keywords"""
        signal_map = {}
        
        for fpath in files:
            try:
                content = fpath.read_text()
                lines = content.split("\n")
                signals = []
                
                for line in lines:
                    line_lower = line.lower()
                    for keyword in self.HIGH_SIGNAL_KEYWORDS:
                        if keyword in line_lower:
                            # Extract meaningful content
                            if line.strip() and not line.startswith("#"):
                                signals.append(line.strip())
                            break
                
                if signals:
                    signal_map[fpath.name] = signals
            except Exception as e:
                print(f"[ERROR] Reading {fpath}: {e}", file=sys.stderr)
        
        return signal_map
    
    def tersify_lines(self, signal_map: Dict[str, List[str]]) -> List[str]:
        """Format lines with terse prefixes"""
        terse = []
        
        for filename, lines in signal_map.items():
            for line in lines:
                prefix = "M:"  # Default: memory
                
                # Detect best prefix
                for keyword, pref in self.TERSE_PREFIXES.items():
                    if keyword in line.lower():
                        prefix = pref
                        break
                
                # Clean line: remove common prefixes/bullets
                clean = line.strip().lstrip("- •").strip()
                
                # Append with prefix
                terse.append(f"{prefix} {clean}")
        
        return terse
    
    def load_existing_memory(self) -> str:
        """Load current MEMORY.md"""
        if MEMORY_FILE.exists():
            return MEMORY_FILE.read_text()
        return ""
    
    def deduplicate(self, new_entries: List[str], existing: str) -> List[str]:
        """Filter out duplicates"""
        existing_lower = existing.lower()
        deduped = []
        
        for entry in new_entries:
            # Fuzzy check: if similar content exists, skip
            entry_lower = entry.lower()
            if entry_lower not in existing_lower:
                deduped.append(entry)
        
        return deduped
    
    def append_consolidated(self, new_entries: List[str], existing: str) -> str:
        """Append new consolidated section"""
        if not new_entries:
            return existing
        
        date_str = self.today.strftime("%Y-%m-%d")
        
        section = f"\n\n## Consolidation: {date_str}\n\n"
        section += "\n".join(f"- {entry}" for entry in new_entries)
        
        return existing + section
    
    def execute(self) -> Dict[str, Any]:
        """Run full consolidation task"""
        print(f"[MEMORY CONSOLIDATION] Starting at {self.today.isoformat()}")
        
        # Step 1: Scan files
        files = self.scan_recent_files()
        print(f"[SCAN] Found {len(files)} recent files")
        
        # Step 2: Extract signals
        signal_map = self.extract_signal_lines(files)
        total_signals = sum(len(v) for v in signal_map.values())
        print(f"[EXTRACT] Found {total_signals} signal lines across {len(signal_map)} files")
        
        # Step 3: Tersify
        terse = self.tersify_lines(signal_map)
        print(f"[TERSIFY] Formatted {len(terse)} terse bullets")
        
        # Step 4: Load existing
        existing = self.load_existing_memory()
        
        # Step 5: Deduplicate
        new_entries = self.deduplicate(terse, existing)
        print(f"[DEDUPE] {len(new_entries)} new entries after dedup")
        
        # Step 6: Append
        updated = self.append_consolidated(new_entries, existing)
        MEMORY_FILE.write_text(updated)
        print(f"[WRITE] Updated MEMORY.md ({len(updated)} bytes)")
        
        return {
            "status": "success",
            "itemsConsolidated": len(new_entries),
            "filesProcessed": len(files),
            "newBulletsAdded": new_entries[:10],  # First 10 for report
            "totalBullets": len(new_entries),
            "timestamp": self.today.isoformat(),
        }

def supervisor(task: str = "consolidate"):
    """Main supervisor entry point"""
    
    if task == "consolidate" or task == "memory":
        consolidator = MemoryConsolidationTask(lookback_days=7)
        report = consolidator.execute()
        
        print("\n" + "="*60)
        print("CONSOLIDATION REPORT")
        print("="*60)
        print(f"Status: {report['status']}")
        print(f"Items Consolidated: {report['itemsConsolidated']}")
        print(f"Files Processed: {report['filesProcessed']}")
        print(f"Total Bullets Added: {report['totalBullets']}")
        print(f"Timestamp: {report['timestamp']}")
        print("\nSample new entries:")
        for entry in report['newBulletsAdded']:
            print(f"  - {entry}")
        print("="*60 + "\n")
        
        return report
    else:
        print(f"[ERROR] Unknown task: {task}")
        sys.exit(1)

if __name__ == "__main__":
    task_arg = sys.argv[1] if len(sys.argv) > 1 else "consolidate"
    result = supervisor(task_arg)
    
    # Output JSON for integration
    print(json.dumps(result, indent=2))
