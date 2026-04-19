#!/bin/bash
# Usage: ./efficient.sh <input_file> <output_file> [<trivial_size>]
# Runs the memory-efficient Hirschberg alignment (Python 3).
# Optional third argument is the trivial subproblem threshold (default: 1 in efficient.py).

set -euo pipefail

if [ "$#" -lt 2 ] || [ "$#" -gt 3 ]; then
  echo "Usage: $0 <input_file> <output_file> [<trivial_size>]" >&2
  exit 1
fi

if [ "$#" -eq 3 ]; then
  exec python3 efficient.py "$1" "$2" "$3"
else
  exec python3 efficient.py "$1" "$2"
fi
