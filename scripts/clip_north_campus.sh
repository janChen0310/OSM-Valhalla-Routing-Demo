#!/usr/bin/env bash
set -euo pipefail

# Requires: osmium-tool (sudo apt-get install osmium-tool)
# Usage: scripts/clip_north_campus.sh custom_files/michigan-latest.osm.pbf

if [ $# -lt 1 ]; then
  echo "Usage: $0 <input.osm.pbf>"
  exit 1
fi

IN="$1"
OUT_DIR="$(cd "$(dirname "$0")/.." && pwd)/custom_files"
mkdir -p "$OUT_DIR"
OUT="$OUT_DIR/north-campus.osm.pbf"

# North Campus bounding box (approx): west,south,east,north
# Covers Pierpont, Duderstadt, EECS, BBB, FXB, GGB, LEC, etc.
BBOX="-83.7240,42.2870,-83.7050,42.2980"

echo "Clipping $IN to North Campus bbox $BBOX -> $OUT"
osmium extract -b $BBOX -o "$OUT" "$IN"

echo "Wrote $OUT"
