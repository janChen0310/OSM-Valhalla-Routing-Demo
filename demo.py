#!/usr/bin/env python3
import argparse
import os
import time
import math
from typing import Tuple

from umich_nav import generate_route, save_route, load_route, set_route, update_position


def parse_location(arg: str):
    if "," in arg:
        lat, lon = arg.split(",", 1)
        return (float(lat.strip()), float(lon.strip()))
    return arg  # treat as place name


def main():
    parser = argparse.ArgumentParser(description="U-M North Campus offline routing demo (Valhalla)")
    parser.add_argument("destination", type=str, help="Destination 'Place Name' or 'lat,lon'")
    parser.add_argument("--start", type=str, default="Pierpont Commons", help="Start 'Place Name' or 'lat,lon'")
    parser.add_argument("--outfile", type=str, default="route.json", help="Where to save the route JSON")
    parser.add_argument("--plot", type=str, default="route_plot.png", help="Path to save the route visualization PNG")
    parser.add_argument("--speed", type=float, default=0.5, help="Simulation speed factor (higher = faster)")
    parser.add_argument("--interactive", action="store_true", help="Animate user movement interactively")
    parser.add_argument("--costing", type=str, default="pedestrian", choices=["auto","pedestrian","bicycle"], help="Valhalla costing model")
    args = parser.parse_args()

    # Configure matplotlib backend after parsing flags
    import matplotlib
    if args.interactive:
        # Try to use an interactive backend if none set
        if not os.environ.get("MPLBACKEND"):
            try:
                matplotlib.use("TkAgg")
            except Exception:
                # Fallback to default without forcing
                pass
    else:
        matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    start = parse_location(args.start)
    dest = parse_location(args.destination)

    route = generate_route(start, dest, costing=args.costing)
    save_route(route, args.outfile)
    print(f"Route saved to {args.outfile}. Distance: {route['distance_m']:.0f} m")

    nav = set_route(route)

    coords = [(c["lat"], c["lon"]) for c in route["coordinates"]]

    # Local equirectangular projection to meters centered on route centroid
    lats = [lat for lat, lon in coords]
    lons = [lon for lat, lon in coords]
    lat0 = sum(lats) / len(lats)
    lon0 = sum(lons) / len(lons)
    lat0_rad = math.radians(lat0)
    R = 6371000.0

    def project(lat: float, lon: float) -> Tuple[float, float]:
        x = R * math.cos(lat0_rad) * math.radians(lon - lon0)
        y = R * math.radians(lat - lat0)
        return x, y

    route_xs, route_ys = zip(*[project(lat, lon) for lat, lon in coords])

    fig, ax = plt.subplots(figsize=(6, 6))
    ax.plot(route_xs, route_ys, "k-", lw=2, label="Route")

    # Waypoints (maneuvers)
    wps = route.get("waypoints", [])
    if wps:
        wp_xy = [project(w["lat"], w["lon"]) for w in wps]
        wp_xs = [x for x, y in wp_xy]
        wp_ys = [y for x, y in wp_xy]
        ax.scatter(wp_xs, wp_ys, c="orange", s=25, zorder=3, label="Waypoints")

    # Start and Destination
    if route.get("start"):
        s = route["start"]
        sx, sy = project(s["lat"], s["lon"])
        ax.scatter([sx], [sy], c="green", s=40, marker="o", zorder=4, label="Start")
    if route.get("destination"):
        d = route["destination"]
        dx, dy = project(d["lat"], d["lon"])
        ax.scatter([dx], [dy], c="red", s=40, marker="x", zorder=4, label="Destination")

    ax.set_xlabel("x (m)")
    ax.set_ylabel("y (m)")
    ax.set_title("Route and simulated user positions (local meters)")
    ax.legend(loc="best")

    # Adjust limits with padding in meters
    if route_xs and route_ys:
        pad_x = max(1.0, (max(route_xs) - min(route_xs)) * 0.1)
        pad_y = max(1.0, (max(route_ys) - min(route_ys)) * 0.1)
        ax.set_xlim(min(route_xs) - pad_x, max(route_xs) + pad_x)
        ax.set_ylim(min(route_ys) - pad_y, max(route_ys) + pad_y)
    ax.set_aspect('equal', adjustable='box')

    # Prepare user path elements
    user_path_xs: list[float] = []
    user_path_ys: list[float] = []
    path_line, = ax.plot([], [], "b-", lw=1.5, alpha=0.7, label="User path")
    user_marker = ax.scatter([], [], c="blue", s=30, zorder=5)

    if args.interactive:
        plt.ion()

    # Simulation loop
    for i, pos in enumerate(coords):
        x, y = project(pos[0], pos[1])
        user_path_xs.append(x)
        user_path_ys.append(y)

        # Update navigator
        instr = update_position(pos)
        if instr:
            print(instr)
            if instr == "Arrived at destination":
                # Still update visuals one last time
                pass

        # Update visuals
        path_line.set_data(user_path_xs, user_path_ys)
        user_marker.set_offsets([[x, y]])

        if args.interactive:
            plt.pause(max(0.01, 0.05 / args.speed))
        else:
            time.sleep(max(0.01, 0.1 / args.speed))

        if instr == "Arrived at destination":
            break

    fig.tight_layout()
    fig.savefig(args.plot, dpi=160)
    print(f"Saved visualization to {args.plot}")

    if args.interactive:
        plt.ioff()
        plt.show()


if __name__ == "__main__":
    main()
