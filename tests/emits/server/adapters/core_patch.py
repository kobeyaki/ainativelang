# Patch to ensure core adapter is present in openclaw_monitor_registry
# This module should be imported before the engine is created.

from . import core
from . import openclaw_integration as oi

# Call the function to get the registry dict and inject core if missing
_reg = oi.openclaw_monitor_registry()
if 'core' not in _reg:
    _reg['core'] = core.core_registry()
