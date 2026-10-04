# SEO reference

Goal: the page can be crawled, understood, and represented well in search and social. This covers on-page technical SEO — not content strategy or link building.

## The checklist

### Head & metadata
- **`<title>`** — present, unique, descriptive, ~50–60 chars, primary topic near the front. One per page.
- **Meta description** — present, ~140–160 chars, compelling, accurate. Not keyword-stuffed. (Not a ranking factor, but drives click-through.)
- **Canonical** — `<link rel="canonical">` pointing to the preferred URL. Prevents duplicate-content dilution.
- **`<meta name="viewport">`** — present (mobile-friendliness is a ranking factor).
- **`<html lang>`** — set correctly; helps search and is also an a11y requirement.
- **Robots** — confirm the page isn't accidentally `noindex`/`nofollow` (meta or `X-Robots-Tag`) when it should be indexed.

### Headings & content structure
- Exactly **one `<h1>`** describing the page. Then `<h2>`/`<h3>` in logical, non-skipping order.
- Headings reflect real structure, not styling choices. Don't use a heading because it "looks big."
- Descriptive link text — never "click here" / "read more" with no context (also an a11y win).

### Crawlability & indexing
- `robots.txt` doesn't block important resources or pages.
- An XML sitemap exists and is referenced; submitted in Search Console.
- Internal links let crawlers reach pages within a few clicks.
- Clean, readable, stable URLs; redirects are 301 (permanent) where appropriate; no chains/loops.
- No important content locked behind JS that doesn't render server-side / isn't in the initial HTML (test: view source, not just DevTools).

### Structured data (schema.org)
- Add JSON-LD for the page type: `Organization`/`LocalBusiness`, `Product` + `Offer`, `Article`, `BreadcrumbList`, `FAQPage`, `Recipe`, etc.
- Valid and matching visible content (no markup-only claims). Validate with Google's Rich Results Test / Schema.org validator.

### Social / sharing
- Open Graph: `og:title`, `og:description`, `og:image`, `og:url`, `og:type`.
- Twitter/X card tags (`twitter:card`, etc.) where relevant.
- `og:image` exists and is a sensible size/ratio (≈1200×630).

### Images & media for SEO
- Descriptive `alt` text (overlaps a11y) and meaningful file names.
- Descriptive figure captions where useful.

## Fixes by form
- **Files/custom:** edit the `<head>` and markup directly; add a JSON-LD `<script type="application/ld+json">`.
- **Webflow:** title/description and OG fields are set per-page in Page Settings; canonical and custom head code go in Page Settings → Custom Code; sitemap/robots in Site Settings → SEO.
- **WordPress:** typically via an SEO plugin (Yoast / Rank Math) for titles, meta, canonical, OG, sitemap, schema — recommend configuring there rather than hand-editing the theme.
- **Shopify:** title/description per product/page in admin; OG and schema often need theme `.liquid`/`theme.liquid` edits; many themes already emit `Product` schema — check before adding duplicate.

## What you can confirm from static files vs. not
- **From HTML:** title, meta description, canonical, viewport, lang, heading structure, OG/Twitter tags, JSON-LD presence/validity, alt text, link text, robots meta.
- **Needs live/site access:** robots.txt, sitemap, server redirects/status codes, indexation status, whether JS-rendered content is in the crawlable HTML, Search Console data. Flag these and point to the tool (Search Console, Rich Results Test, `view-source:`).
