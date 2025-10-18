import json
import logging
from typing import Any, Dict, List, Tuple

import requests
import polyline as polyline_lib

LatLon = Tuple[float, float]

logger = logging.getLogger(__name__)


class ValhallaClient:
    """Thin HTTP client for a local Valhalla server."""

    def __init__(self, *, base_url: str = "http://localhost:8002") -> None:
        self.base_url = base_url.rstrip("/")

    def route(self, start: LatLon, dest: LatLon, *, costing: str = "auto") -> Dict[str, Any]:
        """
        Request a route and parse waypoints and instructions.
        Returns a structured dictionary suitable for storage and navigation.
        """
        data = {
            "locations": [
                {"lat": start[0], "lon": start[1]},
                {"lat": dest[0], "lon": dest[1]},
            ],
            "costing": costing,
            "directions_options": {"units": "kilometers"},
        }

        url = f"{self.base_url}/route"
        logger.info("Requesting route from %s to %s via %s", start, dest, url)
        resp = requests.post(url, json=data, timeout=30)
        resp.raise_for_status()
        resp_json = resp.json()

        trip = resp_json.get("trip", {})
        legs: List[Dict[str, Any]] = trip.get("legs", [])
        if not legs:
            raise RuntimeError("Valhalla response contained no legs")

        leg = legs[0]
        shape = leg.get("shape")
        if not shape:
            raise RuntimeError("Valhalla leg missing shape")

        # Decode polyline; Valhalla uses polyline6 precision
        coords: List[Tuple[float, float]] = polyline_lib.decode(shape, precision=6)

        maneuvers: List[Dict[str, Any]] = leg.get("maneuvers", [])
        waypoints: List[Dict[str, Any]] = []
        for m in maneuvers:
            idx = m.get("begin_shape_index", 0)
            instruction = m.get("instruction", "")
            if 0 <= idx < len(coords):
                lat, lon = coords[idx]
                waypoints.append({
                    "index": idx,
                    "lat": lat,
                    "lon": lon,
                    "instruction": instruction,
                })

        result: Dict[str, Any] = {
            "coordinates": [{"lat": lat, "lon": lon} for lat, lon in coords],
            "distance_m": float(trip.get("summary", {}).get("length", 0.0)) * 1000.0,
            "duration_s": float(trip.get("summary", {}).get("time", 0.0)),
            "waypoints": waypoints,
            "destination": {"lat": dest[0], "lon": dest[1]},
            "start": {"lat": start[0], "lon": start[1]},
        }
        return result
