import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from runtime.adapters.base import RuntimeAdapter
from runtime.engine import RuntimeEngine
from tests.helpers.recording_adapters import RecordingAdapterRegistry, ReplayAdapterRegistry


class _CounterAdapter(RuntimeAdapter):
    def __init__(self):
        self.n = 0

    def call(self, target, args, context):
        self.n += 1
        return self.n


def test_replay_registry_reproduces_output_and_call_log():
    code = "L1: R ext.next seed ->a\nR ext.next seed ->b\nX out add a b\nJ out\n"

    live_reg = RecordingAdapterRegistry(allowed=["core", "ext"])
    live_reg.register("ext", _CounterAdapter())
    out_live = RuntimeEngine.from_code(code, strict=True, trace=False, adapters=live_reg, step_fallback=False).run_label("1")

    replay_reg = ReplayAdapterRegistry(live_reg.call_log, allowed=["core", "ext"])
    out_replay = RuntimeEngine.from_code(code, strict=True, trace=False, adapters=replay_reg, step_fallback=False).run_label("1")

    assert out_live == out_replay
    assert replay_reg.call_log == live_reg.call_log
