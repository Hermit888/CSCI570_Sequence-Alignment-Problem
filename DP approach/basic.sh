#!/bin/bash
# Usage: ./basic.sh <input_file> <output_file>
# Runs the O(mn) dynamic programming sequence alignment (Python 3).

set -euo pipefail

if [ "$#" -ne 2 ]; then
  echo "Usage: $0 <input_file> <output_file>" >&2
  exit 1
fi

exec python3 basic.py "$1" "$2"
