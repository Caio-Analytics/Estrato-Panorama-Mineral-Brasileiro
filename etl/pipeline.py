"""Orchestrates the full pipeline: Bronze -> dbt build -> Dashboard.

    python -m etl.pipeline
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
    # profiles.yml paths are relative to transform/; override with absolute
    # paths since this subprocess's cwd is the repo root.
    DUCKDB_PATH.parent.mkdir(parents=True, exist_ok=True)
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
