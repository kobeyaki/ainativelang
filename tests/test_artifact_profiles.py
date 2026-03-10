import json
import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from compiler_v2 import AICodeCompiler


ROOT = Path(__file__).resolve().parent.parent
PROFILE_PATH = ROOT / "tooling" / "artifact_profiles.json"


def _load_profiles() -> dict:
    return json.loads(PROFILE_PATH.read_text(encoding="utf-8"))


def _flatten(section: dict) -> dict:
    out = {}
    for cls in ("strict-valid", "non-strict-only", "legacy-compat"):
        for p in section.get(cls, []):
            out[p] = cls
    return out


def _compile_errors(path: Path, *, strict: bool) -> list:
    code = path.read_text(encoding="utf-8")
    return list(AICodeCompiler(strict_mode=strict).compile(code, emit_graph=True).get("errors", []))


def test_profiles_cover_examples_and_corpus_program_sources():
    profiles = _load_profiles()
    listed = {}
    listed.update(_flatten(profiles["examples"]))
    listed.update(_flatten(profiles["corpus_examples"]))

    discovered = set()
    for p in (ROOT / "examples").rglob("*"):
        if p.suffix in {".ainl", ".lang"}:
            discovered.add(p.relative_to(ROOT).as_posix())
    for p in (ROOT / "corpus").glob("example_*/*_program.ainl"):
        discovered.add(p.relative_to(ROOT).as_posix())
    for p in (ROOT / "corpus").glob("example_*/program.ainl"):
        discovered.add(p.relative_to(ROOT).as_posix())

    assert discovered == set(listed.keys()), (
        "artifact_profiles examples/corpus coverage mismatch",
        sorted(discovered - set(listed.keys())),
        sorted(set(listed.keys()) - discovered),
    )


def test_profiles_enforce_strict_vs_non_strict_compile_expectations():
    profiles = _load_profiles()
    combined = {}
    combined.update(_flatten(profiles["examples"]))
    combined.update(_flatten(profiles["corpus_examples"]))

    for rel, cls in sorted(combined.items()):
        path = ROOT / rel
        strict_errs = _compile_errors(path, strict=True)
        loose_errs = _compile_errors(path, strict=False)
        if cls == "strict-valid":
            assert not strict_errs, f"{rel} expected strict-valid, got errors={strict_errs!r}"
            assert not loose_errs, f"{rel} expected non-strict compile success, got errors={loose_errs!r}"
        elif cls == "non-strict-only":
            assert loose_errs == [], f"{rel} expected non-strict compile success, got errors={loose_errs!r}"
            assert strict_errs, f"{rel} expected strict failure but compiled strict-clean"
        else:
            # Legacy compatibility artifacts are intentionally not part of strict conformance targets.
            assert path.exists(), rel


def test_runtime_fixture_profiles_match_fixture_strict_flags_and_compile_behavior():
    profiles = _load_profiles()
    fx_classes = _flatten(profiles["runtime_fixtures"])

    discovered = {
        p.relative_to(ROOT).as_posix()
        for p in (ROOT / "tests" / "conformance_runtime" / "fixtures").glob("*.json")
    }
    assert discovered == set(fx_classes.keys())

    for rel, cls in sorted(fx_classes.items()):
        fx = json.loads((ROOT / rel).read_text(encoding="utf-8"))
        code = fx["code"]
        strict_errs = list(AICodeCompiler(strict_mode=True).compile(code, emit_graph=True).get("errors", []))
        loose_errs = list(AICodeCompiler(strict_mode=False).compile(code, emit_graph=True).get("errors", []))
        strict_flag = bool(fx.get("strict", True))
        if cls == "strict-valid":
            assert strict_flag is True, f"{rel} strict-valid fixtures must set strict=true or omit it"
            assert not strict_errs, f"{rel} expected strict-valid, got errors={strict_errs!r}"
            assert not loose_errs, f"{rel} expected non-strict compile success, got errors={loose_errs!r}"
        elif cls == "non-strict-only":
            assert strict_flag is False, f"{rel} non-strict-only fixtures must set strict=false"
            assert not loose_errs, f"{rel} expected non-strict compile success, got errors={loose_errs!r}"
            assert strict_errs, f"{rel} expected strict failure but compiled strict-clean"
