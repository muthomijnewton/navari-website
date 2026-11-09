# Navari website overhaul v2

Implemented 7 November 2026. This supersedes the first-pass redesign notes.

## Design and architecture

Five pages share a warm off-white, deep green and terracotta design, serif
accents, native SVG app icons and consistent conversion paths. A sample
workspace diagram is explicitly illustrative. Odoo informed app discovery and
navigation patterns; its visual assets, pricing and platform claims are not copied.

The supplied blueprint is reference material. These implementation choices
resolve its unverified or underspecified items:

- Use the official “100+ clients running on ERPNext” wording. Do not claim that
  all are active enterprise clients or localized deployments.
- Do not promise PostgreSQL ownership, universal integration or zero cost for
  implementation. Hosting, integrations and service scope require assessment.
- Request a preferred consultation date/time in EAT; do not claim calendar
  availability or confirmed appointments without a scheduling service.
- Preserve existing routes and page IDs. Solutions live at `/services`, company
  at `/about`, and resources at `/stories` rather than introducing parallel URLs.
- Curate verified customer stories linking to their original publications.
  The prior dynamic page-data script and pagination are intentionally replaced;
  no new live `/blog` backend or invented articles are included.
- Careers opens an enquiry path; no vacancies, team biographies or quotes are fabricated.

## Interactions

- Solutions, Company and Resources navigation panels; touch drawer at 900px and
  below, Escape handling, keyboard focus containment and focus restoration.
- Fifteen categorized solutions with native expandable details and official
  product links. Eight are featured on the homepage.
- Accessible category buttons with pressed state and live result counts.
- App deep links open their details and reset filters to make the target visible.
- Solution-specific contact links preselect the app on the enquiry form.
- Story filters distinguish customer experiences from news.
- Native form validation, pending state, request timeout, retry and live feedback.
- Preferred solution/date/time are appended to the existing Web Form message,
  avoiding a schema change. A preferred date cannot precede the current Nairobi day.
- App details and core content remain available without JavaScript; a fallback
  navigation and direct email/phone paths remain available.

## Sources reviewed

- https://navari.co.ke/ — current services, positioning, partner status, client count and business contacts.
- https://navari.co.ke/frappe-partner-awards-2026/ — Africa partnership award.
- https://navari.co.ke/stories/ — story titles and original publication links.
- https://navari.co.ke/transforming-distribution-with-frappes-erpnext-from-chaos-to-clarity/ — Ciira Agrovet story.
- https://navari.co.ke/choosing-erpnext-over-sap-and-others-and-our-experience-thus-far/ — Amotech Africa story.
- https://docs.navari.co.ke/ — Navari apps and integrations.
- https://frappe.io/products — product families and official links.
- https://frappe.io/education and https://frappe.io/learning — app positioning.
- https://www.odoo.com/ and https://www.odoo.com/page/all-apps — discovery inspiration.

## Source and deployment workflow

`website/apps.json`, `website/site.css`, `website/site.js` and
`scripts/build_overhaul.py` are the maintained sources. Compile with
`python scripts/build_overhaul.py` and validate with
`python scripts/validate_exports.py`. The generated HTML is for inspection;
Frappe Builder JSON is the deployment format.

1. Back up existing Builder Page and Builder Client Script documents on the target site.
2. Upload the included logo as a public File at `/files/navari-logo.png`.
3. Confirm the `Navari Contact Submission` DocType and `navari-contact-submission`
   Web Form exist, are published, and permit the intended guest submission flow.
4. Import the three shared client scripts from `migration/scripts/client_scripts.json`.
5. Update the five existing Builder Page documents from the canonical exports.
   Use cloud-create payloads only when creating new documents; preserve route/homepage settings.
6. Verify successful persistence, CSRF/request-key requirements of the installed
   Frappe version, anti-spam controls, email notifications and error handling on staging.
7. Publish the pages and verify anonymous access, navigation, logo and contact flow.

No production website or local Frappe database was changed by this overhaul.
The public GitHub repository is the delivery destination. The Cloud Environment
plugin offered no attached-environment status/runtime tool, so development and
browser checks used the user's local environment.

## Verification

- All 13 exported page files validated; all shared JavaScript/CSS references resolved.
- JavaScript syntax, internal routes/fragments, unique block/HTML IDs and one H1 per page checked.
- Five pages checked in the browser at 320, 768 and 1440px: no horizontal overflow.
- App filtering, native details, contact preselection, desktop/mobile menus,
  Escape handling, required fields, local submission failure and retry state checked.
- Native installed Frappe Builder block rendering succeeded for all five pages;
  its generated Jinja was rendered using the registered Builder filters without
  connecting to or modifying a Frappe database.
- A successful real backend submission and email delivery remain staging checks.

## App links — 9 November 2026

App icons, headings, navigation entries and Explore links now open the matching
product/module URL in a new tab, with `noopener noreferrer`. Sales and Procurement
are separate catalogue entries. The M-Pesa and Kenya compliance integration rows
use their specific documentation pages. Internal contact and page navigation links
continue within the website.

## Visual motion — 9 November 2026

A shared native Web Animations layer now adds once-per-view entrances for hero
content, section introductions, app cards, trust points, steps, stories and forms.
Sibling entrances stagger by at most 210ms. The workspace plays a short sequence
through its sample workflow and then settles. Filter changes animate the visible
results. There are no endless animations, animation libraries or new dependencies.

CSS adds a drawn headline highlight, icon and button interactions, card lift,
menu/drawer entrances, expanded-detail entrances and a subtle sticky-header shadow.
Hover transforms apply only to fine pointers that support hover.

