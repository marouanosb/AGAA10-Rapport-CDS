"""Unit Disk Graph generation and I/O."""

import math
import random
import json
from typing import List, Tuple, Dict, Set


def generate_points(n: int, side_length: float, seed: int = None) -> List[Tuple[float, float]]:
    """Generate n random 2D points in [0, side_length]^2."""
    if seed is not None:
        random.seed(seed)
    return [(random.uniform(0, side_length), random.uniform(0, side_length)) for _ in range(n)]


def euclidean_distance(p: Tuple[float, float], q: Tuple[float, float]) -> float:
    """Euclidean distance between two 2D points."""
    return math.sqrt((p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2)


def build_udg(points: List[Tuple[float, float]], radius: float = 1.0) -> Dict[int, Set[int]]:
    """Build adjacency list of a UDG (edge iff distance <= radius)."""
    n = len(points)
    adj: Dict[int, Set[int]] = {i: set() for i in range(n)}
    for i in range(n):
        for j in range(i + 1, n):
            if euclidean_distance(points[i], points[j]) <= radius:
                adj[i].add(j)
                adj[j].add(i)
    return adj


def side_length_for_avg_degree(n: int, avg_degree: float) -> float:
    """Compute side length L so expected avg degree ~ avg_degree (L = sqrt(n*pi/d))."""
    return math.sqrt(n * math.pi / avg_degree)


def is_connected(adj: Dict[int, Set[int]]) -> bool:
    """Check graph connectivity via BFS."""
    if not adj:
        return True
    start = next(iter(adj))
    visited = set()
    queue = [start]
    visited.add(start)
    while queue:
        v = queue.pop(0)
        for u in adj[v]:
            if u not in visited:
                visited.add(u)
                queue.append(u)
    return len(visited) == len(adj)


def largest_connected_component(points: List[Tuple[float, float]],
                                adj: Dict[int, Set[int]]):
    """Extract largest connected component, re-indexed 0..k-1."""
    visited: Set[int] = set()
    best_comp: List[int] = []
    for start in adj:
        if start in visited:
            continue
        comp = []
        queue = [start]
        visited.add(start)
        while queue:
            v = queue.pop(0)
            comp.append(v)
            for u in adj[v]:
                if u not in visited:
                    visited.add(u)
                    queue.append(u)
        if len(comp) > len(best_comp):
            best_comp = comp

    # Re-index
    old_to_new = {old: new for new, old in enumerate(best_comp)}
    new_points = [points[v] for v in best_comp]
    new_adj: Dict[int, Set[int]] = {i: set() for i in range(len(best_comp))}
    for old_v in best_comp:
        nv = old_to_new[old_v]
        for old_u in adj[old_v]:
            if old_u in old_to_new:
                new_adj[nv].add(old_to_new[old_u])
    return new_points, new_adj


def generate_connected_udg(n: int, avg_degree: float, radius: float = 1.0,
                           seed: int = None, max_attempts: int = 100):
    """Generate a connected UDG; falls back to largest component if needed."""
    L = side_length_for_avg_degree(n, avg_degree)
    best_points, best_adj, best_size = None, None, 0

    for attempt in range(max_attempts):
        s = seed + attempt if seed is not None else None
        points = generate_points(n, L, seed=s)
        adj = build_udg(points, radius)
        if is_connected(adj):
            return points, adj
        # Track the attempt with the largest component as fallback
        lcc_pts, lcc_adj = largest_connected_component(points, adj)
        if len(lcc_adj) > best_size:
            best_size = len(lcc_adj)
            best_points, best_adj = lcc_pts, lcc_adj

    # Fallback: return the largest connected component found
    return best_points, best_adj


def save_instance(filepath: str, points: List[Tuple[float, float]],
                  adj: Dict[int, Set[int]]):
    """Save UDG instance to JSON."""
    edges = []
    seen = set()
    for u, neighbors in adj.items():
        for v in neighbors:
            if (v, u) not in seen:
                edges.append([u, v])
                seen.add((u, v))
    data = {
        "n": len(points),
        "points": [list(p) for p in points],
        "edges": edges,
    }
    with open(filepath, "w") as f:
        json.dump(data, f, indent=2)


def load_instance(filepath: str):
    """Load UDG instance from JSON."""
    with open(filepath, "r") as f:
        data = json.load(f)
    points = [tuple(p) for p in data["points"]]
    n = data["n"]
    adj: Dict[int, Set[int]] = {i: set() for i in range(n)}
    for u, v in data["edges"]:
        adj[u].add(v)
        adj[v].add(u)
    return points, adj


if __name__ == "__main__":
    n, avg_deg = 100, 10
    pts, adjacency = generate_connected_udg(n, avg_deg, seed=42)
    total_deg = sum(len(nb) for nb in adjacency.values())
    print(f"Generated connected UDG: n={n}, edges={total_deg // 2}, "
          f"avg_degree={total_deg / n:.1f}")
