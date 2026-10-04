---
name: page-quality-auditor
description: Audit and improve web pages across Performance, SEO, Accessibility, and Best Practices (the Lighthouse categories). Use whenever the user wants a page reviewed, scored, or optimized for page speed and Core Web Vitals (LCP, INP, CLS), SEO (meta tags, headings, structured data, crawlability), accessibility (a11y, WCAG, screen readers, contrast, alt text), or best practices (HTTPS, console errors, security headers). Works on live URLs and on HTML/CSS/JS files, and serves double duty — an AUDIT tool producing a prioritized report, AND a BUILD-TIME STANDARD applied while writing/editing page code so it comes out clean. Trigger on phrases like "audit my site", "improve page speed", "is this accessible", "fix my SEO", "Lighthouse score", "Core Web Vitals", "make this WCAG compliant", "review this page", or any request to make a page faster / findable / more accessible. Platform-aware for Webflow, WordPress, and Shopify, works on any stack. Output is a prioritized report PLUS code changes applied to the user's files.
---

## Changes

- 22 Sep 2026: editable master moved to `~/Documents/AI Agent Config/skills/`. Synced claude.ai copy is the published twin; re-upload after improvements.

# Page Quality Auditor

Review and improve web pages across the four Lighthouse categories — **Performance, SEO, Accessibility, Best Practices** — and either report findings, apply fixes, or both. Works on live URLs and on local HTML/CSS/JS. Also doubles as a build-time standard: the same criteria that catch problems in an audit are the rules to build against from the start.

The goal isn't a vanity score. It's pages that load fast, get found, work for everyone, and follow current web conventions — with fixes the user can actually ship.

> **Companion skill:** pairs with `webflow-ui-design` (often shipped alongside). That skill handles design, Client-First structure, and the Webflow-conversion launch checklist; this one is the deep quality engine it defers to for SEO / a11y / performance / best-practices detail. This skill is standalone and platform-agnostic (Webflow, WordPress, Shopify, any stack) — it doesn't require the design skill to function.

## Two modes

**Audit mode** — the user points at a page and wants to know what's wrong and how to fix it. Produce a prioritized report; then apply the code changes (see Output).

**Build-time mode** — the user is writing or editing page code and wants it to come out clean. Apply the relevant per-category criteria as you build, and end with a short conformance note instead of a full report. Don't run a heavy audit on code you just wrote to spec — just confirm it meets the standard and flag anything you couldn't control (e.g. server headers).

When unclear which mode, infer from the verb: "audit / review / check / score / why is this slow" → audit; "build / write / add / make this page…" → build-time.

## Workflow (audit mode)

### 1. Get the page
- **URL:** fetch it. Read the rendered HTML, linked CSS/JS, `<head>`, and resource hints. Note what you *can't* see from HTML alone (real Core Web Vitals need field/lab data — say so rather than guessing a number).
- **Files:** read the HTML and its linked assets. View the directory first to find the CSS/JS the HTML references.
- Identify the platform (Webflow / WordPress / Shopify / custom) — it changes which fixes are possible and how they're applied. See `references/platform-notes.md`.

### 2. Triage across all four categories
Do a fast first pass using the checklist below, then read the matching reference file(s) for any category with real issues to audit it properly. Don't read all four references reflexively — read the ones that matter for this page.

| Category | Read | First-pass smell test |
|---|---|---|
| Performance | `references/performance.md` | Unoptimized/oversized images, no width/height, render-blocking JS/CSS, no lazy-load, heavy fonts, no caching/compression |
| SEO | `references/seo.md` | Missing/weak `<title>`/meta description, no/multiple `<h1>`, no canonical, no structured data, non-descriptive links, blocked crawling |
| Accessibility | `references/accessibility.md` | Missing alt text, low contrast, no labels on inputs, no focus states, poor heading order, missing landmarks, keyboard traps |
| Best Practices | `references/best-practices.md` | HTTP not HTTPS, console errors, deprecated APIs, missing `lang`/charset/viewport, no security headers, mixed content |

Cross-cutting: `references/attributes.md` is a cheat-sheet of HTML attributes (with correct values and when-not-to-use notes) that fix issues across performance, a11y, and SEO — read it whenever a fix is "add/correct an attribute."

