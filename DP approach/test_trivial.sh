#!/bin/bash

# 你想测试的 trivial sizes
TRIVIAL_SIZES=(1 10 50 100 200 500)

# 创建总目录
mkdir -p efficient_trivial_tests

for T in "${TRIVIAL_SIZES[@]}"
do
    echo "Testing trivial size = $T"

    OUTPUT_DIR="efficient_trivial_tests/trivial_${T}"
    mkdir -p "$OUTPUT_DIR"

    for i in {1..15}
    do
        INPUT_FILE="../Datapoints/in${i}.txt"
        OUTPUT_FILE="${OUTPUT_DIR}/out${i}.txt"

        if [ -f "$INPUT_FILE" ]; then
            python efficient.py "$INPUT_FILE" "$OUTPUT_FILE" "$T"
        else
            echo "Missing $INPUT_FILE"
        fi
    done

    echo "Finished trivial size = $T"
done

echo "All tests completed."