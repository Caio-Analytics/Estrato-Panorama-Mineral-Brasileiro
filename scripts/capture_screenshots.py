"""Captures portfolio screenshots of the dashboard and the dbt docs site
via Playwright.

Not part of the data pipeline — a dev utility to regenerate
docs/screenshots/ after a redesign. Requires the dashboard to already be
built (`python -m etl.pipeline`) and the dbt docs already generated
(`dbt docs generate --static --project-dir transform --profiles-dir
transform`, then copy transform/target/static_index.html to
docs/dbt/index.html). Both are served over HTTP rather than opened as raw
`file://` URLs — headless Chromium's page-load handling is more predictable
that way, and the dbt docs app's own routing expects it.

    pip install playwright && python -m playwright install chromium
    python scripts/capture_screenshots.py
"""

import http.server
import logging
import sys
import threading
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from playwright.sync_api import sync_playwright

from etl.config import DOCS_DIR, OUTPUT_DIR, PROJECT_ROOT

logger = logging.getLogger(__name__)

DASHBOARD_PORT = 8743
DBT_DOCS_PORT = 8744
OUT_DIR = PROJECT_ROOT / "docs" / "screenshots"
VIEWPORT = {"width": 1440, "height": 900}
DBT_DOCS_VIEWPORT = {"width": 1600, "height": 1000}


def _serve(directory: Path, port: int):
    handler = lambda *args, **kwargs: http.server.SimpleHTTPRequestHandler(*args, directory=str(directory), **kwargs)
    server = http.server.ThreadingHTTPServer(("localhost", port), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server


def capture_dashboard(browser) -> None:
    url = f"http://localhost:{DASHBOARD_PORT}/dashboard.html"

    page = browser.new_page(viewport=VIEWPORT, color_scheme="dark")
    page.goto(url, wait_until="networkidle")
    page.evaluate("document.documentElement.setAttribute('data-theme','dark')")
    page.wait_for_timeout(300)
    page.screenshot(path=str(OUT_DIR / "overview_full.png"), full_page=True)
    page.close()

    for anchor in ["bruta", "beneficiada", "beneficiamento"]:
        page = browser.new_page(viewport=VIEWPORT, color_scheme="dark")
        page.goto(url, wait_until="networkidle")
        page.evaluate("document.documentElement.setAttribute('data-theme','dark')")
        page.evaluate(f"document.getElementById('{anchor}').scrollIntoView()")
        page.wait_for_timeout(300)
        page.screenshot(path=str(OUT_DIR / f"{anchor}_dark.png"))
        page.close()

    page = browser.new_page(viewport=VIEWPORT, color_scheme="light")
    page.goto(url, wait_until="networkidle")
    page.evaluate("document.documentElement.setAttribute('data-theme','light')")
    page.wait_for_timeout(300)
    page.screenshot(path=str(OUT_DIR / "bruta_light.png"))
    page.close()


def capture_dbt_lineage(browser) -> None:
    docs_index = DOCS_DIR / "dbt" / "index.html"
    if not docs_index.exists():
        logger.warning("Skipping dbt lineage screenshot — %s not found (run `dbt docs generate --static` first)", docs_index)
        return

    url = f"http://localhost:{DBT_DOCS_PORT}/index.html"
    page = browser.new_page(viewport=DBT_DOCS_VIEWPORT, color_scheme="light")
    page.goto(url, wait_until="networkidle")
    page.wait_for_timeout(500)
    # The graph-explore FAB is a fixed circular button, bottom-right of the viewport.
    page.mouse.click(DBT_DOCS_VIEWPORT["width"] - 40, DBT_DOCS_VIEWPORT["height"] - 40)
    page.wait_for_timeout(1000)
    page.screenshot(path=str(OUT_DIR / "dbt_lineage.png"))
    page.close()


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    dashboard_server = _serve(OUTPUT_DIR, DASHBOARD_PORT)
    dbt_docs_server = _serve(DOCS_DIR / "dbt", DBT_DOCS_PORT)

    with sync_playwright() as p:
        browser = p.chromium.launch()
        capture_dashboard(browser)
        capture_dbt_lineage(browser)
        browser.close()

    dashboard_server.shutdown()
    dbt_docs_server.shutdown()
    logger.info("Screenshots written to %s", OUT_DIR)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    main()
