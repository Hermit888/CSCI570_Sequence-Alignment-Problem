import time, sys, psutil
from pathlib import Path


# mismatch penalty matrix and gap penalty
alpha = {
    'A': {'A':0, 'C':110, 'G':48, 'T':94},
    'C': {'A':110, 'C':0, 'G':118, 'T':48},
    'G': {'A':48, 'C':118, 'G':0, 'T':110},
    'T': {'A':94, 'C':48, 'G':110, 'T':0}
}
delta = 30


def generate_string(base, indices):
    """
    generate the input string by inserting the current string into itself
    after the given index. each step doubles the length of the string.

    base: the base string
    indices: the list of insertion indices

    return the generated string
    """
    s = base
    for idx in indices:
        # insert a copy of s after position idx (0-indexed)
        s = s[:idx+1] + s + s[idx+1:]
    return s


def parse_input(input_path):
    """
    parse the input file and return the two generated strings

    file format:
        line 1       : base string s0
        next j lines : integer insertion indices for s0
        next line    : base string t0
        next k lines : integer insertion indices for t0

    input_path: the path to the input file

    return the two generated strings
    """
    with open(input_path, 'r') as f:
        lines = [line.strip() for line in f if line.strip()]

    # first base string
    s0 = lines[0]

    # collect s0's insertion indices until we hit a non-integer line (t0)
    i = 1
    s_indices = []
    while i < len(lines) and lines[i].lstrip('-').isdigit():
        s_indices.append(int(lines[i]))
        i += 1

    # second base string
    t0 = lines[i]
    # remaining lines are t0's insertion indices
    t_indices = [int(line) for line in lines[i+1:]]

    # generate the two strings
    x = generate_string(s0, s_indices)
    y = generate_string(t0, t_indices)

    # sanity check: len(sj) should be 2^j * len(s0)
    assert len(x) == (2 ** len(s_indices)) * len(s0)
    assert len(y) == (2 ** len(t_indices)) * len(t0)

    return x, y


def basic_dp(x, y, delta, alpha):
    """
    dynamic programming approach to solve sequence alignment problem

    x: the first string
    y: the second string
    delta: the gap penalty
    alpha: the mismatch penalty matrix

    return cost and two aligned sequences
    """
    m, n = len(x), len(y)

    # create dp table (m+1) * (n+1)
    dp = [[0] * (n+1) for _ in range(m+1)]

    # base cases: gaps only
    for i in range(1, m+1):
        dp[i][0] = delta * i
    for j in range(1, n+1):
        dp[0][j] = delta * j

    # fill the dp table
    for i in range(1, m+1):
        for j in range(1, n+1):
            dp[i][j] = min(
                dp[i-1][j] + delta,
                dp[i][j-1] + delta,
                dp[i-1][j-1] + alpha[x[i-1]][y[j-1]]
            )

    # traceback
    i, j = m, n
    align_x, align_y = [], []

    # traceback to get the aligned sequences
    while i > 0 and j > 0:
        if dp[i][j] == dp[i-1][j-1] + alpha[x[i-1]][y[j-1]]:
            align_x.append(x[i-1])
            align_y.append(y[j-1])
            i -= 1
            j -= 1
        elif dp[i][j] == dp[i-1][j] + delta:
            align_x.append(x[i-1])
            align_y.append('_')
            i -= 1
        else:
            align_x.append('_')
            align_y.append(y[j-1])
            j -= 1

    # if we reach the end of one string,
    # we need to add gaps for the remaining characters of the other string
    while i > 0:
        align_x.append(x[i-1])
        align_y.append('_')
        i -= 1
    # if we reach the end of one string,
    # we need to add gaps for the remaining characters of the other string
    while j > 0:
        align_x.append('_')
        align_y.append(y[j-1])
        j -= 1

    return dp[m][n], ''.join(reversed(align_x)), ''.join(reversed(align_y))


def process_memory():
    """
    get the current memory usage of the process in KB
    """
    process = psutil.Process()
    memory_info = process.memory_info()
    memory_consumed = int(memory_info.rss / 1024)
    return memory_consumed


def write_output(path, cost, align_x, align_y, time_ms, memory_kb):
    """
    write the output to a file
    """
    with open(path, 'w') as f:
        f.write(str(cost) + "\n")
        f.write(align_x + "\n")
        f.write(align_y + "\n")
        f.write(f"{time_ms}\n")
        f.write(f"{memory_kb}\n")


if __name__ == "__main__":
    # parse command line arguments
    if len(sys.argv) != 3:
        raise SystemExit("Usage: python3 basic.py <input_file> <output_file>")
    input_path = sys.argv[1]
    output_path = sys.argv[2]

    # parse input file and generate the two strings
    x, y = parse_input(input_path)

    # start of time
    start_time = time.time()

    # run the basic dp algorithm
    cost, align_x, align_y = basic_dp(x, y, delta, alpha)

    # end of time and memory
    end_time = time.time()
    memory_kb = process_memory()

    # calculate time usage
    time_ms = (end_time - start_time) * 1000

    # generate output file
    write_output(output_path, cost, align_x, align_y, time_ms, memory_kb)