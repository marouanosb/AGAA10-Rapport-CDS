# AAGA10 - Connected Dominating Sets (Li et al., 2005)

Implementation of the two-phase greedy algorithm for Connected Dominating Sets
in Unit Disk Graphs, based on:

> Li, Thai, Wang, Yi, Wan & Du, "On greedy construction of connected dominating
> sets in wireless networks", *Wireless Communications and Mobile Computing*, 2005.

## Requirements

- Python 3.7+
- matplotlib (for plots and visualization)

Install matplotlib if needed:

```
pip install matplotlib
```

## Project Structure

```
src/
├── udg.py                    # Unit Disk Graph generation and I/O
├── cds_greedy.py             # Phase 1 (greedy DS) + Phase 2 (Steiner connection)
├── run.py                    # Full benchmark suite with plot generation
├── visualization.py          # Draw a UDG with the CDS highlighted
├── test_instances/
│   ├── instance_small.json   # 50 nodes, avg_deg ≈ 10
│   └── instance_medium.json  # 200 nodes, avg_deg ≈ 10
├── figures/                  # Generated plots (after running experiments)
└── results/                  # Generated CSV (after running experiments)
```

## Quick Start

### 1. Visualize a graph with its CDS

```
make visualize
```

This loads the small test instance (50 nodes), computes the CDS, saves a
figure to `src/figures/udg_cds.pdf`, and opens it in an interactive window.

To use a different instance or output path, run directly:

```
cd src
python3 visualization.py test_instances/instance_medium.json figures/my_graph.png
```

### 2. Run full experiments

From the project root folder:

```
make run
```

This runs the algorithm on random UDG instances with varying sizes
(n = 50, 100, 200, 500) and densities (avg_degree = 5, 10, 15, 20),
30 runs each. It produces:

- `src/results/summary.csv` - raw numerical results
- `src/figures/cds_size.pdf` - CDS size vs. number of nodes
- `src/figures/exec_time.pdf` - execution time vs. number of nodes
- `src/figures/approx_ratio.pdf` - Steiner overhead vs. average degree

### Windows alternative (run.bat)

If `make` is not available, use `run.bat` from the project root:

```
run.bat run   # Full benchmarks + plots
run.bat visualize     # Visualize CDS on the small instance
```

## Instance File Format

Test instances are stored as JSON:

```json
{
  "n": 50,
  "points": [[x1, y1], [x2, y2], ...],
  "edges": [[0, 3], [1, 5], ...]
}
```

- `n`: number of nodes
- `points`: 2D coordinates of each node
- `edges`: list of undirected edges (pairs of node indices)
