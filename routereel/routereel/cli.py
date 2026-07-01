"""RouteReel — a delivery route optimizer for the command line.

Reads a CSV of stops with coordinates, orders them into an efficient route
from a chosen depot, and prints the stop sequence and total distance.
"""

import argparse
import csv
import sys

from routereel.routing import optimize, nearest_neighbor, route_distance, haversine


def load_stops(path):
    """Load stops from CSV. Returns (names, coords) as parallel lists."""
    names, coords = [], []
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        required = {"stop", "lat", "lon"}
        missing = required - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"CSV is missing columns: {', '.join(sorted(missing))}")
        for i, row in enumerate(reader, start=2):
            try:
                lat = float(row["lat"])
                lon = float(row["lon"])
            except ValueError as e:
                raise ValueError(f"Bad coordinate on line {i}: {e}") from e
            names.append(row["stop"].strip())
            coords.append((lat, lon))
    return names, coords


def find_depot(names, depot_name):
    """Return the index of the depot by name, or 0 if not specified."""
    if depot_name is None:
        return 0
    for i, name in enumerate(names):
        if name.lower() == depot_name.lower():
            return i
    raise ValueError(f"Depot '{depot_name}' not found among stops.")


def cmd_plan(args):
    names, coords = load_stops(args.stops)
    if len(coords) < 2:
        print("Need at least two stops to plan a route.")
        return

    depot = find_depot(names, args.depot)
    return_to_start = not args.one_way

    baseline = nearest_neighbor(coords, start=depot)
    base_dist = route_distance(baseline, coords, return_to_start)

    route, dist = optimize(coords, start=depot, return_to_start=return_to_start)

    print(f"\nDepot: {names[depot]}")
    print(f"Stops: {len(route)}   Return to depot: {'yes' if return_to_start else 'no'}")
    print("\n=== Optimized Route ===")
    for order, idx in enumerate(route, start=1):
        leg = ""
        if order > 1:
            prev = route[order - 2]
            leg = f"  (+{haversine(coords[prev], coords[idx]):.1f} mi)"
        print(f"  {order:>2}. {names[idx]}{leg}")
    if return_to_start:
        back = haversine(coords[route[-1]], coords[route[0]])
        print(f"      ↩ return to {names[depot]}  (+{back:.1f} mi)")

    saved = base_dist - dist
    pct = (saved / base_dist * 100) if base_dist else 0
    print(f"\n=== Summary ===")
    print(f"  Total distance     {dist:.1f} mi")
    print(f"  Naive nearest-nbr  {base_dist:.1f} mi")
    print(f"  Saved by 2-opt     {saved:.1f} mi ({pct:.1f}%)")
    print()


def build_parser():
    p = argparse.ArgumentParser(
        prog="routereel",
        description="Optimize a delivery route from a CSV of stops.",
    )
    sub = p.add_subparsers(dest="command", required=True)
    plan = sub.add_parser("plan", help="Plan an optimized route")
    plan.add_argument("stops", help="Path to stops CSV (columns: stop,lat,lon)")
    plan.add_argument("-d", "--depot", help="Name of the starting depot (default: first stop)")
    plan.add_argument("--one-way", action="store_true", help="Do not return to the depot at the end")
    plan.set_defaults(func=cmd_plan)
    return p


def main(argv=None):
    args = build_parser().parse_args(argv)
    try:
        args.func(args)
    except (FileNotFoundError, ValueError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
