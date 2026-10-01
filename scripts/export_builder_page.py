import json
import os
from pathlib import Path
import sys

BENCH_PATH = Path.home() / "frappe-bench"
SITE = "navari.localhost"
PAGE_NAME = "page-9a38be2a"

os.chdir(BENCH_PATH / "sites")

sys.path.insert(0, str(BENCH_PATH / "apps" / "frappe"))

import frappe


OUTPUT_FILE = (
    Path(__file__).resolve().parents[1]
    / "builder"
    / "navari-kenya.json"
)


def main():
    frappe.init(site=SITE, sites_path=str(BENCH_PATH / "sites"),)
    frappe.connect()

    try:
        page = frappe.get_doc("Builder Page", PAGE_NAME)

        export = {
            "doctype": "Builder Page",
            "name": page.name,
            "route": page.route,
            "page_title": page.page_title,
            "meta_description": page.meta_description,
            "published": page.published,
            "head_html": page.head_html,
            "body_html": page.body_html,
            "page_data_script": page.page_data_script,
            "draft_blocks": page.draft_blocks,
            "blocks": page.blocks,
            "client_scripts": [
                {
                    "name": script.name,
                    "builder_script": script.builder_script,
                }
                for script in page.client_scripts
            ],
        }

        OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

        OUTPUT_FILE.write_text(
            json.dumps(
                export,
                indent=2,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

        print(f"Exported: {OUTPUT_FILE}")
        print(f"Page: {page.name}")
        print(f"Route: {page.route}")

    finally:
        frappe.destroy()


if __name__ == "__main__":
    main()
