"""Benchmarks and plots for CDS experiments."""

import time
import csv
import os
import statistics
from typing import List, Dict, Any

from udg import generate_connected_udg
from cds_greedy import greedy_cds, greedy_dominating_set, verify_cds

# Optional
try:
    import matplotlib.pyplot as plt
    HAS_MPL = True
except ImportError:
    HAS_MPL = False
    print("Warning: matplotlib not found — plots will not be generated.")


# ── Experiment parameters ──────────────────────────────────────────────────

NODE_COUNTS = [50, 100, 200, 500]
AVG_DEGREES = [5, 10, 15, 20]
NUM_RUNS = 30
SEED_BASE = 1000


def run_single(n: int, avg_deg: float, seed: int) -> Dict[str, Any]:
    """Run one experiment: generate UDG, compute CDS, measure time."""
    points, adj = generate_connected_udg(n, avg_deg, seed=seed)

    # Phase 1 + Phase 2
    t0 = time.perf_counter()
    cds = greedy_cds(adj)
    elapsed_ms = (time.perf_counter() - t0) * 1000.0

    # Phase 1 alone
    ds = greedy_dominating_set(adj)

    valid = verify_cds(adj, cds)
    return {
        "n": n,
        "avg_deg": avg_deg,
        "seed": seed,
        "ds_size": len(ds),
        "cds_size": len(cds),
        "steiner_nodes": len(cds) - len(ds & cds),
        "time_ms": elapsed_ms,
        "valid": valid,
        "actual_avg_deg": sum(len(adj[v]) for v in adj) / n,
    }


def run_experiments() -> List[Dict[str, Any]]:
    """Run all experiments and return collected results."""
    results = []
    total = len(NODE_COUNTS) * len(AVG_DEGREES) * NUM_RUNS
    done = 0
    for n in NODE_COUNTS:
        for avg_deg in AVG_DEGREES:
            for run_id in range(NUM_RUNS):
                seed = SEED_BASE + n * 100 + avg_deg * 10 + run_id
                res = run_single(n, avg_deg, seed)
                results.append(res)
                done += 1
                if done % 50 == 0:
                    print(f"  Progress: {done}/{total}")
    return results


def save_csv(results: List[Dict[str, Any]], filepath: str):
    """Save results to CSV."""
    if not results:
        return
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    keys = results[0].keys()
    with open(filepath, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(results)
    print(f"Results saved to {filepath}")


def aggregate(results: List[Dict[str, Any]], n: int, avg_deg: float, key: str):
    """Return (mean, stdev) of key for a given (n, avg_deg) pair."""
    vals = [r[key] for r in results if r["n"] == n and r["avg_deg"] == avg_deg]
    if len(vals) < 2:
        return (vals[0] if vals else 0, 0)
    return (statistics.mean(vals), statistics.stdev(vals))


def plot_cds_size(results, outpath="figures/cds_size.pdf"):
    """CDS size vs. n for selected average degrees."""
    if not HAS_MPL:
        return
    os.makedirs(os.path.dirname(outpath), exist_ok=True)

    fig, ax = plt.subplots(figsize=(8, 5))
    for avg_deg in [10, 20]:
        means, stds, ns = [], [], []
        for n in NODE_COUNTS:
            m, s = aggregate(results, n, avg_deg, "cds_size")
            means.append(m)
            stds.append(s)
            ns.append(n)
        ax.errorbar(ns, means, yerr=stds, marker="o", capsize=4,
                     label=f"avg degree = {avg_deg}")
    ax.set_xlabel("Number of nodes (n)")
    ax.set_ylabel("CDS size")
    ax.set_title("CDS Size vs. Number of Nodes")
    ax.legend()
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(outpath)
    print(f"Plot saved to {outpath}")


def plot_exec_time(results, outpath="figures/exec_time.pdf"):
    """Execution time vs. n (log scale)."""
    if not HAS_MPL:
        return
    os.makedirs(os.path.dirname(outpath), exist_ok=True)

    fig, ax = plt.subplots(figsize=(8, 5))
    for avg_deg in [10, 20]:
        means, ns = [], []
        for n in NODE_COUNTS:
            m, _ = aggregate(results, n, avg_deg, "time_ms")
            means.append(m)
            ns.append(n)
        ax.plot(ns, means, marker="s", label=f"avg degree = {avg_deg}")
    ax.set_xlabel("Number of nodes (n)")
    ax.set_ylabel("Execution time (ms)")
    ax.set_yscale("log")
    ax.set_title("Execution Time vs. Number of Nodes")
    ax.legend()
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(outpath)
    print(f"Plot saved to {outpath}")


def plot_approx_ratio(results, outpath="figures/approx_ratio.pdf"):
    """CDS/DS ratio vs. average degree (Phase 2 overhead)."""
    if not HAS_MPL:
        return
    os.makedirs(os.path.dirname(outpath), exist_ok=True)

    fig, ax = plt.subplots(figsize=(8, 5))
    for n in [100, 200, 500]:
        if n not in NODE_COUNTS:
            continue
        ratios_mean, ratios_std, degs = [], [], []
        for avg_deg in AVG_DEGREES:
            cds_vals = [r["cds_size"] for r in results
                        if r["n"] == n and r["avg_deg"] == avg_deg]
            ds_vals = [r["ds_size"] for r in results
                       if r["n"] == n and r["avg_deg"] == avg_deg]
            if not cds_vals or not ds_vals:
                continue
            # ratio = CDS / DS
            rats = [c / d if d > 0 else 0 for c, d in zip(cds_vals, ds_vals)]
            ratios_mean.append(statistics.mean(rats))
            ratios_std.append(statistics.stdev(rats) if len(rats) > 1 else 0)
            degs.append(avg_deg)
        ax.errorbar(degs, ratios_mean, yerr=ratios_std, marker="^", capsize=4,
                     label=f"n = {n}")
    ax.set_xlabel("Average degree")
    ax.set_ylabel("|CDS| / |DS|  (Phase 2 overhead)")
    ax.set_title("Steiner Overhead vs. Average Degree")
    ax.legend()
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(outpath)
    print(f"Plot saved to {outpath}")


# Main

if __name__ == "__main__":
    print("=" * 60)
    print("Running CDS experiments (Li et al. greedy algorithm)")
    print("=" * 60)

    results = run_experiments()
    save_csv(results, "results/summary.csv")

    print("\n{:<6} {:<8} {:<10} {:<10} {:<10}".format(
        "n", "avg_deg", "CDS_mean", "CDS_std", "time_ms"))
    print("-" * 50)
    for n in NODE_COUNTS:
        for avg_deg in AVG_DEGREES:
            m_cds, s_cds = aggregate(results, n, avg_deg, "cds_size")
            m_t, _ = aggregate(results, n, avg_deg, "time_ms")
            print(f"{n:<6} {avg_deg:<8} {m_cds:<10.1f} {s_cds:<10.2f} {m_t:<10.1f}")

    # Plots
    plot_cds_size(results)
    plot_exec_time(results)
    plot_approx_ratio(results)

    # Validation
    invalid = [r for r in results if not r["valid"]]
    if invalid:
        print(f"\nWARNING: {len(invalid)} invalid CDS found!")
    else:
        print(f"\nAll {len(results)} CDS instances verified as valid.")

    print("\nDone.")

    if HAS_MPL:
        plt.show()
