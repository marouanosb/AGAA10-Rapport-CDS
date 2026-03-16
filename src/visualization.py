"""Draw a UDG and highlight the CDS."""

import sys
import os
from udg import load_instance
from cds_greedy import greedy_cds, verify_cds

try:
    import matplotlib.pyplot as plt
    HAS_MPL = True
except ImportError:
    HAS_MPL = False


def draw_udg_cds(points, adj, cds, outpath="figures/udg_cds.pdf"):
    """Draw UDG with CDS nodes highlighted in red."""
    if not HAS_MPL:
        print("matplotlib not available — cannot draw.")
        return

    os.makedirs(os.path.dirname(outpath), exist_ok=True)
    fig, ax = plt.subplots(figsize=(8, 8))

    # Edges
    for u in adj:
        for v in adj[u]:
            if u < v:
                ax.plot([points[u][0], points[v][0]],
                        [points[u][1], points[v][1]],
                        color="lightgray", linewidth=0.3, zorder=1)

    # Non-CDS nodes
    non_cds = [v for v in adj if v not in cds]
    ax.scatter([points[v][0] for v in non_cds],
               [points[v][1] for v in non_cds],
               s=15, c="gray", alpha=0.6, zorder=2, label="Regular nodes")

    # CDS nodes
    cds_list = list(cds)
    ax.scatter([points[v][0] for v in cds_list],
               [points[v][1] for v in cds_list],
               s=60, c="red", edgecolors="darkred", linewidths=0.5,
               zorder=3, label=f"CDS nodes ({len(cds)})")

    # CDS-induced edges
    for u in cds:
        for v in adj[u]:
            if v in cds and u < v:
                ax.plot([points[u][0], points[v][0]],
                        [points[u][1], points[v][1]],
                        color="red", linewidth=0.8, alpha=0.5, zorder=2)

    ax.legend(fontsize=10)
    ax.set_title(f"UDG with CDS  (n={len(adj)}, |CDS|={len(cds)})")
    ax.set_aspect("equal")
    ax.grid(True, alpha=0.2)
    fig.tight_layout()
    fig.savefig(outpath, dpi=150)
    print(f"Figure saved to {outpath}")
    plt.show()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python visualization.py <instance.json> [output.pdf]")
        sys.exit(1)

    instance_path = sys.argv[1]
    out = sys.argv[2] if len(sys.argv) > 2 else "figures/udg_cds.pdf"

    points, adj = load_instance(instance_path)
    cds = greedy_cds(adj)
    valid = verify_cds(adj, cds)
    print(f"Loaded {instance_path}: n={len(adj)}, |CDS|={len(cds)}, valid={valid}")
    draw_udg_cds(points, adj, cds, outpath=out)
