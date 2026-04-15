#!/bin/bash

# create output directory if not exists
mkdir -p efficient_output

# loop through in1.txt to in15.txt
for i in {1..15}
do
    input_file="../Datapoints/in${i}.txt"
    output_file="efficient_output/out${i}.txt"

    if [ -f "$input_file" ]; then
        echo "Running efficient on $input_file..."
        python efficient.py "$input_file" "$output_file"
    else
        echo "Warning: $input_file not found, skipping..."
    fi
done

echo "All efficient runs completed."