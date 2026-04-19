"""
Run all alignment tests and optionally the datapoints consistency sweep.

Usage (from project root):
  python "DP approach/tests/run_tests.py"
  python "DP approach/tests/run_tests.py" -v
  python "DP approach/tests/run_tests.py" --datapoints

From inside DP approach:
  python tests/run_tests.py

Or use unittest discovery (from project root):
  python -m unittest discover -s "DP approach/tests" -p "test_*.py"
"""

from __future__ import annotations

import argparse
import sys
import unittest
from pathlib import Path
from typing import List, Optional

# Ensure tests/ is on path so alignment_test_utils imports work when run as script.
_TESTS_DIR = Path(__file__).resolve().parent
if str(_TESTS_DIR) not in sys.path:
    sys.path.insert(0, str(_TESTS_DIR))

from alignment_test_utils import DATAPOINTS_DIR, run_datapoint_checks  # noqa: E402


def _build_argparser() -> argparse.ArgumentParser:
    """CLI for unittest verbosity, optional datapoint sweep, and efficiency limits."""
    p = argparse.ArgumentParser(description="Sequence alignment tests (basic vs efficient).")
    p.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="unittest verbose",
    )
    p.add_argument(
        "--datapoints",
        action="store_true",
        help=f"also run checks on files in {DATAPOINTS_DIR}",
    )
    p.add_argument(
        "--datapoint-max-cells",
        type=int,
        default=8_000_000,
        metavar="N",
        help="run basic DP only when len(x)*len(y) <= N (default: 8_000_000)",
    )
    p.add_argument(
        "--trivial-size",
        type=int,
        default=1,
        help="trivial_size passed to efficient (default: 1)",
    )
    return p


def main(argv: Optional[List[str]] = None) -> int:
    """Discover and run test_*.py in this directory; optionally run datapoint sweep."""
    args = _build_argparser().parse_args(argv)

    loader = unittest.TestLoader()
    # Use stdout so per-module messages interleave with unittest output (default runner uses stderr).
    runner = unittest.TextTestRunner(
        stream=sys.stdout,
        verbosity=2 if args.verbose else 1,
    )
    code = 0

    test_paths = sorted(_TESTS_DIR.glob("test_*.py"))
    for path in test_paths:
        module_name = path.stem
        suite = loader.loadTestsFromName(module_name)
        result = runner.run(suite)
        if result.wasSuccessful():
            print(f"no error found in {module_name}", flush=True)
        else:
            code = 1

    if args.datapoints:
        print(
            f"\nDatapoints dir: {DATAPOINTS_DIR} "
            f"(basic if cells <= {args.datapoint_max_cells}, trivial_size={args.trivial_size})"
        )
        errs = run_datapoint_checks(args.datapoint_max_cells, args.trivial_size)
        if errs:
            print("\nDatapoint issues:")
            for e in errs:
                print(f"  - {e}")
            code = 1
        else:
            print("no error found in datapoints")

    return code


if __name__ == "__main__":
    raise SystemExit(main())
