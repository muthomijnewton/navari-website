# Navari website

A responsive, product-led Navari Limited website for Frappe Builder. The redesign
uses app discovery patterns, with original Navari content,
colour-coded app icons, an editorial layout and verified business details.

## Preview

Run from this repository:

```bash
python scripts/serve_preview.py
```

Open **http://localhost:4173**. If that port is occupied:

```bash
python scripts/serve_preview.py --port 4174
```

The script builds the preview and serves it on loopback. It also works from any
other directory when invoked with its absolute path. Stop with **Ctrl+C**.
The preview cannot save enquiries: the contact form requires the Frappe backend.

## Edit and build

- `website/apps.json`: product catalogue, categories, feature summaries and links.
- `website/site.css`: shared design system and responsive layouts.
- `website/site.js`: menus, filters, deep links and consultation requests.
- `website/motion.js`: section entrances, staggered cards and the workspace sequence.
- `website/stories.json`: the published story snapshot, source links, dates and images.
- `website/stories.js`: archive search, categories, pagination and shared URL state.
- `website/articles.json`: concise article overviews and original PDF/webinar references.
- `website/article.js`: reading progress, contents tracking, copy link and media loading.
- `website/documentation.json`: app guide catalogue and verified documentation destinations.
- `website/guides.json`: sanitized snapshot of 225 original documentation chapters and guide status.
- `website/guide.js`: chapter search, mobile sidebar and reading utilities.
- `scripts/guide_pages.py`: native application guide reading layouts.
- `scripts/snapshot_guides.py`: explicit documentation refresh (requires beautifulsoup4).
- `website/documentation.js`: guide search, topics, sorting, lighting and Calm mode.
- `scripts/documentation_page.py`: documentation hub composition.
- `scripts/article_pages.py`: native article reading layouts and related stories.
- `scripts/story_archive.py`: featured story and archive/card composition.
- `scripts/build_overhaul.py`: page composition and HTML-to-Builder compiler.
- `website/*.html`: generated, inspectable HTML; edit the composition script.
- `builder/`: synchronized homepage Builder exports.
- `migration/`: 240 canonical pages, cloud creation payloads, scripts and Web Form.

After editing sources:

```bash
python scripts/build_overhaul.py
python scripts/validate_exports.py
python scripts/serve_preview.py
```

The compiler produces individual editable Builder blocks and preserves existing
page names and routes. It synchronizes drafts, published blocks and cloud payloads.
The validator checks script syntax and references, internal routes and fragments,
unique HTML/block IDs, page headings and export consistency.

## Pages

| Route | Content |
| --- | --- |
| `/home` (site homepage) | Hero, eight featured apps, open-source benefits, integrations, delivery process and stories |
| `/services` | Fifteen filterable solutions, product details, implementation services and FAQs |
| `/about` | Company, approach, partnership recognition and careers enquiry |
| `/stories` | Eight published stories with a featured article, images, search, category filters and pagination |
| `/documentation` | Searchable guide hub for 18 applications, topic filters, lighting and motion controls |
| `/documentation/{app}/{chapter}` | 225 full source chapters with app navigation, contents, media, code and tables; first chapters use `/documentation/{app}` |
| `/contacts` | Enquiry form with solution preselection and optional consultation preference |
| `/{original-story-slug}` | Eight native article pages with reading tools, related stories and access to original material |

The offline preview additionally serves the homepage at `/`.

## Publish to Frappe

See [the overhaul and deployment notes](docs/website-audit/overhaul-v2.md).
Upload `migration/assets/navari-logo.png` as a **public** File at
`/files/navari-logo.png`, upload all eight images in `migration/assets/stories/` as public Files using their
existing filenames, then import the Web Form/DocType if missing, the seven client
scripts and the page documents. The archive script is attached only to Stories;
the reading-tools script is attached only to article pages. The documentation
discovery script is attached only to Documentation; the application guide reading
script is attached only to guide pages. Import the `guide-*-cloud-create.json`
payloads to create the 226 guide documents using their supplied routes and names. Create the new hub using
`migration/pages/documentation-cloud-create.json` (page name `navari-documentation`,
route `documentation`). Use the article cloud-create
payloads to create the eight new Builder Pages, preserving their supplied routes. Update existing pages by their exported
names; use cloud-create payloads only to create new documents. Confirm the site
homepage configuration and test a real enquiry on staging before production.

The hub and product links open local application guides. Their technical content
is a snapshot from `docs.navari.co.ke`, with source links retained and media served
from the original host. The unavailable Vuna Transport guide has a status page
offering Navari contact help. The separate live documentation service is unchanged.

To refresh source content explicitly, run `python scripts/snapshot_guides.py` in
a development environment with `beautifulsoup4` installed, then rebuild and validate.
Routine builds use the committed snapshot and make no network requests. Review
content changes and unavailable-page reports before publishing a refreshed snapshot.

Repository updates do not deploy to `navari.co.ke` automatically. Backend
persistence and email delivery must be verified on the target Frappe site.

## Exporting changes made in the live Builder editor

The legacy `scripts/export_builder_page.py` and
`scripts/export_navari_migration.py` read `navari.localhost` from the local
`~/frappe-bench`. They export the live database state, not these source files.
Do not run them as build checks: doing so before importing this redesign would
replace the new exports with older live Builder content.
