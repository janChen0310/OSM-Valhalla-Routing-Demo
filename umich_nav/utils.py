import math
from typing import Sequence, Tuple

LatLon = Tuple[float, float]


def haversine_m(p1: LatLon, p2: LatLon) -> float:
    """Great-circle distance between two (lat, lon) in meters."""
    lat1, lon1 = map(math.radians, p1)
    lat2, lon2 = map(math.radians, p2)
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return 6371000.0 * c


def point_to_segment_distance_m(p: LatLon, a: LatLon, b: LatLon) -> float:
    """Perpendicular distance from point p to line segment ab (approx for small areas)."""
    lat = math.radians((p[0] + a[0] + b[0]) / 3.0)
    xp = (p[1]) * math.cos(lat)
    xa = (a[1]) * math.cos(lat)
    xb = (b[1]) * math.cos(lat)

    yp = p[0]
    ya = a[0]
    yb = b[0]

    dx = xb - xa
    dy = yb - ya
    if dx == 0 and dy == 0:
        return haversine_m(p, a)
    t = ((xp - xa) * dx + (yp - ya) * dy) / (dx * dx + dy * dy)
    t = max(0.0, min(1.0, t))
    xc = xa + t * dx
    yc = ya + t * dy
    return haversine_m((yp, xp / math.cos(lat)), (yc, xc / math.cos(lat)))


def min_distance_to_polyline_m(p: LatLon, coords: Sequence[LatLon]) -> float:
    min_d = float("inf")
    for i in range(len(coords) - 1):
        d = point_to_segment_distance_m(p, coords[i], coords[i + 1])
        if d < min_d:
            min_d = d
    return min_d
