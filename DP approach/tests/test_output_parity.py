"""
Compare saved program outputs: basic_output vs efficient_output must agree on optimal cost.

Each pair out*.txt in both folders should have the same integer on line 1 (alignment cost).
Alignments and timing may differ; only cost parity is checked.
"""

from __future__ import annotations

from pathlib import Path
import unittest

# tests/ is under DP approach/; output folders are siblings of tests/.
_DP_APPROACH = Path(__file__).resolve().parent.parent
_BASIC_OUTPUT_DIR = _DP_APPROACH / "basic_output"
_EFFICIENT_OUTPUT_DIR = _DP_APPROACH / "efficient_output"


def _read_cost_first_line(output_path: Path) -> int:
    """Read the alignment cost from line 1 of a five-line output file."""
    with open(output_path, "r", encoding="utf-8") as handle:
        line = handle.readline()
    return int(line.strip())


def _paired_output_names() -> list[str]:
    """Return sorted basenames present in both basic_output and efficient_output."""
    if not _BASIC_OUTPUT_DIR.is_dir() or not _EFFICIENT_OUTPUT_DIR.is_dir():
        return []
    basic_names = {p.name for p in _BASIC_OUTPUT_DIR.glob("out*.txt") if p.is_file()}
    efficient_names = {p.name for p in _EFFICIENT_OUTPUT_DIR.glob("out*.txt") if p.is_file()}
    return sorted(basic_names & efficient_names)


class TestBasicEfficientOutputParity(unittest.TestCase):
    """Line-1 cost in basic_output must match line-1 cost in efficient_output for each pair."""

    def test_basic_and_efficient_saved_outputs_same_cost(self) -> None:
        """
        For every out*.txt that exists in both basic_output and efficient_output, the
        reported optimal costs (first line) must be equal.
        """
        if not _BASIC_OUTPUT_DIR.is_dir():
            self.skipTest(f"missing directory: {_BASIC_OUTPUT_DIR}")
        if not _EFFICIENT_OUTPUT_DIR.is_dir():
            self.skipTest(f"missing directory: {_EFFICIENT_OUTPUT_DIR}")

        names = _paired_output_names()
        if not names:
            self.skipTest(
                "no paired out*.txt files in basic_output and efficient_output; "
                "run basic_all.sh / efficient_all.sh first if you expect this test."
            )

        for name in names:
            with self.subTest(output_file=name):
                basic_path = _BASIC_OUTPUT_DIR / name
                efficient_path = _EFFICIENT_OUTPUT_DIR / name
                basic_cost = _read_cost_first_line(basic_path)
                efficient_cost = _read_cost_first_line(efficient_path)
                self.assertEqual(
                    basic_cost,
                    efficient_cost,
                    msg=(
                        f"cost on line 1 differs: basic_output/{name}={basic_cost}, "
                        f"efficient_output/{name}={efficient_cost}"
                    ),
                )


if __name__ == "__main__":
    unittest.main()
