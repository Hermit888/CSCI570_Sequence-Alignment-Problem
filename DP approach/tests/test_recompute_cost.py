"""
Sanity checks for the manual alignment cost recomputation helper.
"""

import unittest

from alignment_test_utils import alignment_cost_from_strings


class TestRecomputeCost(unittest.TestCase):
    """Sanity checks for the manual cost recomputation helper."""

    def test_known_tiny(self) -> None:
        """
        Verify that alignment_cost_from_strings matches a hand-checked tiny example.

        Aligning one base to another via two gaps (e.g. A_ vs _C) costs 2 * gap penalty = 60.
        """
        ax, ay = "A_", "_C"
        self.assertEqual(alignment_cost_from_strings(ax, ay), 60)
        ax, ay = "_A", "C_"
        self.assertEqual(alignment_cost_from_strings(ax, ay), 60)

    def test_match_and_mismatch_columns(self) -> None:
        """
        Cost sums substitution scores column-wise: e.g. A vs A is 0, A vs G is 48.
        """
        self.assertEqual(alignment_cost_from_strings("AA", "AA"), 0)
        self.assertEqual(alignment_cost_from_strings("AG", "AG"), 0)
        # A vs C (110) + C vs G (118) — two mismatch columns, no gaps.
        self.assertEqual(alignment_cost_from_strings("AC", "CG"), 110 + 118)

    def test_invalid_alignment_raises(self) -> None:
        """Unequal lengths or a column with two gaps are invalid and must raise."""
        with self.assertRaises(ValueError):
            alignment_cost_from_strings("A", "AA")
        with self.assertRaises(ValueError) as ctx:
            alignment_cost_from_strings("_", "_")
        self.assertIn("both gaps", str(ctx.exception).lower())


if __name__ == "__main__":
    unittest.main()
