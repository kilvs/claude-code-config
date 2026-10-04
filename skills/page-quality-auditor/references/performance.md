# Performance reference

Goal: fast loading, responsive interaction, stable layout. The scoring proxy is Core Web Vitals, but the real target is the user experience those metrics stand in for.

## Core Web Vitals (the three that count)

Measured at the **75th percentile of real users** (field data), classified Good / Needs Improvement / Poor.

| Metric | Measures | Good | Poor | Most common causes |
|---|---|---|---|---|
| **LCP** (Largest Contentful Paint) | Loading — when the largest element paints | < 2.5s | > 4.0s | Slow server/TTFB, render-blocking resources, unoptimized/late-loaded hero image, no preload |
| **INP** (Interaction to Next Paint) | Responsiveness — full lifecycle of every interaction | < 200ms | > 500ms | Long JS tasks, heavy event handlers, large DOM, main-thread congestion |
| **CLS** (Cumulative Layout Shift) | Visual stability | < 0.1 | > 0.25 | Images/iframes/ads without dimensions, web fonts (FOIT/FOUT), content injected above existing content |

**Verification note:** real CWV come from CrUX/field data or a lab run (PageSpeed Insights, Lighthouse, DevTools). You cannot read them off static HTML. When auditing HTML/files, describe the *likely* CWV issues from the causes above and tell the user to confirm at `pagespeed.web.dev`. Do not state a CWV number you didn't measure.

> Some 2026 SEO blogs claim Google lowered "good" LCP to < 2.0s in a March 2026 update. This is not clearly confirmed by Google's primary docs. Use < 2.5s as the established threshold and, if precision matters for a client, verify the current value on `web.dev` / `developers.google.com` before quoting < 2.0s.

## Highest-impact fixes, by metric

### LCP
- Identify the LCP element (usually the hero image or a large heading). Serve it with `fetchpriority="high"` and **do not** `loading="lazy"` it.
- `<link rel="preload">` the LCP image/font.
- Modern image formats (AVIF, then WebP fallback), correctly sized per breakpoint with `srcset`/`sizes`.
- Inline critical CSS; defer the rest. Eliminate render-blocking JS in `<head>` (`defer`/`async`).
- Preconnect to required origins (`<link rel="preconnect">`) for fonts/CDN.
- Reduce TTFB: caching, CDN, server response time.

### INP
- Break up long JavaScript tasks; yield to the main thread (`scheduler.yield()` / chunking) during interactions.
- Defer or remove non-critical JS; reduce third-party scripts (tag managers, chat widgets, analytics stacks are frequent culprits).
- Keep the DOM small and shallow; large/deep DOMs slow every interaction.
- Avoid expensive work in input/scroll handlers; debounce/throttle, use passive listeners.

### CLS
- Set explicit `width`/`height` (or CSS `aspect-ratio`) on **every** image, video, iframe, and ad slot.
- Reserve space for dynamic/injected content (banners, embeds, cookie bars).
- Fonts: `font-display: swap` and preload the font to avoid late reflow; match fallback metrics where possible.
- Never insert content above existing content after load unless in response to a user action.

## General performance hygiene (visible from code)
- **Images:** right-sized, compressed, modern format, `loading="lazy"` for below-the-fold, dimensions set. The single biggest win on most pages.
- **Fonts:** subset, `woff2`, `font-display: swap`, preload the critical face, limit families/weights.
- **JS/CSS:** minify, tree-shake, defer non-critical, remove unused. Avoid huge frameworks for simple pages.
- **Delivery:** gzip/Brotli compression, long cache lifetimes on static assets, HTTP/2+, CDN. (These are server-side — flag as "verify on the live response" when you only have HTML.)
- **Third parties:** audit each; lazy-load or remove. They're often the largest INP/LCP cost.

## What you can confirm from static files vs. not
- **From files/HTML:** missing image dimensions, `lazy` on the hero, render-blocking `<script>` in head, missing preload/preconnect, oversized inline data URIs, no `srcset`, heavy font declarations, large/deep DOM.
- **Needs live/server/field data:** actual LCP/INP/CLS numbers, TTFB, compression, cache headers, CDN, third-party runtime cost. Recommend PageSpeed Insights / DevTools and say so explicitly.
