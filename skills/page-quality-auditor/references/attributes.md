# Attributes cheat-sheet

A practical reference of HTML attributes that improve performance, accessibility, SEO, and correctness — with the **right value** and **when (and when not)** to use each. Misapplied attributes hurt (e.g. lazy-loading the hero image tanks LCP; a wrong `aria-label` overrides the visible name). Use this when applying fixes or building to spec.

## Performance attributes

### `loading` (on `<img>`, `<iframe>`)
- `loading="lazy"` — defer loading until near viewport. Use for **below-the-fold** images/iframes.
- `loading="eager"` (default) — load immediately. Use for **above-the-fold** content.
- **Do NOT lazy-load the LCP image** (usually the hero). Lazy-loading it delays the largest paint and wrecks LCP. The biggest, earliest image should be eager + high priority.
- Rule of thumb: hero/first-screen → eager; everything further down → lazy.

### `fetchpriority` (on `<img>`, `<link>`, `<script>`)
- `fetchpriority="high"` — raise priority. Put it on the **LCP image** and other critical-path resources so the browser fetches them first.
- `fetchpriority="low"` — lower priority for non-critical resources (e.g. a below-fold image you still want eager-ish, or a deferred third-party).
- Pair the LCP image: `fetchpriority="high"` + no `loading="lazy"` + optionally a `<link rel="preload">`.

### `decoding` (on `<img>`)
- `decoding="async"` — decode off the main thread; good default for most images, helps responsiveness (INP-adjacent).
- `decoding="sync"` — only when the image must be ready before paint (rare).

### `width` / `height` (on `<img>`, `<video>`, `<iframe>`)
- Always set intrinsic `width` and `height` (or CSS `aspect-ratio`). Lets the browser reserve space → prevents layout shift (**CLS**). This is the single most common CLS fix.
- They set the aspect ratio; CSS (`width:100%; height:auto`) still controls displayed size responsively.

### `srcset` / `sizes` (on `<img>`, `<source>`)
- `srcset` — offer multiple resolutions so the browser picks the right one per device/DPR (avoids shipping a 2000px image to a phone). Big LCP/bandwidth win.
- `sizes` — tell the browser the displayed width per breakpoint so it chooses correctly.
- Example: `srcset="hero-800.avif 800w, hero-1600.avif 1600w" sizes="(min-width: 62rem) 50vw, 100vw"`.

### Resource hints (on `<link>` in `<head>`)
- `rel="preload"` (+ `as="image"|"font"|"style"|"script"`) — fetch a critical resource early. Use for the **LCP image** and **critical fonts**. `as` is required; for fonts add `crossorigin`.
- `rel="preconnect"` — open the connection to a required cross-origin (font host, CDN, critical API) early. Add `crossorigin` for fonts.
- `rel="dns-prefetch"` — cheaper DNS-only hint for less-critical origins.
- `rel="prefetch"` — fetch a resource likely needed for the **next** navigation (low priority).
- Don't over-preload — preloading everything de-prioritizes everything. Reserve for genuinely critical assets.

### Script loading (on `<script>`)
- `defer` — download in parallel, execute after HTML parse, in order. **Default choice** for most scripts; keeps JS off the render-blocking path.
- `async` — download in parallel, execute as soon as ready, no order guarantee. Use for independent third-party scripts (analytics) that don't depend on others or the DOM.
- Neither (plain `<script>` in `<head>`) — render-blocking. Avoid; move to end of `<body>` or add `defer`.

### Other
- `rel="noopener"` on `target="_blank"` links — also a perf/security item: prevents the new page accessing `window.opener`.
- `font-display: swap` (CSS, not an attribute, but the partner to font preload) — avoids invisible text and reduces font-driven CLS.

## Accessibility attributes

