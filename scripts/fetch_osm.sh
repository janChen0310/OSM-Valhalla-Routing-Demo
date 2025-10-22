#!/usr/bin/env bash
set -euo pipefail

# One-step helper to fetch Michigan OSM and clip to North Campus.
# Requires: curl, osmium-tool

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
CUSTOM_DIR="$ROOT_DIR/custom_files"
mkdir -p "$CUSTOM_DIR"

PBF_URL="https://download.geofabrik.de/north-america/us/michigan-latest.osm.pbf"
MI_PBF="$CUSTOM_DIR/michigan-latest.osm.pbf"
NC_PBF="$CUSTOM_DIR/north-campus.osm.pbf"

echo "[1/2] Downloading Michigan extract -> $MI_PBF"
curl -L "$PBF_URL" -o "$MI_PBF"

echo "[2/2] Clipping to North Campus bbox -> $NC_PBF"
# North Campus bbox (west,south,east,north)
BBOX="-83.7240,42.2870,-83.7050,42.2980"
osmium extract -b "$BBOX" -o "$NC_PBF" "$MI_PBF"

echo "Done. Files ready in $CUSTOM_DIR"