### 3. Verify, don't assume
Where you can confirm a problem from the actual code (e.g. an `<img>` with no `alt`, a `<title>` that's missing), state it as fact. Where it depends on runtime/server data you can't see (real CWV timings, response headers on a URL you only have HTML for), say it's likely/unverifiable and tell the user how to confirm (PageSpeed Insights, DevTools, the response headers). Don't invent metric numbers.

### 4. Report — prioritized by impact
Use the report format below. Order fixes by impact × effort: high-impact/low-effort first. Each finding names the issue, why it matters, and the concrete fix.

### 5. Apply the fixes
Then make the actual code changes to the user's files (or give exact paste-ready snippets for URL/platform cases where you don't have the files). For Webflow/WordPress/Shopify, give the fix in the form the platform actually accepts (see platform notes) — e.g. a Webflow custom-code embed, a WordPress functions.php / plugin setting, a Shopify Liquid edit. Don't hand someone a raw `.htaccess` rule for a Webflow site.

When a fix is an HTML attribute (`loading`, `fetchpriority`, `decoding`, `srcset`/`sizes`, `aria-label`, `aria-expanded`, `rel`, resource hints, etc.), consult `references/attributes.md` for the correct attribute **and value** — the value is where these go wrong (lazy-loading the LCP image, an `aria-label` overriding visible text, `loading="lazy"` on an above-fold image). Apply the right one, not just any one.

## Report format

Use this structure:

```markdown
# Page Quality Audit — [page/URL]
**Platform:** [Webflow / WordPress / Shopify / custom]   **Audited:** [what you analyzed: HTML only, HTML+CSS+JS, live URL]

## Summary
[2–4 sentences: overall state, the biggest wins, anything you couldn't verify.]

## Findings (prioritized)
### 🔴 High impact
- **[Issue]** — [why it matters]. Fix: [concrete change].
### 🟡 Medium impact
- ...
### 🟢 Low impact / polish
- ...

## Couldn't verify from here
- [Things needing field data / server access / a live run, and how to check them.]

## Fixes applied
- [What was changed in which file, or the snippets to paste and where.]
```

Keep it scannable. Don't pad — if a category is clean, say so in one line.

## Thresholds that matter (quick reference)

Core Web Vitals "good" at the 75th percentile of real users: **LCP < 2.5s, INP < 200ms, CLS < 0.1**. INP replaced FID in 2024 and is the most commonly failed of the three. Note: some 2026 sources claim Google tightened "good" LCP to < 2.0s — treat that as unconfirmed and verify against Google's own `web.dev`/`developers.google.com` guidance before citing a hard number to a client. Full per-metric detail and fixes in `references/performance.md`.

## Build-time mode (applying the standard while building)

When writing/editing page code, bake in the defaults that prevent the common findings:
- Images: explicit `width`/`height` (or aspect-ratio), modern format (AVIF/WebP), `loading="lazy"` except the LCP image, `fetchpriority="high"` on the LCP image.
- Head: `<html lang>`, charset, viewport, a real `<title>` and meta description, canonical, Open Graph basics.
- Semantics & a11y: one `<h1>`, ordered headings, landmark elements, labels for every input, visible focus states, alt text, AA contrast.
- JS/CSS: defer non-critical JS, avoid render-blocking, keep main-thread work small (protects INP).
- Always HTTPS, no console errors, no deprecated APIs.

`references/attributes.md` has the correct attribute + value for each of these (and more). Pull from it so you apply, e.g., `fetchpriority="high"` on the LCP image rather than lazy-loading it, `aria-label` only where there's no visible text, `defer` on non-critical scripts.

End with a one-paragraph conformance note: what the code already satisfies and what's outside your control (server headers, CDN, real-user metrics).

## Don'ts

- Don't report a numeric performance score or CWV timing you didn't measure — describe the likely issues and point to the measuring tool instead.
- Don't give platform-incompatible fixes (raw server config for a hosted no-code platform). Match the fix to the platform.
- Don't dump all four reference files into context for a page that only has one category of problems.
- Don't "fix" by hiding problems (e.g. `outline: none` to silence a focus warning, or `aria-hidden` to mute a contrast issue). Fix the underlying cause.
- Don't overclaim WCAG conformance. Say which checks pass; full conformance requires testing this skill can't fully perform (e.g. real assistive-tech testing).
