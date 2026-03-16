"""Two-phase greedy CDS algorithm (Li et al., WCMC 2005)."""

import heapq
from collections import deque
from typing import Dict, Set, List, Tuple


def greedy_dominating_set(adj: Dict[int, Set[int]]) -> Set[int]:
    """Phase 1: greedy dominating set using max-heap with lazy deletion."""
    WHITE, BLACK, GRAY = 0, 1, 2
    color = {v: WHITE for v in adj}
    white_count = {v: len(adj[v]) for v in adj}

    # Max-heap with lazy deletion
    heap = [(-white_count[v], v) for v in adj]
    heapq.heapify(heap)

    dominating_set: Set[int] = set()

    while heap:
        neg_count, v = heapq.heappop(heap)

        # Skip stale entries
        if -neg_count != white_count[v] or color[v] == GRAY:
            continue
        if -neg_count == 0 and color[v] != WHITE:
            continue

        # Select v as dominator
        dominating_set.add(v)
        color[v] = GRAY

        # Mark WHITE neighbors as BLACK
        for u in adj[v]:
            if color[u] == WHITE:
                color[u] = BLACK
                # Update white_count for neighbors of u
                for w in adj[u]:
                    if white_count[w] > 0:
                        white_count[w] -= 1
                        # Push updated entry
                        heapq.heappush(heap, (-white_count[w], w))

        for u in adj[v]:
            if white_count[u] > 0:
                pass

    # Ensure every vertex is dominated
    for v in adj:
        if color[v] == WHITE:
            dominating_set.add(v)

    return dominating_set


def bfs_shortest_path(adj: Dict[int, Set[int]], sources: Set[int],
                      targets: Set[int]) -> List[int]:
    """Multi-source BFS; return shortest path from sources to any target."""
    if not targets:
        return []
    parent = {s: None for s in sources}
    queue = deque(sources)
    while queue:
        v = queue.popleft()
        if v in targets:
            # Reconstruct path
            path = []
            cur = v
            while cur is not None:
                path.append(cur)
                cur = parent[cur]
            path.reverse()
            return path
        for u in adj[v]:
            if u not in parent:
                parent[u] = v
                queue.append(u)
    return []


def connected_components(adj: Dict[int, Set[int]], subset: Set[int]) -> List[Set[int]]:
    """Connected components of the subgraph induced by subset."""
    visited: Set[int] = set()
    components: List[Set[int]] = []
    for v in subset:
        if v in visited:
            continue
        # BFS restricted to subset
        comp: Set[int] = set()
        queue = deque([v])
        visited.add(v)
        while queue:
            cur = queue.popleft()
            comp.add(cur)
            for u in adj[cur]:
                if u in subset and u not in visited:
                    visited.add(u)
                    queue.append(u)
        components.append(comp)
    return components


def connect_dominating_set(adj: Dict[int, Set[int]], dom_set: Set[int]) -> Set[int]:
    """Phase 2: connect dominating set components via Steiner nodes."""
    cds = set(dom_set)  # copy
    comps = connected_components(adj, cds)

    while len(comps) > 1:
        best_path: List[int] = []
        best_len = float("inf")

        # Find shortest bridge between any two components
        for i, comp_i in enumerate(comps):
            other_vertices = set()
            for j, comp_j in enumerate(comps):
                if j != i:
                    other_vertices |= comp_j
            path = bfs_shortest_path(adj, comp_i, other_vertices)
            if path and len(path) < best_len:
                best_len = len(path)
                best_path = path

        if not best_path:
            break

        # Add intermediate nodes to CDS
        for node in best_path:
            cds.add(node)

        comps = connected_components(adj, cds)

    return cds


def greedy_cds(adj: Dict[int, Set[int]]) -> Set[int]:
    """Full two-phase greedy CDS (Phase 1 + Phase 2)."""
    ds = greedy_dominating_set(adj)
    cds = connect_dominating_set(adj, ds)
    return cds


def is_dominating(adj: Dict[int, Set[int]], dom: Set[int]) -> bool:
    """Check that every vertex is in dom or adjacent to dom."""
    for v in adj:
        if v not in dom and not (adj[v] & dom):
            return False
    return True


def is_connected_set(adj: Dict[int, Set[int]], subset: Set[int]) -> bool:
    """Check that the subgraph induced by subset is connected."""
    comps = connected_components(adj, subset)
    return len(comps) <= 1


def verify_cds(adj: Dict[int, Set[int]], cds: Set[int]) -> bool:
    """Verify that *cds* is indeed a Connected Dominating Set."""
    return is_dominating(adj, cds) and is_connected_set(adj, cds)


# ─── Quick self-test ───────────────────────────────────────────────────────

if __name__ == "__main__":
    from udg import generate_connected_udg

    n, avg_deg = 100, 10
    points, adj = generate_connected_udg(n, avg_deg, seed=42)
    cds = greedy_cds(adj)
    ok = verify_cds(adj, cds)
    print(f"n={n}, |CDS|={len(cds)}, valid={ok}")
