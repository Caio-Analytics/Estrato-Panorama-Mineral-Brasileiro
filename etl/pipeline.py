"""Orchestrates the full pipeline: Bronze -> Silver -> Gold -> Cross-reference
-> Dashboard, for both datasets (Produção Bruta and Produção Beneficiada).

    python -m etl.pipeline

Each stage is timed and logged independently so the console output doubles
as a lightweight performance report (this is also why Bronze/Silver run on
Polars: ingesting + cleaning ~10k combined rows across two 14-20 column CSVs
is dominated by string parsing, exactly where Polars' Rust-native,
multi-threaded expression engine pulls ahead of row-wise Python).
"""

import logging
import time
from contextlib import contextmanager

from dashboard import build_dashboard
from etl import bronze, cross_reference, gold, silver
from etl.config import BENEFICIADA, BRUTA

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s", datefmt="%H:%M:%S")
logger = logging.getLogger("pipeline")


@contextmanager
def timed(stage: str):
    t0 = time.perf_counter()
    logger.info("=== %s: start ===", stage)
    yield
    logger.info("=== %s: done in %.2fs ===", stage, time.perf_counter() - t0)


def main() -> None:
    specs = [BRUTA, BENEFICIADA]

    with timed("Bronze"):
        for spec in specs:
            bronze.run_bronze(spec)

    with timed("Silver"):
        for spec in specs:
            silver.run_silver(spec)

    with timed("Gold"):
        for spec in specs:
            gold.run_gold(spec)

    with timed("Cruzamento"):
        cross_reference.run_cross_reference()

    with timed("Dashboard"):
        out = build_dashboard.build_dashboard()

    logger.info("Pipeline complete -> %s", out)


if __name__ == "__main__":
    main()
