.PHONY: conformance

# Automated Conformance Test Suite (snapshot-driven).
# Usage:
#   make conformance
#   SNAPSHOT_UPDATE=1 make conformance
# Match CI Python 3.10 + deps (pytest-xdist, syrupy), e.g.:
#   make conformance PYTHON=./.venv-py310/bin/python
CONFORMANCE_DIR ?= tests/conformance

PYTHON ?= python3
PYTEST ?= $(PYTHON) -m pytest
SNAPSHOT_UPDATE ?= 0
CONFORMANCE_LOG ?= tests/snapshots/conformance/last_run.log
CONFORMANCE_SUMMARY ?= tests/snapshots/conformance/summary.md
CONFORMANCE_BADGE ?= tests/snapshots/conformance/conformance_badge.svg

conformance:
	@echo "==> Running conformance suite in $(CONFORMANCE_DIR)"
	@mkdir -p tests/snapshots/conformance
	@if [ "$(SNAPSHOT_UPDATE)" = "1" ]; then \
	  $(PYTEST) -n auto $(CONFORMANCE_DIR) --snapshot-update | tee "$(CONFORMANCE_LOG)"; \
	else \
	  $(PYTEST) -n auto $(CONFORMANCE_DIR) | tee "$(CONFORMANCE_LOG)"; \
	fi
	@$(PYTHON) -c 'import re, pathlib; log=pathlib.Path("$(CONFORMANCE_LOG)").read_text(encoding="utf-8"); mp=re.search(r"([0-9]+) passed", log); ms=re.search(r"([0-9]+) skipped", log); mf=re.search(r"([0-9]+) failed", log); p=int(mp.group(1)) if mp else 0; s=int(ms.group(1)) if ms else 0; f=int(mf.group(1)) if mf else 0; status="passing" if f==0 else "failing"; color_hex="#4c1" if f==0 else "#e05d44"; summary=pathlib.Path("$(CONFORMANCE_SUMMARY)"); summary.write_text(f"# Conformance Summary\n\n- Passed: {p}\n- Skipped: {s}\n- Failed: {f}\n- Status: {status}\n", encoding="utf-8"); badge=pathlib.Path("$(CONFORMANCE_BADGE)"); svg=f"<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"180\" height=\"20\" role=\"img\" aria-label=\"conformance: {status}\"><rect width=\"110\" height=\"20\" fill=\"#555\"/><rect x=\"110\" width=\"70\" height=\"20\" fill=\"{color_hex}\"/><text x=\"55\" y=\"14\" fill=\"#fff\" font-family=\"Verdana\" font-size=\"11\" text-anchor=\"middle\">conformance</text><text x=\"145\" y=\"14\" fill=\"#fff\" font-family=\"Verdana\" font-size=\"11\" text-anchor=\"middle\">{status}</text></svg>"; badge.write_text(svg, encoding="utf-8"); print(f"==> Wrote {summary} and {badge}")'

