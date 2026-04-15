import os
import matplotlib.pyplot as plt


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

    return len(x), len(y)


def parse_output(output_path):
    with open(output_path, "r") as f:
        lines = [line.strip() for line in f if line.strip()]

    # output format:
    # cost
    # aligned_x
    # aligned_y
    # time_ms
    # memory_kb

    time_ms = float(lines[3])
    memory_kb = float(lines[4])

    return time_ms, memory_kb


def main():
    basic_times = []
    efficient_times = []
    basic_memory = []
    efficient_memory = []
    problem_sizes = []

    for i in range(1, 16):
        input_file = f"../Datapoints/in{i}.txt"
        basic_file = f"basic_output/out{i}.txt"
        efficient_file = f"efficient_output/out{i}.txt"

        if not (os.path.exists(input_file)
                and os.path.exists(basic_file)
                and os.path.exists(efficient_file)):
            print(f"Skipping in{i}.txt (missing files)")
            continue

        # compute m + n
        m, n = parse_input(input_file)
        problem_sizes.append(m + n)

        # read basic results
        time_b, mem_b = parse_output(basic_file)
        basic_times.append(time_b)
        basic_memory.append(mem_b)

        # read efficient results
        time_e, mem_e = parse_output(efficient_file)
        efficient_times.append(time_e)
        efficient_memory.append(mem_e)

    # sort by problem size (important if inputs not ordered)
    combined = list(zip(problem_sizes,
                        basic_times,
                        efficient_times,
                        basic_memory,
                        efficient_memory))
    combined.sort()

    problem_sizes, basic_times, efficient_times, basic_memory, efficient_memory = zip(*combined)
    for i in range(len(basic_times)):
        print('{:.2f} {:.2f}'.format(basic_times[i], efficient_times[i]))
    print()
    for i in range(len(basic_times)):
        print('{:.2f} {:.2f}'.format(basic_memory[i], efficient_memory[i]))
    # -----------------------
    # Plot 1: Time comparison
    # -----------------------
    plt.figure()
    plt.plot(problem_sizes, basic_times, marker='o', label='Basic')
    plt.plot(problem_sizes, efficient_times, marker='o', label='Efficient')
    plt.xlabel("Problem Size (m + n)")
    plt.ylabel("CPU Time (ms)")
    plt.title("CPU Time vs Problem Size")
    plt.legend()
    plt.grid(True)
    plt.savefig("time_comparison.png")
    plt.show()

    # --------------------------
    # Plot 2: Memory comparison
    # --------------------------
    plt.figure()
    plt.plot(problem_sizes, basic_memory, marker='o', label='Basic')
    plt.plot(problem_sizes, efficient_memory, marker='o', label='Efficient')
    plt.xlabel("Problem Size (m + n)")
    plt.ylabel("Memory Usage (KB)")
    plt.title("Memory Usage vs Problem Size")
    plt.legend()
    plt.grid(True)
    plt.savefig("memory_comparison.png")
    plt.show()


if __name__ == "__main__":
    main()