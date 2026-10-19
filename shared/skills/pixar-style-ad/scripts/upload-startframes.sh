#!/bin/bash
# Prepare N copies of each storyboard still for MiniMax H3 image-to-video.
# Writes a TSV mapping (slot, variation_index, local-path-or-url) to
# $RUN_DIR/references/seedance-startframes.txt for downstream use.
#
# Usage: ./upload-startframes.sh <variations-per-still>
# Reads still list from STDIN:
#   <slot>::<local-still-path>
#
# Example:
#   cat <<EOF | ./upload-startframes.sh 3
#   pain-cpm::stills/batch-a/pain-cpm.png
#   brent-reveal::stills/brent-final.png
#   EOF
set -euo pipefail

N="$1"
MAP="$RUN_DIR/references/seedance-startframes.txt"
mkdir -p "$RUN_DIR/references"
: > "$MAP"

while IFS=$'\n' read -r line; do
  [[ -z "$line" || "$line" =~ ^# ]] && continue
  slot="${line%%::*}"
  path="${line#*::}"
  # Resolve relative paths against RUN_DIR
  [[ "$path" != /* ]] && path="$RUN_DIR/$path"
  echo "preparing $N copies of $slot..." >&2
  for i in $(seq 1 "$N"); do
    echo "$slot:$i:$path" >> "$MAP"
  done
done

echo "Wrote $MAP ($(wc -l < "$MAP") entries)"
