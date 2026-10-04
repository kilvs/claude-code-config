# Client-First Dialect & Token Reference

The naming and token system every generated version must follow. This is the user's site dialect (v2.1 flavor, D1/D2/D3 decisions locked Aug 2026) — it exists so Webflow MCP conversion is mechanical, not interpretive.

## 1. Naming dialect

Lowercase only. Hyphens separate words. Underscores separate structural levels (each underscore creates a folder level in Webflow).

| Thing | Pattern | Examples |
|---|---|---|
| Section wrapper | `section-[page]_[element]` (no tag on the wrapper) | `section-home_hero`, `section-about_team`, `section-template-blog_header` |
| Inside a section | `[page]_[element]_[tag]` | `home_hero_content`, `home_projects_list_wrap`, `home_projects_item` |
| Reusable component | `component_[name]` and `component_[name]_[tag]` | `component_product-card`, `component_product-card_content`, `component_product-card_image-wrap` |
| CMS template pages | page identifier = `template-[collection]` | `section-template-blog_hero` wrapper, `template-blog_hero_content` inside |
| Utility classes | never contain an underscore | `padding-global`, `container-large`, `text-size-large`, `button-group` |

Rules:

- Name by role, never appearance: `card_title`, not `card_blue-18px`. No numbered suffixes as versioning.
- Never leave an element unnamed/auto-style ("div soup") — every structural element carries a dialect class.
- Combo variations use `is-*` (`is-secondary`, `is-reversed`) stacked on a base class; max base + one or two combos.

## 2. Structure skeleton

Every section version follows this chain (the version file starts at the section wrapper — no `page-wrapper`/`main-wrapper` needed in a reference file, note it in the Webflow-notes comment instead):

```html
<section class="section-home_hero">
  <div class="padding-section-large">
    <div class="padding-global">
      <div class="container-large">
        <!-- content -->
      </div>
    </div>
  </div>
</section>
```

- Containers: `container-large` (80rem) · `container-medium` (64rem) · `container-small` (48rem).
- Section padding: `padding-section-small` / `-medium` / `-large`.
- Repeating items: `[id]_list_wrap > [id]_list > [id]_item` — the grid lives on `_list`. Cards inside items: `_item > _card > _card_content`. This maps 1:1 to Webflow CMS Collection List wrappers.
- Images always wrapped: `[id]_image-wrap > img`.
- **Button-group law:** every CTA sits inside a `button-group` div, even a lone button. Buttons are `button` + optional `is-secondary` etc.
- Typography utilities when visual size ≠ semantic level: `heading-style-h1…h6`, `text-size-small/regular/medium/large`, `text-weight-*`.

## 3. Token collections → CSS custom properties

`_tokens.css` mirrors the six Webflow variable collections. Property naming: `--[collection]--[token]` with the collection abbreviated as below. Bind **semantic (Theme) tokens to elements — never Base primitives.**

```css
:root {
  /* ── Base Colour (primitives — referenced only by Theme tokens) ── */
  --base--brand-100: …;   /* through --base--brand-900 */
  --base--neutral-100: …; /* through --base--neutral-900 */
  --base--success: …; --base--warning: …; --base--error: …;

  /* ── Theme (semantic — the only color tokens elements use) ── */
  --theme--background-primary: var(--base--…);
  --theme--background-secondary: …;
  --theme--background-alternate: …;
  --theme--text-primary: …;
  --theme--text-secondary: …;
  --theme--text-alternate: …;
  --theme--text-on-accent: …;
  --theme--border-primary: …;
  --theme--border-secondary: …;
  --theme--link-text: …; --theme--link-text-hover: …;
  --theme--button-primary-background: …;
  --theme--button-primary-text: …;
  --theme--button-primary-border: …;
  --theme--button-primary-background-hover: …;
  --theme--button-primary-text-hover: …;
  /* matching --theme--button-secondary-* set */

  /* ── Spacing ── */
  --spacing--spacer-tiny: 0.125rem;
  --spacing--spacer-xxsmall: 0.25rem;
  --spacing--spacer-xsmall: 0.5rem;
  --spacing--spacer-small: 1rem;
  --spacing--spacer-medium: 2rem;
  --spacing--spacer-large: 3rem;
  --spacing--spacer-xlarge: 4rem;
  --spacing--spacer-xxlarge: 5rem;
  --spacing--padding-global: 2.5rem;      /* per project */
  --spacing--padding-section-small: 3rem; /* per project */
  --spacing--padding-section-medium: 5rem;
  --spacing--padding-section-large: 7rem;

  /* ── Font Family ── */
  --font--heading: …;
  --font--body: …;
  /* add --font--subheading / --font--mono only if the brand uses them */

  /* ── Typography ── */
  --type--heading-h1: …; /* through --type--heading-h6 */
  --type--text-small: …; --type--text-regular: …;
  --type--text-medium: …; --type--text-large: …;
  --type--weight-regular: 400; --type--weight-medium: 500;
  --type--weight-semibold: 600; --type--weight-bold: 700;
  --type--leading-tight: 1.1; --type--leading-normal: 1.5;
  --type--leading-relaxed: 1.7;

  /* ── Layout ── */
  --layout--container-large: 80rem;
  --layout--container-medium: 64rem;
  --layout--container-small: 48rem;
  --layout--radius-small: …; --layout--radius-medium: …;
  --layout--radius-large: …; --layout--radius-round: 100vw;
  --layout--gap-small: …; --layout--gap-medium: …; --layout--gap-large: …;
  --layout--max-width-text: 42rem;
  --layout--navbar-height: …;
}
```

Fill values from the branding source. If the brand guidelines don't specify something (e.g. radii), choose values consistent with the brand personality and mark them `/* proposed */` — proposed tokens are suggestions to the user, not decisions.

Responsive: stepped rem values per breakpoint (not clamp). In a reference file, express breakpoint shifts as plain media queries overriding the custom properties (desktop-base, then `@media (max-width: 991px)`, `767px`, `479px`) — this mirrors Webflow Variable Modes and converts directly.

## 4. Hover / state pattern

Hover is a CSS state consuming a `-hover` token — never a swapped class or a JS style write:

```css
.button {
  background: var(--theme--button-primary-background);
  color: var(--theme--button-primary-text);
}
.button:hover {
  background: var(--theme--button-primary-background-hover);
  color: var(--theme--button-primary-text-hover);
}
```

## 5. Quality floor (applies to every version)

- Sizing in rem (1rem = 16px). Exceptions: `1px` borders, `0.125rem` micro-spacing, `0.875rem` small type.
- Desktop-base, responsive down through 991 / 767 / 479px. Tap targets ≥ 44×44px on touch breakpoints.
- WCAG AA contrast on the token pairings actually used (4.5:1 body, 3:1 large text/UI).
- Visible `:focus-visible` on all interactive elements; real `<button>`/`<a>`; `aria-label` on icon-only controls; decorative icons `aria-hidden="true"`.
- Any animation wrapped in `@media (prefers-reduced-motion: no-preference)` (CSS) or a matching JS guard.
- Fonts in the reference files: load from Google Fonts (or system fallback) with `font-display: swap`; note the real licensed font in the header comment if it differs.
