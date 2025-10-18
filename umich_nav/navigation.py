import logging
from typing import Any, Dict, List, Optional, Tuple

from .utils import haversine_m, min_distance_to_polyline_m
from .valhalla_client import ValhallaClient

LatLon = Tuple[float, float]

logger = logging.getLogger(__name__)


class Navigator:
    """
    Tracks progress along a route and emits instructions.
    Triggers re-routing when off the planned path.
    """

    def __init__(
        self,
        client: ValhallaClient,
        route: Dict[str, Any],
        destination: Optional[LatLon] = None,
        arrival_radius_m: float = 25.0,
        off_route_radius_m: float = 50.0,
    ) -> None:
        self.client = client
        self.route = route
        self.arrival_radius_m = arrival_radius_m
        self.off_route_radius_m = off_route_radius_m
        self.coords: List[LatLon] = [(c["lat"], c["lon"]) for c in route["coordinates"]]
        self.waypoints: List[Dict[str, Any]] = route["waypoints"]
        self.current_waypoint_idx = 0
        self.destination: LatLon = destination if destination is not None else (
            route.get("destination", {}).get("lat"), route.get("destination", {}).get("lon")
        )
        if self.destination[0] is None or self.destination[1] is None:
            raise ValueError("Navigator requires a destination")

    def _rebuild_from_route(self, new_route: Dict[str, Any]) -> None:
        self.route = new_route
        self.coords = [(c["lat"], c["lon"]) for c in new_route["coordinates"]]
        self.waypoints = new_route["waypoints"]
        self.current_waypoint_idx = 0

    def update_position(self, gps_data: Tuple[float, float]) -> Optional[str]:
        """
        Process a GPS update. Returns the next instruction string when approaching a
        waypoint, 'Arrived at destination' upon arrival, 'Rerouting...' if off-route,
        or None otherwise.
        """
        lat, lon = gps_data
        current = (float(lat), float(lon))

        # Off-route detection: distance to polyline
        dist_to_line = min_distance_to_polyline_m(current, self.coords)
        if dist_to_line > self.off_route_radius_m:
            logger.warning("Off route by %.1f m; triggering re-route", dist_to_line)
            new_route = self.client.route(current, self.destination)
            self._rebuild_from_route(new_route)
            return "Rerouting..."

        # Arrival detection for the next waypoint
        if self.current_waypoint_idx < len(self.waypoints):
            next_wp = self.waypoints[self.current_waypoint_idx]
            wp_pos = (next_wp["lat"], next_wp["lon"])
            d = haversine_m(current, wp_pos)
            if d <= self.arrival_radius_m:
                instruction = next_wp.get("instruction") or "Continue"
                logger.info("Approaching waypoint %d: %s", self.current_waypoint_idx, instruction)
                self.current_waypoint_idx += 1
                return instruction

        # Final arrival
        if self.current_waypoint_idx >= len(self.waypoints):
            d_final = haversine_m(current, self.destination)
            if d_final <= self.arrival_radius_m:
                logger.info("Arrived at destination")
                return "Arrived at destination"

        return None
