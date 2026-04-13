"""Memory-efficient sequence alignment using DP + divide-and-conquer.

This module is limited to the memory-efficient alignment step. It assumes the
two full input sequences have already been generated elsewhere.
"""

from __future__ import annotations

from dataclasses import dataclass
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


@dataclass(frozen=True)
class AlignmentResult:
    cost: int
    aligned_x: str
    aligned_y: str


def substitution_cost(left: str, right: str) -> int:
    return MISMATCH_COST[left][right]


def alignment_cost(aligned_x: str, aligned_y: str) -> int:
    total = 0
    for left, right in zip(aligned_x, aligned_y):
        if left == "_" or right == "_":
            total += GAP_PENALTY
        else:
            total += substitution_cost(left, right)
    return total


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


def time_wrapper(x: str, y: str) -> Tuple[int, str, str, float]:
    start_time = time.time()
    cost, aligned_x, aligned_y = memory_efficient_alignment(x, y)
    end_time = time.time()
    time_taken = (end_time - start_time) * 1000
    return cost, aligned_x, aligned_y, time_taken


def process_input_file(input_path: str) -> Tuple[int, str, str, float, int]:
    with open(input_path, "r", encoding="utf-8") as handle:
        lines = [line.strip() for line in handle if line.strip()]

    if len(lines) < 2:
        raise ValueError("Input file must contain two generated sequences.")

    x, y = lines[0], lines[1]

    cost, aligned_x, aligned_y, elapsed_ms = time_wrapper(x, y)
    memory_kb = process_memory()

    return cost, aligned_x, aligned_y, elapsed_ms, memory_kb


def write_output_file(output_path: str, result: Tuple[int, str, str, float, int]) -> None:
    cost, aligned_x, aligned_y, elapsed_ms, memory_kb = result
    with open(output_path, "w", encoding="utf-8") as handle:
        handle.write(f"{cost}\n")
        handle.write(f"{aligned_x}\n")
        handle.write(f"{aligned_y}\n")
        handle.write(f"{elapsed_ms}\n")
        handle.write(f"{memory_kb}\n")


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 3:
        raise SystemExit(
            "Usage: python3 efficient.py <input_file> <output_file>"
        )

    result = process_input_file(sys.argv[1])
    write_output_file(sys.argv[2], result)
