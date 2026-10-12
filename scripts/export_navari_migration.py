
import json
import os
import sys
from pathlib import Path

BENCH = Path.home() / "frappe-bench"
SITE = "navari.localhost"
ROOT = Path(__file__).resolve().parents[1] / "migration"

PAGES = {
    "home": "page-9a38be2a",
    "about": "page-28ffc8fc",
    "services": "page-bd2c9253",
    "stories": "page-aadf94d4",
    "contacts": "page-e219bcee",
}

os.chdir(BENCH / "sites")
sys.path.insert(0, str(BENCH / "apps" / "frappe"))

import frappe


def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(data, indent=2, ensure_ascii=False, default=str),
        encoding="utf-8",
    )


def export_document(doc):
    excluded = {
        "owner", "creation", "modified", "modified_by",
        "docstatus", "_user_tags", "_comments", "_assign",
        "_liked_by",
    }

    result = {}

    for field in doc.meta.fields:
        name = field.fieldname

        if not name or field.fieldtype in {
            "Section Break", "Column Break", "Tab Break",
            "Button", "HTML",
        }:
            continue

        if name in excluded:
            continue

        if field.fieldtype in {"Table", "Table MultiSelect"}:
            result[name] = [
                {
                    key: value
                    for key, value in row.as_dict().items()
                    if key not in excluded
                    and key not in {
                        "name", "parent", "parentfield",
                        "parenttype", "doctype", "idx",
                    }
                }
                for row in (doc.get(name) or [])
            ]
        else:
            result[name] = doc.get(name)

    return result


def main():
    frappe.init(site=SITE, sites_path=str(BENCH / "sites"))
    frappe.connect()

    try:
        script_names = set()
        manifest = {"pages": {}, "scripts": []}

        for label, page_name in PAGES.items():
            page = frappe.get_doc("Builder Page", page_name)

            data = export_document(page)
            data["doctype"] = "Builder Page"
            data["name"] = page.name

            write_json(ROOT / "pages" / f"{label}.json", data)

            references = [
                row.builder_script
                for row in page.client_scripts
            ]

            script_names.update(references)

            manifest["pages"][label] = {
                "name": page.name,
                "route": page.route,
                "scripts": references,
            }

            print(f"Exported page: {label} ({len(references)} scripts)")

        scripts = []

        for name in sorted(script_names):
            doc = frappe.get_doc("Builder Client Script", name)

            scripts.append({
                "name": doc.name,
                "script_type": doc.script_type,
                "script": doc.script,
            })

        write_json(ROOT / "scripts" / "client_scripts.json", scripts)

        manifest["scripts"] = sorted(script_names)

        wf = frappe.get_doc(
            "Web Form", "navari-contact-submission"
        )
        dt = frappe.get_doc(
            "DocType", "Navari Contact Submission"
        )

        write_json(
            ROOT / "web-form" / "web_form.json",
            export_document(wf),
        )
        write_json(
            ROOT / "web-form" / "contact_doctype.json",
            export_document(dt),
        )

        write_json(ROOT / "manifest.json", manifest)

        print(f"\nExported {len(PAGES)} pages")
        print(f"Exported {len(scripts)} client scripts")
        print("Exported contact Web Form and DocType")
        print(f"Migration directory: {ROOT}")

    finally:
        frappe.destroy()


if __name__ == "__main__":
    main()
