#!/usr/bin/env python3
"""
Daily Lead Summary Runner: compiles and executes the daily_lead_summary AINL program
with real OpenClaw integrations.
"""
import os
import sys
import logging
import subprocess
from pathlib import Path
from typing import Dict, Any

# Locate AI_Native_Lang directory (this script is in AI_Native_Lang/scripts/)
SCRIPT_DIR = Path(__file__).resolve().parent
AI_NATIVE_LANG = SCRIPT_DIR.parent
sys.path.insert(0, str(AI_NATIVE_LANG))

from compiler_v2 import AICodeCompiler
from runtime.engine import RuntimeEngine
from adapters.openclaw_integration import openclaw_monitor_registry

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s: %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger('daily_lead_summary')

def send_telegram_error(text: str):
    """Send an error Telegram message via openclaw CLI."""
    openclaw_bin = os.getenv('OPENCLAW_BIN', '/Users/clawdbot/.nvm/versions/node/v22.22.0/bin/openclaw')
    target = os.getenv('OPENCLAW_TARGET', '8626314045')
    try:
        subprocess.run([
            openclaw_bin, 'message', 'send',
            '--target', target,
            '--message', text
        ], check=True, timeout=10)
        logger.info('Error Telegram sent')
    except Exception as e:
        logger.warning(f'Telegram error send failed: {e}')

def main():
    # Ensure OPENCLAW_TARGET is set to Steven's Telegram chat ID for notifications
    if 'OPENCLAW_TARGET' not in os.environ:
        os.environ['OPENCLAW_TARGET'] = '8626314045'
    ainl_path = AI_NATIVE_LANG / 'examples' / 'openclaw' / 'daily_lead_summary.lang'
    logger.info(f'Loading AINL program from {ainl_path}')

    # Compile
    compiler = AICodeCompiler(strict_mode=False, strict_reachability=False)
    with open(ainl_path, 'r') as f:
        src = f.read()
    ir = compiler.compile(src)
    logger.info('Compilation succeeded')

    # Build runtime with OpenClaw adapters
    reg = openclaw_monitor_registry()
    engine = RuntimeEngine(ir, adapters=reg, execution_mode='graph-preferred')
    if not hasattr(engine, 'caps'):
        engine.caps = set()
    if isinstance(engine.caps, list):
        engine.caps = set(engine.caps)
    engine.caps.add('core')
    logger.info('RuntimeEngine ready')

    # Execute label 0; notifications are handled by the AINL program itself via queue.Put
    frame: Dict[str, Any] = {}
    try:
        result = engine.run_label('0', frame)
        logger.info(f'Run complete. Result: {result}')
        # We don't use frame due to copy; just log success
    except Exception as e:
        logger.exception(f'Runtime error: {e}')
        send_telegram_error(f'🔴 Daily Lead Summary: runtime error — {e}')
        sys.exit(1)

if __name__ == '__main__':
    main()
