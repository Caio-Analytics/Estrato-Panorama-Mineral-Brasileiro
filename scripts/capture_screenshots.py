"""Captures portfolio screenshots of the built dashboard via Playwright.

Not part of the data pipeline — a dev utility to regenerate docs/screenshots/
after a dashboard redesign. Requires the dashboard to already be built
(`python -m etl.pipeline`) and served over HTTP (opening it as a raw
`file://` URL renders fine in a real browser, but headless Chromium's own
page-load handling is more predictable over HTTP, so this script starts a
throwaway server rather than pointing at the file directly).

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

from etl.config import OUTPUT_DIR, PROJECT_ROOT

logger = logging.getLogger(__name__)

PORT = 8743
OUT_DIR = PROJECT_ROOT / "docs" / "screenshots"
VIEWPORT = {"width": 1440, "height": 900}


def _serve(directory: Path):
    handler = lambda *args, **kwargs: http.server.SimpleHTTPRequestHandler(*args, directory=str(directory), **kwargs)
    server = http.server.ThreadingHTTPServer(("localhost", PORT), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    server = _serve(OUTPUT_DIR)
    url = f"http://localhost:{PORT}/dashboard.html"

    with sync_playwright() as p:
        browser = p.chromium.launch()

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

        browser.close()

    server.shutdown()
    logger.info("Screenshots written to %s", OUT_DIR)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    main()
