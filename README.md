# U-M North Campus Offline Navigation (Valhalla + OSM)

Offline routing and simple navigation for the University of Michigan North Campus using a local Valhalla server and OpenStreetMap data.

## Setup

1) Create a virtual environment and install dependencies:

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

2) Download the Michigan PBF and clip to North Campus (recommended):

```bash
# Requires osmium-tool
bash scripts/fetch_osm.sh
```

3) Build Valhalla config and tiles

Generate `custom_files/valhalla.json` and routing tiles (Docker required):

```bash
bash scripts/build_valhalla.sh
# Or specify a different extract:
# bash scripts/build_valhalla.sh custom_files/michigan-latest.osm.pbf
```

This creates:
- `custom_files/valhalla.json`
- `custom_files/valhalla_tiles/` (directory tiles)
- Optionally `custom_files/valhalla_tiles.tar` (not used by default)

Note: The config is set to prefer directory tiles to avoid file-descriptor issues. If you want to use the tar extract, set `mjolnir.tile_extract` in `valhalla.json` to `/custom_files/valhalla_tiles.tar`.

4) Run Valhalla locally with your PBF(s):

- Option A (script):
```bash
bash scripts/run_valhalla.sh
```

- Option B (docker compose):
```bash
docker compose up -d
```

Either method serves at `http://localhost:8002`.

## Demo

Simulate a route and print turn-by-turn instructions:

```bash
VALHALLA_URL=http://localhost:8002 python demo.py "Duderstadt Center" --start "Pierpont Commons"
```

Coordinates are also accepted as `lat,lon` (e.g., `"42.29274,-83.71649"`).

## Python API

- `umich_nav.generate_route(start, destination)`
  - `(lat, lon)` or place names (see `umich_nav/places.py`).
  - Returns a dict with:
    - `coordinates`: list of `{lat, lon}` points
    - `waypoints`: list of `{lat, lon, instruction}`
    - `distance_m`, `duration_s`, `start`, `destination`
- `umich_nav.save_route(route, filename)` / `umich_nav.load_route(filename)`
- `umich_nav.set_route(route)` to initialize a navigator
- `umich_nav.update_position((lat, lon))` → `str | None`
  - Emits next instruction when near a waypoint
  - Returns `"Rerouting..."` if off-route
  - Returns `"Arrived at destination"` on arrival

## Notes

- Uses local Valhalla only; no online services required after downloading PBF.
- Off-route detection uses point-to-polyline distance; tune thresholds in `Navigator`.
- Default costing is `auto`; pass other Valhalla costing models as needed.

## References

- Simple Docker setup and Python example: [blog.rtwilson.com](https://blog.rtwilson.com/simple-self-hosted-openstreetmap-routing-using-valhalla-and-docker/)
- Valhalla overview and components: [DeepWiki Valhalla Overview](https://deepwiki.com/valhalla/valhalla/1-overview)
- Valhalla repository: [github.com/valhalla/valhalla](https://github.com/valhalla/valhalla/tree/master)
- Official docs: [valhalla.github.io](https://valhalla.github.io/valhalla/)
