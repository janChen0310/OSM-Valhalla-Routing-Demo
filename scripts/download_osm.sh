#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
CUSTOM_DIR="$ROOT_DIR/custom_files"
mkdir -p "$CUSTOM_DIR"

URL="https://download.geofabrik.de/north-america/us/michigan-latest.osm.pbf"
OUT="$CUSTOM_DIR/michigan-latest.osm.pbf"

echo "Downloading Michigan extract to $OUT"
curl -L "$URL" -o "$OUT"

echo "Done. Place additional city-sized extracts in custom_files if desired."
