"""
Small synthetic inputs (short strings, no insertion steps) for corner-case behavior.

Each case lists a hard-coded optimal cost (Needleman–Wunsch with δ=30 and the course α
matrix). Those values were verified once against basic_dp; both basic and efficient must
match them, and returned alignments must recompute to the same cost.
"""

from __future__ import annotations

import unittest
from typing import List, Tuple

from alignment_test_utils import (
    alignment_cost_from_strings,
    assert_alignment_matches_inputs,
    get_basic_module,
    run_basic,
    run_efficient,
    write_temp_input,
)

# ---------------------------------------------------------------------------
# Hard-coded expected optimal costs (ground truth for the test harness).
# Scoring: gap δ=30; α as in basic.py / efficient.py. Multiple optimal alignments may
# exist; only the minimum total cost is fixed.
# ---------------------------------------------------------------------------

# Two base strings only: X = s0, Y = t0 (no insertion index lines).
_NO_INSERTION_CASES: List[Tuple[str, str, str, str, int]] = [
    # label, file_body, expected_x, expected_y, expected_cost
    ("actg_vs_tacg", "ACTG\nTACG\n", "ACTG", "TACG", 60),
    ("cc_vs_gg", "CC\nGG\n", "CC", "GG", 120),
    ("single_match", "A\nA\n", "A", "A", 0),
    ("atgc_identical", "ATGC\nATGC\n", "ATGC", "ATGC", 0),
    ("tgca_vs_catg", "TGCA\nCATG\n", "TGCA", "CATG", 120),
]

# One character per line for s0 and t0 (no insertion lines).
_SINGLE_CHAR_CASES: List[Tuple[str, str, str, str, int]] = [
    ("a_vs_c_gaps_cheaper_than_mismatch", "A\nC\n", "A", "C", 60),
    ("a_vs_a", "A\nA\n", "A", "A", 0),
    ("g_vs_t_gaps_cheaper_than_mismatch", "G\nT\n", "G", "T", 60),
    # Mismatch cost α < 2δ (60): optimal alignment uses the letter pair, not two gaps.
    ("a_vs_g_mismatch", "A\nG\n", "A", "G", 48),
    ("c_vs_t_mismatch", "C\nT\n", "C", "T", 48),
]

# Equal-length strings, no insert steps: mix of exact matches and uniform-letter mismatch.
_EQUAL_LENGTH_CASES: List[Tuple[str, str, str, str, int]] = [
    ("aaaa_vs_tttt", "AAAA\nTTTT\n", "AAAA", "TTTT", 240),
    ("aa_vs_aa", "AA\nAA\n", "AA", "AA", 0),
    ("acgt_vs_acgt", "ACGT\nACGT\n", "ACGT", "ACGT", 0),
    ("gggg_vs_aaaa", "GGGG\nAAAA\n", "GGGG", "AAAA", 192),
]

# Both strings consist of a single repeated letter (possibly different letters).
_UNIFORM_LETTER_CASES: List[Tuple[str, str, str, str, int]] = [
    ("aaa_vs_ccc", "AAA\nCCC\n", "AAA", "CCC", 180),
    ("aa_vs_cc", "AA\nCC\n", "AA", "CC", 120),
    ("aaaa_vs_cccc", "AAAA\nCCCC\n", "AAAA", "CCCC", 240),
]


class TestEdgeCases(unittest.TestCase):
    """Short synthetic inputs (no insert steps) with hard-coded optimal costs."""

    def _run_content(self, content: str) -> Tuple[str, str]:
        """Parse a minimal in-memory input file and return the two generated strings."""
        basic = get_basic_module()
        path = write_temp_input(content)
        try:
            return basic.parse_input(str(path))
        finally:
            path.unlink(missing_ok=True)

    def _assert_case_against_expected(
        self,
        label: str,
        x: str,
        y: str,
        expected_cost: int,
    ) -> None:
        """
        Compare basic and efficient to the same expected optimal cost and validate
        alignments (feasible for X/Y, cost matches recomputation).
        """
        with self.subTest(label=label, x=x, y=y, expected_cost=expected_cost):
            cb, abx, aby = run_basic(x, y)
            ce, aex, aey = run_efficient(x, y, 1)
            self.assertEqual(
                expected_cost,
                cb,
                msg="basic cost must match hard-coded optimum",
            )
            self.assertEqual(
                expected_cost,
                ce,
                msg="efficient cost must match hard-coded optimum",
            )
            self.assertEqual(cb, ce, msg="basic and efficient must agree")
            assert_alignment_matches_inputs(x, y, abx, aby)
            assert_alignment_matches_inputs(x, y, aex, aey)
            self.assertEqual(alignment_cost_from_strings(abx, aby), cb)
            self.assertEqual(alignment_cost_from_strings(aex, aey), ce)

    def test_no_insertions(self) -> None:
        """
        Only two lines in the file (s0, t0): no insertion indices.

        Parsed X and Y must match the expected strings; optimal cost must match each
        hard-coded value; both algorithms must hit that cost.
        """
        for label, body, want_x, want_y, want_cost in _NO_INSERTION_CASES:
            with self.subTest(case=label):
                x, y = self._run_content(body)
                self.assertEqual(x, want_x)
                self.assertEqual(y, want_y)
                self._assert_case_against_expected(label, x, y, want_cost)

    def test_single_char_bases(self) -> None:
        """
        Smallest nontrivial sizes: one character per string (still no insertion lines).

        Covers match, cheap-gap vs mismatch tradeoffs, and a pure mismatch alignment.
        """
        for label, body, want_x, want_y, want_cost in _SINGLE_CHAR_CASES:
            with self.subTest(case=label):
                x, y = self._run_content(body)
                self.assertEqual(x, want_x)
                self.assertEqual(y, want_y)
                self._assert_case_against_expected(label, x, y, want_cost)

    def test_equal_length_strings(self) -> None:
        """
        Equal-length X and Y without insert steps: identical strings (cost 0) and
        homogeneous / patterned mismatches with known optimal costs.
        """
        for label, body, want_x, want_y, want_cost in _EQUAL_LENGTH_CASES:
            with self.subTest(case=label):
                x, y = self._run_content(body)
                self.assertEqual(x, want_x)
                self.assertEqual(y, want_y)
                self._assert_case_against_expected(label, x, y, want_cost)

    def test_uniform_letter_strings(self) -> None:
        """
        Each string is one repeated letter (AAA, CCC, ...): stresses uniform mismatch grids.
        """
        for label, body, want_x, want_y, want_cost in _UNIFORM_LETTER_CASES:
            with self.subTest(case=label):
                x, y = self._run_content(body)
                self.assertEqual(x, want_x)
                self.assertEqual(y, want_y)
                self._assert_case_against_expected(label, x, y, want_cost)


if __name__ == "__main__":
    unittest.main()
