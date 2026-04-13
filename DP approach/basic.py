import time, psutil 
from pathlib import Path


# mismatch penalty matrix and gap penalty
alpha = {
    'A': {'A':0, 'C':110, 'G':48, 'T':94},
    'C': {'A':110, 'C':0, 'G':118, 'T':48},
    'G': {'A':48, 'C':118, 'G':0, 'T':110},
    'T': {'A':94, 'C':48, 'G':110, 'T':0}
}
delta = 30

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
        f.write(f"{time_ms:.3f}\n")
        f.write(f"{memory_kb:.3f}")


def main_dp(x, y, delta, alpha, idx):
    """
    main function to run the basic dp approach

    x: the first string
    y: the second string
    delta: the gap penalty
    alpha: the mismatch penalty matrix
    idx: the index of the input case
    """
    # start of time and memory
    start_mem = process_memory()
    start_time = time.time()

    cost, align_x, align_y = basic_dp(x, y, delta, alpha)

    # end of time and memory
    end_time = time.time()
    end_mem = process_memory()

    # calculate time and memory usage
    time_ms = (end_time - start_time) * 1000
    memory_kb = max(0, end_mem - start_mem)

    # get currect directory
    curr_dir = Path(__file__).resolve().parent
    # output directory
    output_dir = curr_dir / 'output'
    # if don't exist, create it
    output_dir.mkdir(exist_ok=True)

    # create output file
    path = output_dir / f'output{idx}.txt'

    # generate output file
    write_output(path, cost, align_x, align_y, time_ms, memory_kb)
