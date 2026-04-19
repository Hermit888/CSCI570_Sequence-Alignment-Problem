"""
Shared helpers for sequence alignment tests: paths, scoring, I/O, and datapoint sweeps.

Imported by test_*.py modules and by run_tests.py.
"""

from __future__ import annotations

import math
import sys
import tempfile
from pathlib import Path
from typing import Iterable, List, Tuple

# -----------------------------------------------------------------------------
# Project constants (must match basic.py / efficient.py)
# -----------------------------------------------------------------------------

GAP = 30
ALPHA = {
    "A": {"A": 0, "C": 110, "G": 48, "T": 94},
    "C": {"A": 110, "C": 0, "G": 118, "T": 48},
    "G": {"A": 48, "C": 118, "G": 0, "T": 110},
    "T": {"A": 94, "C": 48, "G": 110, "T": 0},
}

# tests/ lives inside DP approach/ next to basic.py and efficient.py.
_TESTS_DIR = Path(__file__).resolve().parent
_DP_APPROACH = _TESTS_DIR.parent
_PROJECT_ROOT = _DP_APPROACH.parent
if str(_DP_APPROACH) not in sys.path:
    sys.path.insert(0, str(_DP_APPROACH))

import basic as _BASIC  # noqa: E402
import efficient as _EFFICIENT  # noqa: E402

SAMPLE_DIR = _PROJECT_ROOT / "SampleTestCases"
DATAPOINTS_DIR = _PROJECT_ROOT / "Datapoints"


def alignment_cost_from_strings(ax: str, ay: str) -> int:
    """Recompute Needleman–Wunsch cost from two aligned strings (gaps as '_')."""
    if len(ax) != len(ay):
        raise ValueError("aligned strings must have equal length")
    total = 0
    for a, b in zip(ax, ay):
        if a == "_" and b == "_":
            raise ValueError("invalid column: both gaps")
        if a == "_":
            total += GAP
        elif b == "_":
            total += GAP
        else:
            if a not in ALPHA or b not in ALPHA[a]:
                raise ValueError(f"invalid base character: {a!r} vs {b!r}")
            total += ALPHA[a][b]
    return total


def recovered_sequence(aligned: str) -> str:
    """Return the original sequence string with gap characters removed."""
    return aligned.replace("_", "")


def parse_output_lines(text: str) -> Tuple[int, str, str, float, float]:
    """Parse the five-line program output format (cost, two alignments, time, memory)."""
    lines = text.strip().splitlines()
    if len(lines) != 5:
        raise ValueError(f"expected 5 lines, got {len(lines)}")
    cost = int(lines[0])
    ax, ay = lines[1], lines[2]
    time_ms = float(lines[3])
    mem_kb = float(lines[4])
    if math.isnan(time_ms) or math.isnan(mem_kb):
        raise ValueError("time/memory must not be NaN")
    return cost, ax, ay, time_ms, mem_kb


def read_expected_cost(sample_output_path: Path) -> int:
    """Read the integer optimal cost from line 1 of a sample output file."""
    with open(sample_output_path, "r", encoding="utf-8") as f:
        first = f.readline().strip()
    return int(first)


def assert_alignment_matches_inputs(
    x: str, y: str, align_x: str, align_y: str
) -> None:
    """Check that alignments are consistent with the raw input strings X and Y."""
    if recovered_sequence(align_x) != x:
        raise AssertionError("first alignment does not match input x after removing gaps")
    if recovered_sequence(align_y) != y:
        raise AssertionError("second alignment does not match input y after removing gaps")


def run_basic(x: str, y: str) -> Tuple[int, str, str]:
    """Run the full-table DP implementation and return (cost, aligned_x, aligned_y)."""
    cost, ax, ay = _BASIC.basic_dp(x, y, _BASIC.delta, _BASIC.alpha)
    return cost, ax, ay


def run_efficient(x: str, y: str, trivial_size: int) -> Tuple[int, str, str]:
    """Run the Hirschberg-style implementation with the given trivial-size threshold."""
    return _EFFICIENT.memory_efficient_alignment(x, y, trivial_size)


def get_basic_module():
    """Expose basic module for parse_input etc. in tests."""
    return _BASIC


def write_temp_input(content: str) -> Path:
    """Write text to a temporary file and return its path (caller may delete after use)."""
    tmp = tempfile.NamedTemporaryFile(
        mode="w", suffix=".txt", delete=False, encoding="utf-8"
    )
    tmp.write(content)
    tmp.close()
    return Path(tmp.name)


def iter_datapoint_inputs(directory: Path) -> Iterable[Path]:
    """Yield sorted paths matching in*.txt under the datapoints directory."""
    if not directory.is_dir():
        return
    for p in sorted(directory.glob("in*.txt"), key=lambda x: x.name):
        yield p


def run_datapoint_checks(max_cells: int, trivial_size: int) -> List[str]:
    """
    For each datapoint input: parse, run efficient, verify recomputed cost.

    If len(x)*len(y) <= max_cells, also run basic and compare costs.
    """
    errors: List[str] = []
    for inp in iter_datapoint_inputs(DATAPOINTS_DIR):
        try:
            x, y = _BASIC.parse_input(str(inp))
        except Exception as exc:
            errors.append(f"{inp.name}: parse_input failed: {exc}")
            continue
        m, n = len(x), len(y)
        cells = m * n
        try:
            ce, aex, aey = run_efficient(x, y, trivial_size)
        except Exception as exc:
            errors.append(f"{inp.name}: efficient failed: {exc}")
            continue
        try:
            assert_alignment_matches_inputs(x, y, aex, aey)
            cr = alignment_cost_from_strings(aex, aey)
            if cr != ce:
                errors.append(
                    f"{inp.name}: recomputed cost {cr} != reported {ce} (efficient)"
                )
        except Exception as exc:
            errors.append(f"{inp.name}: verify efficient alignment: {exc}")

        if cells <= max_cells:
            try:
                cb, abx, aby = run_basic(x, y)
            except Exception as exc:
                errors.append(f"{inp.name}: basic failed (cells={cells}): {exc}")
                continue
            if cb != ce:
                errors.append(
                    f"{inp.name}: basic cost {cb} != efficient cost {ce} (cells={cells})"
                )
            try:
                assert_alignment_matches_inputs(x, y, abx, aby)
                if alignment_cost_from_strings(abx, aby) != cb:
                    errors.append(f"{inp.name}: basic alignment recomputed cost mismatch")
            except Exception as exc:
                errors.append(f"{inp.name}: verify basic alignment: {exc}")
        else:
            pass
    return errors
