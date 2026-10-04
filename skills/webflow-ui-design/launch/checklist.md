# Launch Checklist (pre + post) — design file → Webflow

This is the quality contract baked into the **designed HTML reference file** this skill produces, and the checklist to run before and after the Webflow build. The HTML file is the source of truth (like a Figma design, but already best-practices-correct); the developer rebuilds it in Webflow and ports the attributes/meta/schema across.

**Division of labour:** this checklist covers the design-file-level and launch-level items specific to the Webflow workflow. For the deep per-criterion detail (every a11y rule, every perf technique, full attribute values), defer to the `page-quality-auditor` skill and its references (`seo.md`, `accessibility.md`, `performance.md`, `best-practices.md`, `attributes.md`) — don't re-derive them here. Use that skill in build-time mode while writing the HTML, then run this checklist at launch.

Mark each item: built into the HTML reference file (✎), or a Webflow-Designer/setting step the dev does (⚙).

---

## SEO

### Pre-launch
- ✎ One `<h1>` per page, correct heading order (no skipping levels for visual size — use `heading-style-h*` to decouple size from level).
- ✎ `<title>` unique per page, ~50–60 chars, primary keyword near front.
- ✎ `<meta name="description">` unique, ~150–160 chars, compelling (not keyword-stuffed).
- ✎ Open Graph + Twitter card meta (`og:title`, `og:description`, `og:image`, `og:url`, `og:type`, `twitter:card`). OG image 1200×630.
- ✎ Semantic landmarks: `header`, `nav`, `main`, `footer`, `article`/`section` where meaningful.
- ✎ Descriptive link text (no "click here"); descriptive `alt` on meaningful images, empty `alt=""` on decorative ones.
- ✎ Canonical tag placeholder (`<link rel="canonical">`) — note the real URL for the dev.
- ✎ Clean, readable URL slug intent noted (lowercase, hyphenated, no params).
- ⚙ `robots.txt` allows crawl; no accidental `noindex` on live pages.
- ⚙ XML sitemap enabled (Webflow auto-generates; confirm it's on in Site settings → SEO).

### Post-launch
- ⚙ Submit sitemap in Google Search Console; verify property.
- ⚙ Request indexing / confirm key pages indexed (URL Inspection).
- ⚙ Check Search Console Coverage + Enhancements for errors after first crawl.
- ⚙ Confirm canonical resolves to the live https URL; no www/non-www or trailing-slash duplicates.
- ⚙ 301 redirects in place for any changed URLs (Webflow → Site settings → Publishing → 301 redirects).

## Best Practices

### Pre-launch
- ✎ Valid, well-formed HTML; correct `<!DOCTYPE html>`, `lang` on `<html>`, `charset` and responsive `viewport` meta.
- ✎ No console errors from the reference file's own markup/scripts.
- ✎ External links that open new tabs use `rel="noopener"` (and `noreferrer` where appropriate).
- ✎ Favicon + touch icon referenced.
- ⚙ HTTPS enforced (Webflow default; confirm SSL on).
- ⚙ No mixed content (all assets https).

### Post-launch
- ⚙ Test on real mobile + desktop; check console on the live site.
- ⚙ Forms submit and the success/error states work; spam protection (reCAPTCHA/Turnstile) live.
- ⚙ 404 page exists and is helpful; 404s return proper status.
- ⚙ Analytics/tag manager firing; cookie-consent banner present if required.

## Accessibility

### Pre-launch
- ✎ Colour contrast meets WCAG AA (4.5:1 body text, 3:1 large text ≥24px or bold ≥18.66px). Verify before finalizing the palette.
- ✎ Every form input has a `<label>` (or `aria-label`); related inputs grouped with `<fieldset>`/`<legend>`.
- ✎ Visible focus states on all interactive elements (don't remove outlines without a replacement).
- ✎ Images: meaningful → descriptive `alt`; decorative → `alt=""`. Icons that convey meaning get an accessible name.
- ✎ Interactive elements are real buttons/links (`<button>`, `<a>`), not click-handlered `<div>`s. Keyboard operable, logical tab order.
- ✎ Landmarks present; skip-to-content link for keyboard users.
- ✎ `prefers-reduced-motion` respected by any animation (the GSAP `data-*` init handles this — see animation.md).
- ✎ Sufficient touch target size (~44×44px) on interactive controls.

### Post-launch
- ⚙ Keyboard-only pass: tab through the whole page, nothing trapped, focus visible throughout.
- ⚙ Screen-reader smoke test (VoiceOver/NVDA) on key flows.
- ⚙ Run axe DevTools or Lighthouse a11y on the live page; fix flagged issues.
- ⚙ Webflow note: set element-level "aria" / "alt from CMS field" where the design used a dynamic image.

## Schema / JSON-LD markup

### Pre-launch
- ✎ Identify the page type and pick the schema (see priority matrix in `schema-templates.md`). Foundation: Organization (or LocalBusiness) + WebSite + BreadcrumbList site-wide; then Article on blog detail, Product on product pages.
- ✎ Fill the matching template(s) from `schema-templates.md` with real values; include the JSON-LD block(s) in the reference file `<head>` (clearly marked) so the dev knows exactly what to paste.
- ✎ Schema must reflect **visible** content only — never mark up data the user can't see.
- ✎ Dates in ISO 8601 (`2026-01-15`), URLs absolute, `image`/`logo` real URLs, prices as plain numbers with separate `priceCurrency`.
- Note: FAQ and HowTo rich results are deprecated (FAQ removed from Google Search May 2026; HowTo since 2023). Keep FAQ content for users if useful, but don't expect a rich result. Don't invest in HowTo schema.

### Post-launch
- ⚙ In Webflow, paste each JSON-LD block into Page settings → Custom code → Inside `<head>` (Webflow adds no schema on its own). Site-wide blocks (Organization/WebSite) go in Site settings → Custom code → Head.
- ⚙ Validate every block in Google's Rich Results Test and validator.schema.org before calling it done.
- ⚙ After indexing, check Search Console → Enhancements for schema errors.
- ⚙ Confirm `item` URLs in BreadcrumbList are absolute (relative URLs silently break it).

## Page optimisation (performance)

### Pre-launch
- ✎ Images sized to display dimensions; modern format (AVIF/WebP) intended; `width`+`height` (or `aspect-ratio`) set on every `<img>` to prevent CLS.
- ✎ LCP image (usually hero): `fetchpriority="high"`, NOT `loading="lazy"`, optionally `<link rel="preload">`. Everything below the fold: `loading="lazy"` + `decoding="async"`.
- ✎ `srcset`/`sizes` on responsive images so phones don't download desktop-sized files.
- ✎ Fonts: `font-display: swap`; preload the primary font; subset/limit weights (variable font ideal). No more than 2 families.
- ✎ Defer non-critical JS (`defer`/`async`); keep the state helper and other scripts out of the render path.
- ✎ No layout shift from late-loading embeds — reserve space (aspect-ratio box) for video/iframe/widgets.
- (Full attribute values + when-not-to-use: see `page-quality-auditor/references/attributes.md` and `performance.md`.)

### Post-launch
- ⚙ Run PageSpeed Insights / Lighthouse on the live URL (field + lab). Target Core Web Vitals: LCP <2.5s, INP <200ms, CLS <0.1.
- ⚙ Confirm Webflow image settings: responsive images on, lazy-load on for below-fold (Webflow does this by default — verify the hero is set to eager/priority).
- ⚙ Check the published page weight; compress or swap any oversized asset.
- ⚙ Enable Webflow's minify (CSS/JS/HTML) in Site settings → Publishing.
- ⚙ Verify CDN caching and that no render-blocking third-party script crept in.

---

## How this maps into Webflow

The reference HTML is the spec. In Webflow:
- **Meta/title/OG** → Page settings → SEO + Open Graph fields (or Custom code head for anything not exposed).
- **Optimising attributes** (`loading`, `fetchpriority`, `decoding`, `rel`, `aria-*`, `width`/`height`) → element's **custom attributes** panel, or native Webflow settings where one exists (alt text, image lazy-load toggle). See `attributes.md` in this folder for the Webflow-mappable subset.
- **JSON-LD** → Page/Site custom code (head). Webflow never auto-generates schema.
- **Heading/structure/landmarks** → set the element's HTML tag in the Designer (the `_section`, `_content`, semantic tags carry over 1:1).
