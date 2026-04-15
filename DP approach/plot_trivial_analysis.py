import os
import matplotlib.pyplot as plt


TRIVIAL_SIZES = [1, 10, 50, 100, 200, 500]


def generate_string(base, indices):
    s = base
    for idx in indices:
        s = s[:idx + 1] + s + s[idx + 1:]
    return s


def parse_input(input_path):
    with open(input_path, "r") as f:
        lines = [line.strip() for line in f if line.strip()]

    s0 = lines[0]
    i = 1
    s_indices = []

    while i < len(lines) and lines[i].lstrip("-").isdigit():
        s_indices.append(int(lines[i]))
        i += 1

    t0 = lines[i]
    t_indices = [int(line) for line in lines[i + 1:]]

    x = generate_string(s0, s_indices)
    y = generate_string(t0, t_indices)

    return len(x) + len(y)


def parse_output(output_path):
    with open(output_path, "r") as f:
        lines = [line.strip() for line in f if line.strip()]

    time_ms = float(lines[3])
    memory_kb = float(lines[4])

    return time_ms, memory_kb


def main():
    # 先算 problem sizes
    problem_sizes = []
    for i in range(1, 16):
        input_file = f"in{i}.txt"
        if os.path.exists(input_file):
            size = parse_input(input_file)
            problem_sizes.append(size)

    # 排序
    problem_sizes.sort()

    # -------- 时间图 --------
    plt.figure()

    for T in TRIVIAL_SIZES:
        times = []
        sizes = []

        for i in range(1, 16):
            output_file = f"efficient_trivial_tests/trivial_{T}/out{i}.txt"
            input_file = f"../Datapoints/in{i}.txt"

            if os.path.exists(output_file) and os.path.exists(input_file):
                size = parse_input(input_file)
                time_ms, _ = parse_output(output_file)
                sizes.append(size)
                times.append(time_ms)

        combined = sorted(zip(sizes, times))
        sizes, times = zip(*combined)

        plt.plot(sizes, times, marker='o', label=f"trivial={T}")

    plt.xlabel("Problem Size (m + n)")
    plt.ylabel("CPU Time (ms)")
    plt.title("Efficient Algorithm: Time vs Problem Size")
    plt.legend()
    plt.grid(True)
    plt.savefig("trivial_time_comparison.png")
    plt.show()

    # -------- 内存图 --------
    plt.figure()

    for T in TRIVIAL_SIZES:
        memories = []
        sizes = []

        for i in range(1, 16):
            output_file = f"efficient_trivial_tests/trivial_{T}/out{i}.txt"
            input_file = f"../Datapoints/in{i}.txt"

            if os.path.exists(output_file) and os.path.exists(input_file):
                size = parse_input(input_file)
                _, memory_kb = parse_output(output_file)
                sizes.append(size)
                memories.append(memory_kb)

        combined = sorted(zip(sizes, memories))
        sizes, memories = zip(*combined)

        plt.plot(sizes, memories, marker='o', label=f"trivial={T}")

    plt.xlabel("Problem Size (m + n)")
    plt.ylabel("Memory Usage (KB)")
    plt.title("Efficient Algorithm: Memory vs Problem Size")
    plt.legend()
    plt.grid(True)
    plt.savefig("trivial_memory_comparison.png")
    plt.show()


if __name__ == "__main__":
    main()