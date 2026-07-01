"""Routing algorithms for RouteReel.

Uses the haversine formula for real-world distance between lat/lon points,
a nearest-neighbor heuristic to build an initial route, and a 2-opt pass
to iteratively improve it.
"""

import math


def haversine(a, b):
    """Great-circle distance in miles between two (lat, lon) points."""
    R = 3958.8  # Earth radius in miles
    lat1, lon1 = math.radians(a[0]), math.radians(a[1])
    lat2, lon2 = math.radians(b[0]), math.radians(b[1])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    h = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    return 2 * R * math.asin(math.sqrt(h))


def route_distance(route, coords, return_to_start=True):
    """Total distance of a route (list of stop indices) given a coords lookup."""
    if len(route) < 2:
        return 0.0
    total = sum(haversine(coords[route[i]], coords[route[i + 1]]) for i in range(len(route) - 1))
    if return_to_start:
        total += haversine(coords[route[-1]], coords[route[0]])
    return total


def nearest_neighbor(coords, start=0):
    """Build a route by always hopping to the closest unvisited stop."""
    n = len(coords)
    unvisited = set(range(n))
    unvisited.discard(start)
    route = [start]
    current = start
    while unvisited:
        nxt = min(unvisited, key=lambda i: haversine(coords[current], coords[i]))
        route.append(nxt)
        unvisited.discard(nxt)
        current = nxt
    return route


def two_opt(route, coords, return_to_start=True):
    """Improve a route by reversing segments while it shortens the total."""
    best = route[:]
    best_dist = route_distance(best, coords, return_to_start)
    improved = True
    while improved:
        improved = False
        # Keep the depot (index 0 position) fixed as the start.
        for i in range(1, len(best) - 1):
            for j in range(i + 1, len(best)):
                candidate = best[:i] + best[i:j + 1][::-1] + best[j + 1:]
                cand_dist = route_distance(candidate, coords, return_to_start)
                if cand_dist + 1e-9 < best_dist:
                    best, best_dist = candidate, cand_dist
                    improved = True
    return best, best_dist


def optimize(coords, start=0, return_to_start=True):
    """Full pipeline: nearest-neighbor seed, then 2-opt polish."""
    seed = nearest_neighbor(coords, start=start)
    route, dist = two_opt(seed, coords, return_to_start)
    return route, dist
