# Navari Website

Source and documentation repository for the Navari Limited website built with Frappe Builder.

## Project Structure

```text
navari-website/
├── assets/                  # Website assets and supporting files
├── builder/                 # Exported Frappe Builder page configuration
├── docs/                    # Project documentation
├── scripts/                 # Development and export utilities
├── .gitignore
└── README.md
```

## Builder Page

The current website is built using Frappe Builder.

* **Site:** `navari.localhost`
* **Route:** `/navari-kenya`
* **Builder Page:** `page-9a38be2a`

The Builder page export is stored at:

```text
builder/navari-kenya.json
```

## Exporting the Current Builder Page

From this repository:

```bash
~/frappe-bench/env/bin/python scripts/export_builder_page.py
```

The script exports the current Builder Page configuration from the local Frappe site into:

```text
builder/navari-kenya.json
```

## Development Workflow

The website is developed section by section with responsive behaviour considered across:

* Desktop
* Tablet
* Mobile

Frappe Builder's built-in page snapshots provide recovery points for the live Builder page, while this repository provides project-level version control and documentation.

## Design Direction

The redesign aims for a clean, modern and professional visual identity combining:

* Clear editorial layouts
* Generous whitespace
* Strong typography
* Navari brand colours
* Responsive layouts
* Accessible interaction patterns
* Subtle motion
* Clear calls to action

The design is inspired by modern enterprise and product websites while remaining distinct to Navari.

## Version Control

Changes should be committed in meaningful milestones, for example:

```text
chore: establish Navari website baseline
feat: redesign responsive navigation
feat: redesign homepage hero
feat: add solutions section
```

Frappe Builder's source repository is not modified as part of this project. This repository contains the Navari website project files and exported Builder configuration.

## Review the improved website without Frappe

```bash
python scripts/preview_site.py
python -m http.server 4173 --directory dist
```

Open http://localhost:4173. The preview supports all five static page layouts;
dynamic stories and the contact submission endpoint require Frappe.
Generated preview files are ignored by Git.

See [the redesign notes](docs/website-audit/redesign.md) for verified content
sources, changes, and Frappe import requirements. Upload the included logo as a
public File at `/files/navari-logo.png` before publishing imported pages.

Validate the exports with `python scripts/validate_exports.py`.
