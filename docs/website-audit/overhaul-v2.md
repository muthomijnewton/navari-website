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
4. Import the two shared client scripts from `migration/scripts/client_scripts.json`.
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

- All 13 exported page files validated; both shared JavaScript/CSS references resolved.
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
