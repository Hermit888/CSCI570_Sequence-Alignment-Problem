"""
Tests against SampleTestCases (input1..input5) and reference costs on line 1 of outputs.
"""

from pathlib import Path
from typing import List, Tuple
import unittest

from alignment_test_utils import (
    alignment_cost_from_strings,
    assert_alignment_matches_inputs,
    get_basic_module,
    read_expected_cost,
    run_basic,
    run_efficient,
    SAMPLE_DIR,
)


class TestSampleCases(unittest.TestCase):
    """Tests against the course SampleTestCases inputs and reference costs (line 1)."""

    @classmethod
    def setUpClass(cls) -> None:
        """Build the list of (input, output) paths for input1..input5 when both exist."""
        cls.cases: List[Tuple[Path, Path]] = []
        for i in range(1, 6):
            inp = SAMPLE_DIR / f"input{i}.txt"
            out = SAMPLE_DIR / f"output{i}.txt"
            if inp.is_file() and out.is_file():
                cls.cases.append((inp, out))

    def test_sample_costs_basic_vs_efficient(self) -> None:
        """
        For each sample pair, check that basic and efficient match the reference cost,
        agree with each other, produce alignments consistent with X/Y, and that the
        recomputed cost from the printed strings equals the reported optimal cost.
        """
        basic = get_basic_module()
        for inp, expected_out in self.cases:
            with self.subTest(input=inp.name):
                x, y = basic.parse_input(str(inp))
                want = read_expected_cost(expected_out)
                cb, abx, aby = run_basic(x, y)
                ce, aex, aey = run_efficient(x, y, trivial_size=1)
                self.assertEqual(cb, want, msg="basic cost vs sample line 1")
                self.assertEqual(ce, want, msg="efficient cost vs sample line 1")
                self.assertEqual(cb, ce, msg="basic vs efficient")
                assert_alignment_matches_inputs(x, y, abx, aby)
                assert_alignment_matches_inputs(x, y, aex, aey)
                self.assertEqual(alignment_cost_from_strings(abx, aby), cb)
                self.assertEqual(alignment_cost_from_strings(aex, aey), ce)

    def test_trivial_sizes_match(self) -> None:
        """
        Hirschberg's trivial threshold should not change the optimal cost.

        For sample input1, efficient costs must match basic for several trivial_size values.
        """
        inp = SAMPLE_DIR / "input1.txt"
        if not inp.is_file():
            self.skipTest("input1 missing")
        basic = get_basic_module()
        x, y = basic.parse_input(str(inp))
        b_cost, _, _ = run_basic(x, y)
        for t in (1, 2, 8, 16, 32):
            with self.subTest(trivial_size=t):
                e_cost, _, _ = run_efficient(x, y, trivial_size=t)
                self.assertEqual(e_cost, b_cost)


if __name__ == "__main__":
    unittest.main()
