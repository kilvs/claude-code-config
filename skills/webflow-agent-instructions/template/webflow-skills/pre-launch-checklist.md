---
name: pre-launch-checklist
description: The final quality sweep before any publish, launch, or client handoff of this site. Reference this skill whenever a launch, go-live, handoff, or "is this ready" check is requested. It verifies the work of all site Rules end-to-end and covers the settings, SEO, schema, accessibility, performance, and post-launch steps that don't live on the canvas.
---

# Pre-Launch Checklist

Division of labour: the site Rules govern build-time; this skill is the end-to-end sweep before (and just after) going live. Run it as an audit and deliver a report. Never publish — stage everything and hand the publish decision to the site owner (edit-safety rule).

## 1. Content & pages

- No lorem ipsum, placeholder copy, or placeholder images anywhere.
- Custom 404 page exists, is styled, and is helpful.
- Draft and utility pages are excluded from indexing or removed.
- Every page checked at every breakpoint (edit-safety + responsive-quality rules).

## 2. SEO & meta

- Unique title (~50–60 chars) and meta description (~150–160 chars) per page; Open Graph + Twitter card fields set, OG image 1200×630.
- Clean slugs: lowercase, hyphenated, no junk parameters.
- No accidental noindex on live pages; XML sitemap enabled in Site Settings.
- 301 redirects entered for every changed URL.

## 3. Schema (JSON-LD)

- Site-wide: Organization (or LocalBusiness) + WebSite + BreadcrumbList in Site Settings head code. Per-type: Article/BlogPosting on posts, Service/Product where relevant (seo-essentials rule).
- Schema reflects **visible content only**; dates in ISO 8601; URLs absolute (relative URLs silently break BreadcrumbList).
- Note: FAQ and HowTo rich results are deprecated in Google Search — keep FAQ content for users if useful, but don't build FAQ/HowTo schema expecting rich results.
- Validate every block with Google's Rich Results Test and validator.schema.org.

## 4. Accessibility sweep

- Keyboard-only pass of every key page: tab through everything, focus visible throughout, no traps, modals close on Escape and return focus.
- Contrast spot-check on the Theme token pairings; run axe DevTools or Lighthouse accessibility.
- Skip-to-content link present; screen-reader smoke test (VoiceOver/NVDA) on the primary flow.

## 5. Media & performance

- Every image: WebP, exported ≤2× display size, width/height attributes set, correct eager/lazy + `fetchpriority` (links-and-media rule).
- Fonts: WOFF2, ≤2 families, `display: swap`, primary font preloaded (performance rule).
- Lighthouse / PageSpeed on the staged URL: LCP < 2.5s, INP < 200ms, CLS < 0.1.
- Webflow minify on; no render-blocking third-party scripts crept in.

## 6. Forms & integrations

- Real test submission on every form; notification recipients confirmed; spam protection live; error and success states verified (forms rule).
- Analytics / tag manager firing; cookie consent present if required.

## 7. Settings

- Favicon (32×32) + webclip set — never the Webflow default (seo-essentials rule).
- Locale = {{SITE_LOCALE}} so `lang="{{LANG_CODE}}"` renders.
- Custom domain connected, SSL on, https enforced, no mixed content; www/non-www resolve to one canonical form.
- Site password removed (unless intentionally staging).

## 8. Post-launch (after the site owner publishes)

- Submit the sitemap in Google Search Console; request indexing on key pages.
- Console check + real-device test on the live URL.
- Watch Search Console Coverage and Enhancements after the first crawl for index or schema errors.
- Re-run PageSpeed on the live URL.

## Output format

Report every item as ✅ pass · ⚠ needs attention (with the specific fix) · ❌ blocker. Deliver the report with staged changes; the site owner reviews and publishes.
