"""
Tests for input string generation: generate_string and parse_input (course spec).

Each insertion step copies the current string into itself immediately after the given
0-based index; after j steps, length is 2^j * len(s0).
"""

from __future__ import annotations

import unittest
from pathlib import Path

from alignment_test_utils import get_basic_module, write_temp_input


def _generate_string(base: str, indices: list[int]) -> str:
    """Delegate to basic.generate_string (same algorithm as efficient.generate_string)."""
    return get_basic_module().generate_string(base, indices)


def _parse_input(path: str) -> tuple[str, str]:
    return get_basic_module().parse_input(path)


class TestGenerateString(unittest.TestCase):
    """Unit tests for iterative insertion (generate_string)."""

    def test_empty_indices_returns_base(self) -> None:
        """With no insertion steps, the result equals the base string."""
        self.assertEqual(_generate_string("ACTG", []), "ACTG")
        self.assertEqual(_generate_string("A", []), "A")

    def test_each_step_doubles_length(self) -> None:
        """After j insertions, length equals 2^j * len(base)."""
        base = "AGTC"
        for j in range(0, 6):
            indices = [0] * j
            got = _generate_string(base, indices)
            self.assertEqual(
                len(got),
                (2**j) * len(base),
                msg=f"j={j} insertions at index 0",
            )

    def test_pdf_example_actg_then_tacg(self) -> None:
        """
        Handout example: ACTG with insertions after indices 3, 6, then 1;
        TACG with insertions after 1, 2, then 9.
        """
        x = _generate_string("ACTG", [3, 6, 1])
        y = _generate_string("TACG", [1, 2, 9])
        self.assertEqual(x, "ACACTGACTACTGACTGGTGACTACTGACTGG")
        self.assertEqual(y, "TATTATACGCTATTATACGCGACGCGGACGCG")
        self.assertEqual(len(x), 32)
        self.assertEqual(len(y), 32)

    def test_basic_and_efficient_generate_string_agree(self) -> None:
        """efficient.generate_string must match basic for the same inputs."""
        basic = get_basic_module()
        import efficient as eff

        cases: list[tuple[str, list[int]]] = [
            ("ACTG", [3, 6, 1]),
            ("TACG", [1, 2, 9]),
            ("A", []),
            ("CC", [0, 1]),
        ]
        for base, idx in cases:
            with self.subTest(base=base, indices=idx):
                self.assertEqual(
                    basic.generate_string(base, idx),
                    eff.generate_string(base, idx),
                )


class TestParseInput(unittest.TestCase):
    """parse_input reads a file and must produce the same strings as generate_string."""

    def test_parse_matches_generate_for_two_line_file(self) -> None:
        """Minimal file: s0, t0 only — no index lines."""
        path = write_temp_input("ACTG\nTACG\n")
        try:
            x, y = _parse_input(str(path))
            self.assertEqual(x, _generate_string("ACTG", []))
            self.assertEqual(y, _generate_string("TACG", []))
        finally:
            Path(path).unlink(missing_ok=True)

    def test_parse_matches_pdf_style_file(self) -> None:
        """Multi-line file with indices for both strings matches composed generate_string."""
        body = (
            "ACTG\n"
            "3\n6\n1\n"
            "TACG\n"
            "1\n2\n9\n"
        )
        path = write_temp_input(body)
        try:
            x, y = _parse_input(str(path))
            self.assertEqual(x, _generate_string("ACTG", [3, 6, 1]))
            self.assertEqual(y, _generate_string("TACG", [1, 2, 9]))
        finally:
            Path(path).unlink(missing_ok=True)

    def test_parse_sample_input1_file(self) -> None:
        """If SampleTestCases/input1.txt exists, parsed strings match generate_string from its lines."""
        from alignment_test_utils import SAMPLE_DIR

        inp = SAMPLE_DIR / "input1.txt"
        if not inp.is_file():
            self.skipTest("SampleTestCases/input1.txt not found")
        x, y = _parse_input(str(inp))
        # input1.txt: s0 ACTG, indices 3,6,1,1 — t0 TACG, indices 1,2,9,2
        self.assertEqual(x, _generate_string("ACTG", [3, 6, 1, 1]))
        self.assertEqual(y, _generate_string("TACG", [1, 2, 9, 2]))


if __name__ == "__main__":
    unittest.main()
