"""
Tests for parsing the five-line submission output format (cost, alignments, time, memory).
"""

import unittest

from alignment_test_utils import parse_output_lines


class TestOutputFormat(unittest.TestCase):
    """Tests for parsing the five-line submission output format."""

    def test_parse_good_output(self) -> None:
        """
        A well-formed five-line string should parse into cost, alignments, time, and memory.

        Guards against accidental format drift in write_output helpers.
        """
        text = "1296\nAA\nCC\n1.5\n100.0\n"
        c, ax, ay, t, m = parse_output_lines(text)
        self.assertEqual(c, 1296)
        self.assertEqual(ax, "AA")
        self.assertEqual(ay, "CC")
        self.assertAlmostEqual(t, 1.5)
        self.assertAlmostEqual(m, 100.0)

    def test_parse_alignments_containing_gaps(self) -> None:
        """
        Lines 2 and 3 may contain '_' gap characters, as in real program output.

        Verifies parsing does not strip or alter alignment strings beyond line splitting.
        """
        text = (
            "240\n"
            "A_CG_T\n"
            "_ACGT_\n"
            "0.0048828125\n"
            "55152.0\n"
        )
        c, ax, ay, t, m = parse_output_lines(text)
        self.assertEqual(c, 240)
        self.assertEqual(ax, "A_CG_T")
        self.assertEqual(ay, "_ACGT_")
        self.assertAlmostEqual(t, 0.0048828125)
        self.assertAlmostEqual(m, 55152.0)

    def test_parse_invalid_line_count_raises(self) -> None:
        """Exactly five lines are required after strip(); otherwise parse_output_lines raises."""
        with self.assertRaises(ValueError) as ctx:
            parse_output_lines("1\n2\n3\n4\n")
        self.assertIn("5 lines", str(ctx.exception).lower())
        with self.assertRaises(ValueError):
            parse_output_lines("1\n2\n3\n4\n5\n6\n")


if __name__ == "__main__":
    unittest.main()
