# Best Practices reference

Goal: the page is built on a correct, secure, modern foundation — the "is this done right" category. Overlaps the Lighthouse Best Practices audit plus general web hygiene.

## The checklist

### Security & transport
- **HTTPS everywhere.** No HTTP resources on an HTTPS page (**mixed content** breaks the padlock and can be blocked).
- No secrets/API keys in client-side code.
- Security headers (verify on the live response — can't see from HTML alone):
  - `Content-Security-Policy` (at least a baseline)
  - `Strict-Transport-Security` (HSTS)
  - `X-Content-Type-Options: nosniff`
  - `Referrer-Policy`
  - `X-Frame-Options` / CSP `frame-ancestors`
- External links with `target="_blank"` use `rel="noopener"` (and usually `noreferrer`).
- Forms post to HTTPS endpoints.

### Correctness & standards
- **Valid HTML:** proper `<!DOCTYPE html>`, well-formed, no duplicate IDs, properly nested/closed tags.
- **`<head>` essentials:** `<meta charset="utf-8">` (first), `<meta name="viewport">`, `<html lang>`.
- **No console errors or warnings** on load (JS errors, failed requests, deprecation notices).
- **No deprecated APIs** (e.g. legacy `document.write`, outdated libraries, removed browser APIs).
- **No broken resources** — 404s on images/CSS/JS, broken links.
- Correct, non-deprecated CSS; no reliance on vendor-prefixed-only properties without standard fallback.

### Images & media
- Images served at correct resolution (not a giant file scaled down in CSS) — overlaps performance.
- Correct aspect ratio (not distorted by mismatched width/height).
- Modern formats where supported.

### Trust & UX hygiene
- Favicon present and valid.
- 404 and error pages are real, helpful pages.
- No intrusive interstitials that block content (also an SEO/UX penalty risk).
- Cookie/consent handling present where legally required; consent UI doesn't cause layout shift (overlaps CLS) and defaults to privacy-preserving.
- Third-party scripts loaded over HTTPS from trusted origins.

### Privacy / compliance signals (flag, don't legally advise)
- A privacy policy / cookie notice exists where expected.
- Trackers/analytics disclosed; consent gating where required by jurisdiction.
- (Note: this skill flags presence/absence; it does not give legal compliance opinions.)

## Fixes by form
- **Files/custom:** fix markup, swap HTTP→HTTPS resources, add `rel="noopener"`, fix console errors, replace deprecated APIs. Security *headers* are server/host config — provide the values and tell the user where their stack sets them.
- **Webflow:** HTTPS is automatic on Webflow hosting; security headers are limited on standard hosting (note this constraint); `rel` attributes via element settings or custom code; favicon in Site Settings.
- **WordPress:** headers via server config / a security plugin; HTTPS via host + a force-HTTPS setting/plugin; console errors often from plugins/theme — isolate the culprit.
- **Shopify:** HTTPS automatic; headers are largely managed by Shopify (limited control — note this); fixes mostly in theme `.liquid`/JS; favicon in theme settings.

## What you can confirm from static files vs. not
- **From code:** mixed content references, missing charset/viewport/lang, `target="_blank"` without `rel`, deprecated APIs in the JS, malformed HTML, duplicate IDs, hardcoded secrets, http:// asset URLs.
- **Needs live/server access:** response security headers, HSTS, actual console errors at runtime, broken-resource 404s, TLS config, redirect behavior. Flag these as "verify on the live response / DevTools console / a headers checker."
