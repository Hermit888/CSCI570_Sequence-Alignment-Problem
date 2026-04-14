"""
Memory-efficient sequence alignment using DP + divide-and-conquer.
"""

from __future__ import annotations

from dataclasses import dataclass
import sys
import time
from typing import Dict, List, Tuple
import psutil


GAP_PENALTY = 30
MISMATCH_COST: Dict[str, Dict[str, int]] = {
    "A": {"A": 0, "C": 110, "G": 48, "T": 94},
    "C": {"A": 110, "C": 0, "G": 118, "T": 48},
    "G": {"A": 48, "C": 118, "G": 0, "T": 110},
    "T": {"A": 94, "C": 48, "G": 110, "T": 0}
}


def generate_string(base: str, indices: List[int]) -> str:
    """Iteratively insert the current string into itself after each given index."""
    s = base
    for idx in indices:
        s = s[:idx + 1] + s + s[idx + 1:]
    return s


def parse_input(input_path: str) -> Tuple[str, str]:
    """Parse the input file and return the two generated sequences."""
    with open(input_path, "r", encoding="utf-8") as handle:
        lines = [line.strip() for line in handle if line.strip()]

    s0 = lines[0]

    # Collect s0's insertion indices until we hit a non-integer line (t0).
    i = 1
    s_indices: List[int] = []
    while i < len(lines) and lines[i].lstrip("-").isdigit():
        s_indices.append(int(lines[i]))
        i += 1

    t0 = lines[i]
    t_indices = [int(line) for line in lines[i + 1:]]

    x = generate_string(s0, s_indices)
    y = generate_string(t0, t_indices)

    # len(sj) should equal 2^j * len(s0)
    assert len(x) == (2 ** len(s_indices)) * len(s0)
    assert len(y) == (2 ** len(t_indices)) * len(t0)

    return x, y


@dataclass(frozen=True)
class AlignmentResult:
    cost: int
    aligned_x: str
    aligned_y: str


def substitution_cost(left: str, right: str) -> int:
    return MISMATCH_COST[left][right]


def last_row_costs(x: str, y: str) -> List[int]:
    """Returns DP costs for aligning x with every prefix of y using O(len(y)) space."""
    previous = [j * GAP_PENALTY for j in range(len(y) + 1)]

    for i, x_char in enumerate(x, start=1):
        current = [i * GAP_PENALTY] + [0] * len(y)
        for j, y_char in enumerate(y, start=1):
            match = previous[j - 1] + substitution_cost(x_char, y_char)
            delete = previous[j] + GAP_PENALTY
            insert = current[j - 1] + GAP_PENALTY
            current[j] = min(match, delete, insert)
        previous = current

    return previous


def basic_alignment(x: str, y: str) -> AlignmentResult:
    """Standard Needleman-Wunsch used for Hirschberg base cases."""
    rows = len(x) + 1
    cols = len(y) + 1
    dp = [[0] * cols for _ in range(rows)]

    for i in range(1, rows):
        dp[i][0] = i * GAP_PENALTY
    for j in range(1, cols):
        dp[0][j] = j * GAP_PENALTY

    for i in range(1, rows):
        x_char = x[i - 1]
        for j in range(1, cols):
            y_char = y[j - 1]
            dp[i][j] = min(
                dp[i - 1][j - 1] + substitution_cost(x_char, y_char),
                dp[i - 1][j] + GAP_PENALTY,
                dp[i][j - 1] + GAP_PENALTY
            )

    aligned_x: List[str] = []
    aligned_y: List[str] = []
    i = len(x)
    j = len(y)

    while i > 0 and j > 0:
        score = dp[i][j]
        if score == dp[i - 1][j - 1] + substitution_cost(x[i - 1], y[j - 1]):
            aligned_x.append(x[i - 1])
            aligned_y.append(y[j - 1])
            i -= 1
            j -= 1
        elif score == dp[i - 1][j] + GAP_PENALTY:
            aligned_x.append(x[i - 1])
            aligned_y.append("_")
            i -= 1
        else:
            aligned_x.append("_")
            aligned_y.append(y[j - 1])
            j -= 1

    while i > 0: # Deal with the remaining x
        aligned_x.append(x[i - 1])
        aligned_y.append("_")
        i -= 1

    while j > 0: # Deal with the remaining y
        aligned_x.append("_")
        aligned_y.append(y[j - 1])
        j -= 1

    aligned_x.reverse()
    aligned_y.reverse()

    return AlignmentResult(
        cost=dp[-1][-1],
        aligned_x="".join(aligned_x),
        aligned_y="".join(aligned_y)
    )


def hirschberg_alignment(x: str, y: str) -> AlignmentResult:
    """Computes one optimal alignment in O(len(x) * len(y)) time and O(len(y)) space."""
    if not x:
        return AlignmentResult(len(y) * GAP_PENALTY, "_" * len(y), y)
    if not y:
        return AlignmentResult(len(x) * GAP_PENALTY, x, "_" * len(x))
    if len(x) == 1 or len(y) == 1:
        return basic_alignment(x, y)

    x_mid = len(x) // 2

    left_costs = last_row_costs(x[:x_mid], y)
    right_costs = last_row_costs(x[x_mid:][::-1], y[::-1])

    split_y = 0
    best_cost = None
    y_len = len(y)
    for j in range(y_len + 1):
        candidate = left_costs[j] + right_costs[y_len - j]
        if best_cost is None or candidate < best_cost:
            best_cost = candidate
            split_y = j

    left_result = hirschberg_alignment(x[:x_mid], y[:split_y])
    right_result = hirschberg_alignment(x[x_mid:], y[split_y:])

    aligned_x = left_result.aligned_x + right_result.aligned_x
    aligned_y = left_result.aligned_y + right_result.aligned_y

    return AlignmentResult(
        cost=left_result.cost + right_result.cost,
        aligned_x=aligned_x,
        aligned_y=aligned_y
    )


def memory_efficient_alignment(x: str, y: str) -> Tuple[int, str, str]:
    result = hirschberg_alignment(x, y)
    return result.cost, result.aligned_x, result.aligned_y


def process_memory() -> int:
    process = psutil.Process()
    memory_info = process.memory_info()
    memory_consumed = int(memory_info.rss / 1024)
    return memory_consumed


def write_output_file(output_path: str, cost: int, aligned_x: str, aligned_y: str, elapsed_ms: float, memory_kb: int) -> None:
    with open(output_path, "w", encoding="utf-8") as handle:
        handle.write(f"{cost}\n")
        handle.write(f"{aligned_x}\n")
        handle.write(f"{aligned_y}\n")
        handle.write(f"{elapsed_ms}\n")
        handle.write(f"{memory_kb}\n")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit(
            "Usage: python3 efficient.py <input_file> <output_file>"
        )

    input_path = sys.argv[1]
    output_path = sys.argv[2]

    # Parse input file and generate the two sequences.
    x, y = parse_input(input_path)

    # Run the memory-efficient alignment with time measurement.
    start_time = time.time()
    cost, aligned_x, aligned_y = memory_efficient_alignment(x, y)
    elapsed_ms = (time.time() - start_time) * 1000
    memory_kb = process_memory()

    write_output_file(output_path, cost, aligned_x, aligned_y, elapsed_ms, memory_kb)