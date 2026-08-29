"""Orchestrates the full pipeline: Bronze (Python/Polars) -> dbt build
(staging + marts + tests, DuckDB) -> Dashboard.

    python -m etl.pipeline

Bronze is Python because dbt isn't an extraction tool — it assumes data is
already queryable, and these are cp1252-encoded CSVs DuckDB can't decode
natively. Everything past "typed, UTF-8, columnar" is dbt: cleaning,
region lookups, aggregation, and the cross-dataset join are all SQL models
under transform/, tested and documented via `dbt build`.
"""

import logging
import os
import subprocess
import time
from contextlib import contextmanager

from dashboard import build_dashboard
from etl import bronze
from etl.config import BENEFICIADA, BRUTA, DATA_DIR, DUCKDB_PATH, PROJECT_ROOT, TRANSFORM_DIR

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s", datefmt="%H:%M:%S")
logger = logging.getLogger("pipeline")


@contextmanager
def timed(stage: str):
    t0 = time.perf_counter()
    logger.info("=== %s: start ===", stage)
    yield
    logger.info("=== %s: done in %.2fs ===", stage, time.perf_counter() - t0)


def run_dbt_build() -> None:
    cmd = ["dbt", "build", "--project-dir", str(TRANSFORM_DIR), "--profiles-dir", str(TRANSFORM_DIR)]
    logger.info("Running: %s", " ".join(cmd))
    # profiles.yml / sources.yml default to paths relative to transform/ (so
    # `dbt build` run by hand from that directory just works) — override
    # with absolute paths here since this subprocess's cwd is the repo root.
    DUCKDB_PATH.parent.mkdir(parents=True, exist_ok=True)  # DuckDB won't create it itself
    env = {**os.environ, "BATEIA_DUCKDB_PATH": str(DUCKDB_PATH), "BATEIA_DATA_DIR": str(DATA_DIR)}
    subprocess.run(cmd, cwd=PROJECT_ROOT, check=True, env=env)


def main() -> None:
    with timed("Bronze"):
        bronze.run_bronze(BRUTA)
        bronze.run_bronze(BENEFICIADA)

    with timed("dbt build"):
        run_dbt_build()

    with timed("Dashboard"):
        out = build_dashboard.build_dashboard()

    logger.info("Pipeline complete -> %s", out)


if __name__ == "__main__":
    main()
