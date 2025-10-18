#!/usr/bin/env python3
import argparse
import math

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from umich_nav.places import _PLACES


def main():
    parser = argparse.ArgumentParser(description="Plot predefined places from umich_nav.places")
    parser.add_argument("--out", type=str, default="places.png", help="Output PNG path")
    args = parser.parse_args()

    names = list(_PLACES.keys())
    coords = [_PLACES[n] for n in names]

    if not coords:
        print("No places to plot.")
        return

    lats = [lat for lat, lon in coords]
    lons = [lon for lat, lon in coords]

    # Local equirectangular projection to meters
    lat0 = sum(lats) / len(lats)
    lon0 = sum(lons) / len(lons)
    lat0_rad = math.radians(lat0)
    R = 6371000.0

    xs = [R * math.cos(lat0_rad) * math.radians(lon - lon0) for lon in lons]
    ys = [R * math.radians(lat - lat0) for lat in lats]

    fig, ax = plt.subplots(figsize=(7, 6))
    ax.scatter(xs, ys, c="purple", s=30, zorder=3)

    for name, x, y in zip(names, xs, ys):
        ax.text(x, y, f"  {name}", fontsize=8, va="center", ha="left")

    ax.set_xlabel("x (m)")
    ax.set_ylabel("y (m)")
    ax.set_title("U-M North Campus predefined places (local meters)")
    ax.set_aspect('equal', adjustable='box')

    if xs and ys:
        pad_x = max(1.0, (max(xs) - min(xs)) * 0.2)
        pad_y = max(1.0, (max(ys) - min(ys)) * 0.2)
        ax.set_xlim(min(xs) - pad_x, max(xs) + pad_x)
        ax.set_ylim(min(ys) - pad_y, max(ys) + pad_y)

    ax.grid(True, ls=":", lw=0.5, alpha=0.5)
    fig.tight_layout()
    fig.savefig(args.out, dpi=160)
    print(f"Saved {args.out}")


if __name__ == "__main__":
    main()
