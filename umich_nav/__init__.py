import os
import logging
from typing import Any, Dict, Optional, Tuple, Union

from .valhalla_client import ValhallaClient
from .route_store import save_route, load_route
from .navigation import Navigator
from .places import resolve_place

LatLon = Tuple[float, float]
LocationInput = Union[str, LatLon]

logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))

_default_valhalla_url = os.getenv("VALHALLA_URL", "http://localhost:8002")
_client_singleton: Optional[ValhallaClient] = None
_navigator_singleton: Optional[Navigator] = None


def _get_client() -> ValhallaClient:
    global _client_singleton
    if _client_singleton is None:
        _client_singleton = ValhallaClient(base_url=_default_valhalla_url)
    return _client_singleton


def _normalize_location(value: Optional[LocationInput]) -> Optional[LatLon]:
    if value is None:
        return None
    if isinstance(value, tuple) and len(value) == 2:
        lat, lon = float(value[0]), float(value[1])
        return (lat, lon)
    if isinstance(value, str):
        coords = resolve_place(value)
        if coords is None:
            raise ValueError(f"Unknown place name: {value}")
        return coords
    raise TypeError("Location must be (lat, lon) tuple or known place name string")


def generate_route(start: Optional[LocationInput], destination: LocationInput, *, costing: str = "auto") -> Dict[str, Any]:
    """
    Generate a route using the local Valhalla instance.

    - start: (lat, lon) or known place name; if None, use current GPS from Navigator when used interactively
    - destination: (lat, lon) or known place name
    - costing: Valhalla costing model, default 'auto'
    """
    client = _get_client()
    start_coords = _normalize_location(start)
    dest_coords = _normalize_location(destination)
    if dest_coords is None:
        raise ValueError("destination is required")

    if start_coords is None:
        raise ValueError("start is None. Provide (lat, lon) or place name, or use Navigator with a GPS provider.")

    return client.route(start_coords, dest_coords, costing=costing)


def set_route(route: Dict[str, Any]) -> Navigator:
    """Create and store a Navigator for subsequent update_position calls."""
    global _navigator_singleton
    client = _get_client()
    destination = (route.get("destination", {}).get("lat"), route.get("destination", {}).get("lon"))
    nav = Navigator(client, route, destination=destination)
    _navigator_singleton = nav
    return nav


def update_position(gps_data: Tuple[float, float]) -> Optional[str]:
    """Convenience function using the current Navigator (created via set_route)."""
    if _navigator_singleton is None:
        raise RuntimeError("Navigator not initialized. Call set_route(route) first.")
    return _navigator_singleton.update_position(gps_data)


__all__ = [
    "ValhallaClient",
    "Navigator",
    "generate_route",
    "save_route",
    "load_route",
    "resolve_place",
    "set_route",
    "update_position",
]
