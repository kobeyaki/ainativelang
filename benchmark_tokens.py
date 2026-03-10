"""
Compatibility entrypoint for the size benchmark.

Canonical benchmark implementation now lives in `scripts/benchmark_size.py`.
"""

from scripts.benchmark_size import main


if __name__ == "__main__":
    raise SystemExit(main())
