# SEO essentials

- **Structured data:** key pages carry JSON-LD schema — Organization/LocalBusiness site-wide, plus per-type where relevant: Article/BlogPosting on blog posts, FAQPage where FAQs exist, BreadcrumbList on deep pages, Service/Product where applicable. Validate with Google's Rich Results Test before handoff.
- Schema lives in page-level head custom code or a reusable embed — one source per schema type, never inconsistent duplicates across pages.
- **Favicons:** the favicon (32×32) and webclip (256×256+) are set in Site Settings before any launch or handoff. Never ship the default Webflow favicon.
- **Language:** the site's primary locale is {{SITE_LOCALE}}, so the `html` element renders `lang="{{LANG_CODE}}"`. Do not change locale settings; flag it if the lang attribute is missing. All copy uses {{SPELLING_VARIANT}} spelling.
- Every page has a unique meta title and meta description, and Open Graph fields set.