Reduced-motion preferences disable scripted motion and CSS transitions, including
when the preference changes during the session. Keyboard focus cancels an entrance
on the focused element's container; hidden tabs settle active scripted animation.
No preload/opacity-zero class is used, so unsupported animation APIs or missing
JavaScript cannot strand invisible content.

Validation: all 13 exports and three shared scripts passed; all five pages were
checked at 320, 768 and 1440px without horizontal overflow. Product filtering,
details, desktop and mobile menu/Escape behavior passed. Local QA fixtures emulated
the reduced-motion branch/CSS and script-free fallback: content stayed visible,
reduced mode did not enable the motion class, and the headline had no animation.
The GIF preview records actual browser screenshots of the homepage entrance.

## Full Stories archive — 9 November 2026

The Stories page is now the full archive in the existing Navari theme, replacing
the three-card resource listing and its external archive exit. The screenshot's
“Browse the full Navari archive” action now targets `#archive` on the redesigned
page. Individual articles still open their original published URLs in new tabs.

The source snapshot comes from the public WordPress posts API:
`https://navari.co.ke/wp-json/wp/v2/posts?per_page=100&_embed=1`. It returned eight
published posts (2020–2026), including the older Frappe partnership post that was
not visible in the current two-page archive listing. Titles, publication dates,
original URLs and original featured images were retained. Short summaries and the
three browsing categories are editorial descriptions, not WordPress taxonomies.

`website/stories.json` is the maintained content snapshot; it does not poll the
live site at runtime. Add new records there and rebuild to extend the archive.
Original image URLs are recorded for traceability. Eight optimized WebP assets
(total about 290 KB) live in `migration/assets/stories/`; upload each as a public
Frappe File with its existing filename, giving `/files/navari-story-<id>.webp`.
The preview launcher copies them automatically.

The archive has a featured story, six cards per page, category filters, search,
empty-state recovery and URL state (`category`, `q`, `page`). Browser Back/Forward
restores the collection state; category anchors from navigation remain supported.
Without scripts all eight articles remain readable. Four client scripts are now
exported; the new archive script is attached only to the Stories page.

Verified: both pagination pages, Back navigation, category selection, search,
no-result recovery, direct page/category URLs, internal archive action and the
script-free fallback. The Stories layout passed 320, 768 and 1440px overflow checks.
The installed native Builder renderer and registered Jinja filters also rendered
the new archive successfully, with working filtering in its generated HTML.

## Native article pages — 9 November 2026

Eight article pages now use the shared editorial theme at the original root-level
slugs. Homepage cards, archive cards, featured articles and the award call to action
open these native pages. External links explicitly marked as original publications
retain their source destinations.

The new pages include breadcrumbs, publication metadata, original artwork,
concise editorial overviews, a contents index, section tracking, reading progress,
copy-link feedback, neighbouring articles and related stories. The overviews are
labelled as such; they are not presented as the full original articles or direct
quotations. Source publications remain linked for complete context. Historic
statistics were not republished as current company claims.

The Ciira Agrovet and Amotech pages retain access to their full original PDF
presentations (12 and 10 pages respectively). Both were checked against their
source documents. The partnership webinar retains its original YouTube video
(`Os3bC13DiWA`) through a click-to-load privacy-enhanced player. PDFs and video
players are not loaded until requested; direct source links remain available
without scripts. No documents or external media were altered.

Sources are `website/articles.json`, `scripts/article_pages.py` and
`website/article.js`. Article cloud-create payloads include deterministic
`page_name` values (`navari-story-<id>`) and the original slugs. Import the new
reading-tools client script before creating article documents. There are now
13 native pages, 29 total export files and five client scripts; only the article
pages attach the reading-tools script. Preview generation now follows the
manifest rather than a fixed list of five routes.

Verified: all eight articles at 320, 768 and 1440px without horizontal overflow;
archive-to-article navigation; contents anchors and progress tracking; direct
PDF links and the inline reader; webinar iframe creation; script-free content;
and native Builder/Jinja rendering for all eight article exports. Full external
media availability continues to depend on the original hosting services.

A motion interaction found during QA was fixed: pointer focus no longer cancels
an entrance transform between mouse-down and mouse-up, preventing interrupted
link clicks. Keyboard focus still settles an active entrance.


## Documentation hub redesign

Added `/documentation`, matching the existing cream, ink, coral and lime theme.
The hero uses soft light washes, pointer-follow illumination, a tilted guide panel
and brief decorative star/orbit motion. Cards stagger into view and respond to
hover. Decorative sequences finish within four seconds. Calm mode stops page
motion; reduced-motion preferences are respected. All guide cards remain readable
without JavaScript.

The catalogue snapshots 18 applications across seven topics from
https://docs.navari.co.ke/. Search, category filters, sorting, shareable URL state,
reset and a slash-key search shortcut help visitors find a guide. Generic website
documentation links now open this internal hub; individual guide links continue
to open the original documentation service in new tabs. Seventeen guide
destinations were verified. Vuna Transport's published `/vuna_transport` route
returns HTTP 404, so its card is labelled unavailable and offers contact help.

Sources: `website/documentation.json`, `website/documentation.js` and
`scripts/documentation_page.py`. The manifest now contains 14 native pages,
31 exports and six client scripts. Import the discovery script before creating
`navari-documentation` from `documentation-cloud-create.json`. This change does
not deploy or restyle the separate live documentation service. No dependencies
or image downloads were added.

Verified search, topics, sort, empty/reset states, keyboard search, Calm mode,
and direct topic URLs; no horizontal overflow at 320, 768 and 1440px. Native
Builder/Jinja rendering was checked, plus script-free and simulated reduced-motion
fixtures. Export validation checks syntax, script references, routes, fragments
and synchronized draft/published blocks.
