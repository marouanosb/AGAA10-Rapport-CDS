# ============================================================================
# Makefile — AAGA10 CDS Project
#
#   make run → Run full benchmark suite + generate plots
#   make visualize → Visualize CDS on the small test instance
# ============================================================================

PYTHON  = python3
SRC_DIR = src
FIG_DIR = src/figures
RES_DIR = src/results
TEST_DIR= src/test_instances

.PHONY: run visualize

# ── Run full experiments (generates plots and CSV) ─────────────────────
run:
	cd $(SRC_DIR) && $(PYTHON) run.py

# ── Visualize CDS on the small test instance ─────────────────────────
visualize:
	cd $(SRC_DIR) && $(PYTHON) visualization.py test_instances/instance_small.json