### Naming (give elements an accessible name)
- `alt` (on `<img>`) — describe the image's meaning. Decorative image → `alt=""` (empty, present). Never omit `alt`. Don't start with "image of"; describe content/purpose.
- `aria-label` — provides an accessible name when there's **no visible text** (icon-only button, icon link). Don't put it on elements that already have visible text labels (it overrides them and desyncs from what's seen).
- `aria-labelledby` — name an element by referencing the ID(s) of visible text. Prefer this over `aria-label` when visible text exists.
- `aria-describedby` — attach supplementary description (e.g. a form field's help/error text) by ID. Doesn't replace the label.
- `<label for="id">` — the correct, first-choice way to label form inputs. Placeholder is **not** a label.
- `title` — weak/unreliable for AT; don't rely on it for naming. (Fine as a supplemental tooltip only.)

### State & relationships
- `aria-expanded="true|false"` — on a toggle/disclosure/menu button; reflects open state. Update it in JS when toggling.
- `aria-controls="id"` — points a control to the element it controls (e.g. button → menu).
- `aria-current="page|step|true"` — marks the current item in nav/breadcrumbs/steps.
- `aria-hidden="true"` — hide purely decorative content from AT. **Never** put it on focusable/interactive content (creates a "ghost" focus stop).
- `aria-live="polite|assertive"` — announce dynamic content changes (toasts, validation, async results). `polite` for most; `assertive` for urgent.
- `aria-invalid="true"` + `aria-describedby` → the error text, on a field that failed validation.
- `role="..."` — only when no native element exists. Prefer native (`<button>`, `<nav>`, `<main>`) over `role="button"` etc. Bad/invalid roles are worse than none.

### Keyboard & focus
- `tabindex="0"` — make a custom interactive element focusable in normal order (only if you've also added keyboard handlers + role). Prefer a native `<button>`/`<a>` instead.
- `tabindex="-1"` — focusable by script only (e.g. move focus to a heading/dialog), not in tab order. Useful for skip-link/dialog focus management.
- **Avoid `tabindex` > 0** — it breaks natural tab order. Almost always a smell.
- `accesskey` — generally avoid; conflicts with AT/browser shortcuts.

### Language & document
- `lang` (on `<html>`, and on inline elements for language changes) — correct language code. Helps screen-reader pronunciation (and SEO).

### Media
- `<track kind="captions">` on `<video>` — captions/subtitles.
- `controls` on audio/video — keyboard-operable native controls.

## SEO attributes
- `rel="canonical"` (`<link>`) — the preferred URL for duplicate/variant pages.
- `rel="nofollow"` / `rel="sponsored"` / `rel="ugc"` (on `<a>`) — don't pass ranking signal / mark paid / user-generated links.
- `rel="alternate" hreflang="xx"` (`<link>`) — language/region variants.
- `meta name="robots" content="index,follow|noindex|nofollow"` — indexing control (confirm it's not accidentally `noindex`).
- `meta property="og:*"` / `name="twitter:*"` — social sharing (title, description, image, url, type, card).
- Descriptive `href` + meaningful link text (not "click here") — crawlable and accessible.

## Correctness / best-practice attributes
- `lang` on `<html>` (required), `charset="utf-8"` (first meta), `name="viewport" content="width=device-width, initial-scale=1"`.
- `rel="noopener"` (and usually `noreferrer`) on every `target="_blank"`.
- `type` on `<input>` — correct type (`email`, `tel`, `url`, `number`, `search`) → right mobile keyboard + native validation.
- `autocomplete="..."` on inputs (e.g. `email`, `name`, `current-password`) — faster, more accessible form fill.
- `inputmode` — refine the on-screen keyboard without changing validation (`numeric`, `decimal`, `tel`).
- `crossorigin` on `<link rel="preload" as="font">` and CORS-served assets — required for fonts/anonymous fetches.
- `integrity` + `crossorigin` (SRI) on third-party `<script>`/`<link>` — verify the resource wasn't tampered with.
- Unique `id` values (no duplicates) — duplicates break label/ARIA associations and are invalid HTML.

## Quick "right value" reminders
- LCP image: `fetchpriority="high"`, **no** `loading="lazy"`, ideally `<link rel="preload" as="image">`, plus `width`/`height`, `decoding="async"`.
- Below-fold image: `loading="lazy"`, `decoding="async"`, `width`/`height`, `srcset`/`sizes`.
- Icon-only button: `<button aria-label="Close">` (not a `<div>`); add `aria-expanded` if it toggles something.
- Visible-text button: no `aria-label` — the text is the name.
- Form field: `<label for>` + matching `id`; errors via `aria-describedby` + `aria-invalid="true"`.
- External link in new tab: `target="_blank" rel="noopener noreferrer"`.
- Non-critical script: `defer` (or `async` if independent).
- Decorative image: `alt=""`. Decorative SVG/icon: `aria-hidden="true"` + `focusable="false"`.
