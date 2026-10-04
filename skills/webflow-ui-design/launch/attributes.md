# Optimising attributes — for the HTML reference file → Webflow

The attributes to put on elements in the designed HTML reference file so the developer can port them straight onto Webflow elements. Each row: the attribute, its value, what it does, and **where it goes in Webflow** (native setting vs the element's custom-attributes panel).

For the full attribute catalogue with every value and when-NOT-to-use caveat, use `page-quality-auditor/references/attributes.md`. This file is the Webflow-handoff subset — the ones worth pre-setting in the reference file.

## Images (`<img>`)

| Attribute | Value | Why | Webflow |
|---|---|---|---|
| `alt` | descriptive, or `""` if decorative | a11y + SEO | Native: image element → Alt text (or "from CMS field") |
| `width` / `height` | intrinsic pixel dims | reserves space, prevents CLS | Webflow sets these when you upload; for embeds, custom attrs |
| `loading` | `lazy` (below fold) | defer offscreen images | Native lazy-load toggle; default lazy. **Hero: set to eager** |
| `loading` | `eager` (hero/LCP) | don't defer the LCP image | Native: set the hero image load to "eager" |
| `fetchpriority` | `high` (LCP image only) | fetch hero first | Custom attribute `fetchpriority="high"` |
| `decoding` | `async` | decode off main thread | Custom attribute `decoding="async"` |
| `srcset` / `sizes` | resolution set + displayed widths | right image per device | Webflow generates responsive images automatically; verify on |

Rule: hero/LCP image = `eager` + `fetchpriority="high"` + NOT lazy. Everything below the fold = `lazy` + `decoding="async"`.

## Links (`<a>`)

| Attribute | Value | Why | Webflow |
|---|---|---|---|
| `rel` | `noopener` (new-tab links) | security (prevents `window.opener` access) | Custom attribute, or Webflow adds it when "open in new tab" is set |
| `rel` | `noreferrer` | also strip referrer | Custom attribute |
| `rel` | `nofollow` / `sponsored` / `ugc` | mark paid/user links for SEO | Custom attribute |
| `aria-label` | accessible name | when link text isn't descriptive (icon links) | Custom attribute |
| `target` | `_blank` | new tab | Native: link settings → open in new tab |

## Iframes / embeds (`<iframe>`)

| Attribute | Value | Why | Webflow |
|---|---|---|---|
| `loading` | `lazy` | defer offscreen embeds | Custom attribute on the embed |
| `title` | descriptive | a11y (names the frame) | Custom attribute |
| `width` / `height` or aspect-ratio box | intrinsic | prevents CLS from late embeds | wrap in an aspect-ratio `_image_wrap`-style box |

## Document head (per page)

| Element | Why | Webflow |
|---|---|---|
| `<title>` | SEO | Native: Page settings → SEO title |
| `<meta name="description">` | SEO | Native: Page settings → SEO meta description |
| `<link rel="canonical">` | dedupe | Native: Page settings → canonical (or head custom code) |
| `og:*` / `twitter:*` | social cards | Native: Page settings → Open Graph fields |
| `<link rel="preload" as="font">` (primary font) | LCP/font perf | Site/Page custom code head |
| `<html lang="...">` | a11y/SEO | Native: Site settings → language |

## Accessibility attributes

| Attribute | Value | Why | Webflow |
|---|---|---|---|
| `aria-label` | accessible name | icon buttons, unlabeled controls | Custom attribute |
| `aria-hidden` | `true` | hide decorative icons from AT | Custom attribute |
| `aria-expanded` / `aria-controls` | state + target id | menus, accordions, dropdowns | Custom attribute (or Webflow's interaction components) |
| `role` | landmark/widget role | only when a native tag can't express it | Custom attribute — prefer the right tag first |
| `tabindex` | `0` (focusable) / `-1` (programmatic) | keyboard order; avoid positive values | Custom attribute, sparingly |

Prefer the correct **semantic tag** over ARIA: set the element's tag in the Designer (`button`, `a`, `nav`, `header`, `main`, `footer`, `h1`–`h6`) so it's accessible by default. ARIA only fills gaps the tag can't.

## Custom data attributes already in this skill

These carry over as Webflow custom attributes too:
- `data-animate="<preset>"`, `data-animate-trigger="load"`, `data-animate-split`, plus `data-nav`, `data-accordion`, `data-tabs` and their parts — motion (see animation.md). The presets are site-scoped IX3 interactions; the state helper sits in site custom code.
- `data-variant="light|dark"` — theme variant (see client-first.md). Switches the active token set inside the wrapper.

## How to add a custom attribute in Webflow

Select the element → Settings panel (gear) → Custom attributes → add `Name` + `Value`. This is where every non-native attribute above lives. Native settings (alt, lazy-load, SEO title/meta, OG, new-tab rel) have dedicated fields — use those first; custom attributes for the rest.
