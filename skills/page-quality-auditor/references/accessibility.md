# Accessibility reference

Goal: the page works for everyone, including people using screen readers, keyboards, magnification, or with low vision / motor / cognitive differences. Target **WCAG 2.2 Level AA** as the practical bar.

**Honesty rule:** automated/code review catches maybe 30–40% of WCAG issues. Real conformance needs keyboard testing, screen-reader testing, and human judgment. Report which checks pass and which need manual testing — never claim full WCAG conformance from a code read alone.

## The checklist (grouped by WCAG principle)

### Perceivable
- **Text alternatives:** every meaningful `<img>` has descriptive `alt`; decorative images use `alt=""` (empty, not missing). Icons that convey meaning need accessible names. Complex images (charts) need longer descriptions.
- **Color contrast:** body text ≥ **4.5:1**, large text (≥24px or ≥18.66px bold) ≥ **3:1**, UI components/graphical objects ≥ **3:1** against adjacent colors. Check actual computed colors.
- **Don't rely on color alone** to convey information (e.g. error states need text/icon, not just red).
- **Captions/transcripts** for audio/video.
- Content reflows at 320px width and 200% zoom without loss (responsive, no horizontal scroll trap).

### Operable
- **Keyboard:** every interactive element is reachable and operable by keyboard; no keyboard traps. Tab order is logical.
- **Visible focus:** clear focus indicator on all interactive elements. Never `outline: none` without a replacement focus style. (WCAG 2.2 adds Focus Appearance/Not Obscured criteria.)
- **Targets:** interactive targets ≥ 24×24px (WCAG 2.2) — ideally 44×44.
- **No motion traps:** respect `prefers-reduced-motion`; nothing flashes more than 3×/sec; auto-playing/moving content can be paused.
- **Skip link** to main content for keyboard/screen-reader users.

### Understandable
- **`<html lang>`** set correctly (also SEO).
- **Form labels:** every input has a programmatic label (`<label for>`, `aria-label`, or `aria-labelledby`) — placeholder text is not a label.
- **Error identification:** errors are described in text and associated with their field (`aria-describedby`); instructions don't rely on sensory cues alone.
- Predictable, consistent navigation and component behavior.

### Robust
- **Valid, semantic HTML:** real `<button>`/`<a>`/`<nav>`/`<main>`/`<header>`/`<footer>`, headings in order. Don't rebuild native controls from `<div>`s without full ARIA + keyboard support.
- **Landmarks:** one `<main>`, plus `<nav>`, `<header>`, `<footer>`; ARIA landmarks only where semantic elements aren't possible.
- **ARIA used correctly:** prefer native semantics; ARIA only to fill gaps. No invalid roles, no `aria-hidden` on focusable content, names/roles/values exposed for custom widgets. **Bad ARIA is worse than none.**
- **One `<h1>`**, logical heading hierarchy (no skipped levels).

## Common anti-patterns to flag
- `<div onclick>` instead of `<button>` (not keyboard/AT accessible).
- `outline: none` on focus with no replacement.
- Placeholder used as the only label.
- Missing/auto-generated unhelpful alt (`alt="image123.jpg"`).
- Low-contrast "subtle" grey text on white.
- Icon-only buttons with no accessible name.
- `aria-hidden="true"` hiding real content; or muting a warning instead of fixing it.

## Fixes by form
- **Files/custom:** edit markup/CSS directly — swap `div`→`button`, add `alt`/labels/`for`, add focus styles, fix contrast tokens, add skip link and landmarks.
- **Webflow:** alt text per image in the asset/element settings; semantic tags via the element's Tag setting; focus states via the Focused state in the Designer; custom ARIA via element custom attributes.
- **WordPress:** theme template + CSS edits; some via block settings; recommend an a11y-ready theme and manual testing — plugins ("accessibility overlays") do **not** create conformance and can make things worse; advise against overlay widgets.
- **Shopify:** theme `.liquid` + CSS; alt text per image in admin; many issues live in theme code.

## What you can confirm from static files vs. not
- **From code:** missing alt, missing labels, `div`-as-button, missing lang, heading order, missing landmarks, `outline:none`, target sizes in CSS, ARIA misuse, color values for contrast (compute it).
- **Needs manual testing:** actual keyboard operability of complex widgets, screen-reader announcement quality, focus order in practice, reflow/zoom behavior, motion. Say these need a manual pass and (optionally) name tools: axe DevTools, WAVE, Lighthouse a11y, plus real keyboard + VoiceOver/NVDA testing.
