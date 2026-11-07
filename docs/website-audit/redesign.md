# Website improvements — 7 November 2026

The existing Frappe Builder page structure, IDs, routes, dynamic story bindings and contact Web Form are retained. Canonical migration pages, cloud creation payloads and the two homepage Builder exports now share the updated published blocks. Draft blocks match the updated published version.

## Design and content

The homepage introduces Navari's offering with two clear next steps: contact the team or explore services. Tighter section spacing, responsive typography and a restrained warm background keep the existing identity. The operations illustration is labelled as illustrative. Payment and compliance tags now reflect the local integration story. A new section links to Navari's documentation for M-Pesa, Kenya compliance and biometric attendance.

Verified sources, accessed 7 November 2026:

- https://navari.co.ke/ — enterprise focus, service offering, first Frappe partner in Kenya, 100+ clients, 2026 partner award, business contact details.
- https://navari.co.ke/services/ — ERPNext/Frappe services and covered business functions.
- https://docs.navari.co.ke/ — payments, compliance and biometric integrations.

No customer quotations or project outcomes were invented. Partnership claims should be reviewed when Navari's live site changes.

## Reliability and accessibility

- Relative internal URLs replace development-host links; navigation remains in the same tab.
- Contact email consistently uses the published solutions address.
- Public logo path replaces an inaccessible private attachment.
- Identical client scripts share one canonical definition and references.
- JavaScript initialises after DOM readiness and has isolated scope.
- Content stays readable without JavaScript, with visible focus and skip links.
- Navigation collapses at tablet widths; Escape closes the mobile drawer and returns focus.
- Contact submission validates required fields, maps the name correctly, displays success/error feedback and supports retry after a completed request.

## Preview and deployment

Run `python scripts/preview_site.py`, then `python -m http.server 4173 --directory dist`.
This dependency-free preview renders static blocks, client scripts and breakpoint styles. It does not execute Frappe page-data scripts: dynamic stories and successful contact persistence require a running Frappe site.

For Frappe deployment, upload `migration/assets/navari-logo.png` as a **public** File with URL `/files/navari-logo.png`. Import the client scripts before pages, using `migration/manifest.json` as the reference list. Update existing Builder Page documents using their exported names; use cloud-create payloads only for new documents. Preserve the original site's home-page routing. The exports do not change the production Navari website until imported and published there.
