#!/usr/bin/env bash
set -euo pipefail

# Build valhalla.json and tiles using the docker image tooling.
# Requires: docker, OSM PBF at custom_files/north-campus.osm.pbf (or any *.osm.pbf)

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
CUSTOM_DIR="$ROOT_DIR/custom_files"
PBF="${1:-}"

if [ -z "${PBF}" ]; then
  # default to north-campus if present, otherwise any pbf in custom_files
  if [ -f "$CUSTOM_DIR/north-campus.osm.pbf" ]; then
    PBF="$CUSTOM_DIR/north-campus.osm.pbf"
  else
    PBF_CANDIDATE=$(ls -1 "$CUSTOM_DIR"/*.osm.pbf 2>/dev/null | head -n1 || true)
    if [ -z "$PBF_CANDIDATE" ]; then
      echo "No PBF provided and none found in $CUSTOM_DIR. Run scripts/fetch_osm.sh first." >&2
      exit 1
    fi
    PBF="$PBF_CANDIDATE"
  fi
fi

mkdir -p "$CUSTOM_DIR/valhalla_tiles"

echo "Using PBF: $PBF"
PBF_BASENAME="$(basename "$PBF")"
HOST_UID="$(id -u)"
HOST_GID="$(id -g)"

# Generate config and build tiles inside the Valhalla container environment
docker run --rm \
  -v "$CUSTOM_DIR":/custom_files \
  -u 0:0 \
  -e HOST_UID="$HOST_UID" -e HOST_GID="$HOST_GID" \
  --entrypoint bash \
  ghcr.io/gis-ops/docker-valhalla/valhalla:latest \
  -lc '
    set -euo pipefail
    CFG=/custom_files/valhalla.json
    TILE_DIR=/custom_files/valhalla_tiles
    PBF_IN="/custom_files/'$PBF_BASENAME'"

    echo "Generating valhalla.json -> $CFG"
    valhalla_build_config \
      --mjolnir-tile-dir "$TILE_DIR" \
      --mjolnir-timezone /custom_files/timezone_data/timezones.sqlite \
      --mjolnir-admin /custom_files/admin_data/admins.sqlite \
      > "$CFG"

    echo "Building tiles..."
    valhalla_build_tiles -c "$CFG" "$PBF_IN"

    # (Optional) Build extract tar if you later want to use tile_extract
    # valhalla_build_extract -c "$CFG" -v || true

    # Ensure host user owns generated files
    if [ -n "${HOST_UID:-}" ] && [ -n "${HOST_GID:-}" ]; then
      chown -R "$HOST_UID":"$HOST_GID" /custom_files/valhalla.json /custom_files/valhalla_tiles || true
      [ -f /custom_files/valhalla_tiles.tar ] && chown "$HOST_UID":"$HOST_GID" /custom_files/valhalla_tiles.tar || true
    fi
  '

echo "Done. Config at $CUSTOM_DIR/valhalla.json; tiles in $CUSTOM_DIR/valhalla_tiles"

