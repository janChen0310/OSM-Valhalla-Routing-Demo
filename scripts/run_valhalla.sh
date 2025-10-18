#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
CUSTOM_DIR="$ROOT_DIR/custom_files"
mkdir -p "$CUSTOM_DIR"

# Place one or more *.osm.pbf files in custom_files/
# Example download script is scripts/download_osm.sh

# Remove existing container if present
docker rm -f valhalla >/dev/null 2>&1 || true

echo "Launching Valhalla on http://localhost:8002 using PBF(s) in $CUSTOM_DIR"
docker run -d --name valhalla \
  --ulimit nofile=1048576:1048576 \
  -p 8002:8002 \
  -v "$CUSTOM_DIR":/custom_files \
  --entrypoint bash \
  ghcr.io/gis-ops/docker-valhalla/valhalla:latest \
  -lc "valhalla_service /custom_files/valhalla.json 1"

echo "Container started. Use 'docker logs -f valhalla' to watch logs."
