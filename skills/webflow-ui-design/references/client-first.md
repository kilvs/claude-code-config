# Client-First Reference (v2.1)

Finsweet's Client-First is the naming and structure system for Webflow used in this skill. Goal: any human — another dev, the client — can read the class names and understand the build. This file holds the rules the skill applies. Source: finsweet.com/client-first/docs.

## Table of contents
- [Core structure](#core-structure)
- [Class naming strategy](#class-naming-strategy)
- [Global vs. custom (combo) classes](#global-vs-custom-classes)
- [Utility classes](#utility-classes)
- [Spacing system](#spacing-system)
- [Variables (design tokens)](#variables-design-tokens)
- [Folders](#folders)
- [Semantic HTML](#semantic-html)
- [Quick do/don't](#quick-dodont)

## Core structure

Every section follows this nesting. Memorize it — mockups and build notes mirror it exactly:

```
[prefix]_[element]_section      ← section wrapper. prefix = page name (static) or template_[collection] (CMS)
  └ padding-section-[large|medium|small]   ← top/bottom section padding
      └ padding-global          ← left/right page padding (consistent site-wide)
          └ container-large     ← max-width container, centers content
              └ [prefix]_[element]_content   ← wrapper holding the actual content
                  └ [content]   ← headings, paragraphs, buttons, etc.
```

`prefix` is the page name on static pages (`home_legacy_section`), `template_[collection]` on CMS template pages (`template_blog_section`), or `component_` for reusable blocks (`component_product_card`). See [Identifier naming](#identifier-naming-page-template-and-component-prefixes).

### Identifier naming: page, template, and component prefixes

Identifier classes are scoped by where they live, then the element/block, then the type of thing. There are three prefixes depending on what the block is:

- **Static pages** → `[page]_[element]_[tag]`, prefixed with the page name. `home_legacy_section`, `home_banner_section`, `about_team_section`.
- **CMS template pages** (the Collection page template) → `template_[collection]_[tag]`, prefixed with `template_` plus the collection/template name. `template_blog_section`, `template_blog_content`, `template_property_image_wrap`. The literal word `template` flags that the page is a CMS-driven detail page rather than a one-off static page.
- **Reusable components** → `component_[element]_[specific-element]`, prefixed with `component_`. For blocks that aren't tied to one page and get reused across the site — `component_product_card`, `component_testimonial_card`, `component_team_member`, `component_pricing_tier`. The `component_` prefix flags "this is portable, it can live anywhere."

**When to use `component_` vs a page/template prefix:** if the block belongs to one specific page or template section, use the page/template prefix (`home_legacy_item`). If it's a self-contained, reusable unit you'd drop into multiple places, use `component_` (`component_product_card`). A reusable component can sit *inside* a page-specific or template item — they nest. Example: a `home_products_item` (or `template_shop_item`) wraps a `component_product_card`, so the page owns the grid/layout and the component owns the card's internal structure:

```
home_products_list_wrap
  └ home_products_list           ← page owns the grid
      └ home_products_item        ← page owns the cell
          └ component_product_card        ← reusable component starts here
              └ component_product_image_wrap
              └ component_product_content
                  └ h3.heading-style-h5
                  └ p.text-size-small
                  └ button-group
```

This keeps the component's internals identical everywhere it's used (style it once, reuse), while each page controls only how the components are laid out. The same `component_product_card` can sit inside `home_products_item`, `template_shop_item`, or anywhere else without change.

Everything else about the convention is identical across all three — `_content`, `_card`, `_list_wrap > _list > _item`, `_image_wrap`, `button-group`, `heading-style-h*` all work the same way; only the prefix changes (`home_…` / `template_blog_…` / `component_…`).

- **Section wrapper:** `[prefix]_[element]_section` → `home_legacy_section` (static) / `template_blog_section` (template).
- **Content wrapper:** the block inside the section padding holding headings, paragraphs, and buttons is `[prefix]_[element]_content` → `home_legacy_content` / `template_blog_content` / `component_product_content`. If a section has multiple distinct content blocks (e.g. a split layout), they can each be `_content` or be distinguished further.

The prefix keeps classes unique across a multi-page site and reads top-down (where it lives → what it is → what kind). For genuinely site-wide structural components like the nav and footer, the established `navbar_component` / `footer_component` names are fine too; `component_` is the prefix for the reusable content blocks you build.

### Structural utilities (unchanged)

- `padding-global` controls the horizontal gutter for the whole site. Change it once, it updates everywhere.
- `container-large` (also `container-medium`, `container-small`) sets max width and centers.
- `padding-section-large/medium/small` controls vertical rhythm between sections.

Container max-widths (typical): large ≈ 80rem (1280px), medium ≈ 64rem, small ≈ 48rem. Adjust per project, but keep them as named container classes, not one-off widths.

### Grid / list / collection pattern

For repeating items (especially grids and CMS Collection Lists), nest three layers:

```
[page]_[element]_list_wrap      ← outer wrapper (sets the section's list area)
  └ [page]_[element]_list       ← the grid/flex parent (maps to Collection List)
      └ [page]_[element]_item    ← a single item (maps to Collection Item)
          └ [page]_[element]_card        ← optional card shell, when the design has one
              └ [page]_[element]_content  ← content block (headings, text, buttons, image)
                  └ [page]_[element]_image_wrap   ← optional image slot
                  └ h2.heading-style-h4 / p / button-group / ...
```

- `..._list_wrap` → `..._list` → `..._item` is the standard chain. Example: `home_legacy_list_wrap` / `home_legacy_list` / `home_legacy_item`.
- **Nesting order inside an item:** `_card` (when present) wraps `_content`; `_content` holds the actual stuff — headings, paragraphs, buttons, and (often) the `_image_wrap`. So the usual chain is `_item > _card > _content > [_image_wrap + text + button-group]`. This is the common case, not a hard rule — split layouts separate the image from the content (see Image wrapper below), and simple items skip layers.
- Both `_card` and `_content` are situational. Add `_card` only when the item has a visible card shell. `_content` appears wherever there's a grouped block of content (inside a card, inside an item, or directly inside the section padding for non-list sections). A bare item with no card and a single paragraph can put that `_content` directly under `_item`.
- The `_list` element is the one that gets `display: grid` (or flex). The `_wrap` exists so you can pad/constrain the grid area without touching the grid itself.

### Image wrapper

Wrap images in an image wrap so the aspect ratio and overflow are controlled by the wrapper, not the raw `img`. Where the image wrap sits is case-by-case:

- **Image as part of a content block** (image stacked above/below text): the `_image_wrap` lives inside `_content` alongside the headings and text.
```
[page]_[element]_content        ← content block
  └ [page]_[element]_image_wrap  ← controls ratio/overflow (e.g. home_legacy_image_wrap)
  │   └ img                       ← the image, typically width/height 100%, object-fit cover
  └ h2.heading-style-h4 / p / button-group
```
- **Split layout** (image on one side, text on the other — e.g. a flex row with `justify-content: space-between`, often wrapping to a column on mobile): the `_image_wrap` and `_content` are **siblings** under the item/section, not nested. The flex parent splits them.
```
[page]_[element]_item (or _content_wrap)   ← flex parent, space-between
  └ [page]_[element]_image_wrap   ← one side
  │   └ img
  └ [page]_[element]_content      ← other side: headings, text, button-group
```

Either way the image wrap gives a clean slot to set aspect ratio, rounding, and overflow on the wrapper. Pick the structure that matches the layout, don't force the image inside `_content` when the design splits them.

## Class naming strategy

Format: lowercase, hyphen-separated words; underscore reserved for identifier/structural separation.

- **Identifier classes** describe a unique block, scoped by page: `home_legacy_section`, `home_legacy_content`, `home_legacy_list`, `home_legacy_item`. Use the `[page]_[element]_[tag]` pattern with underscores separating each part. See the full convention in [Core structure](#core-structure).
- **Utility classes** are reusable, single-purpose, hyphenated: `text-size-large`, `margin-bottom`, `background-color-primary`, `button-group`, `heading-style-h2`.
- Be descriptive and human-readable. **Never** use cryptic shorthand like `flex-a-l-j-c`, `col-2-d`, `pd-t-24`. If a teammate can't read it, it's wrong.

Naming wrapper/list pattern for a repeating block (page-scoped):
```
[page]_[element]_list_wrap   ← outer wrapper of the list area
[page]_[element]_list        ← collection/grid parent (maps to Collection List)
[page]_[element]_item        ← a single item (maps to Collection Item)
[page]_[element]_content     ← content block inside the item/section
[page]_[element]_image_wrap  ← image slot controlling ratio/overflow
```

## Global vs. custom classes

- A **global class** does one job everywhere (`text-color-primary`, `margin-bottom`, `container-large`). Define once, reuse.
- **Combo/custom classes** layer a variation on a base. Acceptable, but stacking many combos (`.button.is-secondary.is-large.is-icon`) gets hard to maintain — prefer a clear single class when a variation is used often.
- Variation suffix convention: `is-[variant]` (e.g. `button` + `is-secondary`). Keep the base class carrying the shared styles; the `is-` combo carries only the difference.

### Theme variants: `data-variant`

For light/dark (or other colour) variants of the same component, use a `data-variant` attribute instead of stacking combo classes. The component keeps one class (`component_product_card`) and the attribute swaps the colour scheme:

```html
<div class="component_product_card" data-variant="light">…</div>
<div class="component_product_card" data-variant="dark">…</div>
```

```css
[data-variant="light"] { --card-bg: var(--background-primary);   --card-text: var(--text-primary); }
[data-variant="dark"]  { --card-bg: var(--background-secondary); --card-text: var(--text-alternate); }
```

Why `data-variant` over an `is-dark` combo:
- **One source of truth.** The component's structure and base styles stay in a single class; only the colour tokens flip. No parallel `.component_product_card.is-dark` rule set to keep in sync.
- **Editable in Webflow.** `data-variant="dark"` is a custom attribute the editor can change per-instance in the Designer, without touching classes.
- **Scoped theming.** Pair it with CSS variables so a `[data-variant="dark"]` wrapper re-tints everything inside it (text, borders, buttons) by reassigning the semantic tokens — the same primary/alternate token concept used site-wide (see Color variables). This is also how you do a dark section on an otherwise light page: put `data-variant="dark"` on the section or card wrapper.
- **Consistent with `data-*` motion.** Variants and animations both ride on data attributes, so the markup reads declaratively: what it is (class), how it looks (`data-variant`), how it moves (`data-scroll-animate`).

Keep variant values to a small, named set (`light`, `dark`, and any brand-specific ones like `brand`, `inverse`) rather than ad-hoc colours — the point is a controlled theme switch, not arbitrary styling. `is-[variant]` combos are still fine for non-colour structural variations (`button` + `is-secondary`, a wider card via `is-large`); reserve `data-variant` for colour/theme.

## Utility classes

Reusable single-purpose classes. Common families:
- Heading style: `heading-style-h1 / h2 / h3 / h4 / h5 / h6` (see below)
- Text size: `text-size-tiny / small / regular / medium / large / huge`
- Text weight: `text-weight-light / normal / medium / semibold / bold`
- Text style: `text-style-allcaps`, `text-style-italic`, `text-align-center`
- Color: `text-color-primary`, `background-color-primary`, etc. (linked to semantic variables)
- Display/visibility: `hide`, `hide-mobile-landscape`, `hide-tablet`, etc.
- Max width: `max-width-small / medium / large`, `max-width-full`
- Button grouping: `button-group` (see below)

### Headings: `heading-style-h1`–`h6` + styled base tags

Two things carry heading styles, and they're kept in sync:

1. The bare element tags `h1`–`h6` are styled directly (a default look for each level).
2. A matching utility class `heading-style-h1` through `heading-style-h6` carries the same styles.

This lets you decouple visual size from semantic level: an `h2` that needs to look like an h4 gets `heading-style-h4`, and an element that isn't a heading tag can still take a heading look via the class. In the screenshot, the `4.9 Stars` heading is an `<h2 class="heading-style-h4">` — h2 for document structure, h4 for appearance. Apply this anytime visual hierarchy and semantic hierarchy diverge; otherwise the bare tag's default styling is enough.

### Buttons: wrap in `button-group`

Buttons live inside a `button-group` utility wrapper rather than sitting loose in the content. The group handles spacing/alignment between one or more buttons (and keeps a single button consistent with multi-button rows):
```
button-group
  └ a.button            ← primary
  └ a.button.is-secondary   ← optional secondary
```
Always wrap CTAs in `button-group`, even a lone button.

## Spacing system

Client-First favors a padding/spacer approach over scattered margins.

- **Section padding:** `padding-section-large/medium/small` for vertical space between sections.
- **Global padding:** `padding-global` for horizontal page gutters.
- **Spacer blocks** or `margin-bottom` utilities for rhythm between elements within a section. Prefer consistent named steps over arbitrary values.
- Spacing values come from the approved rem scale (see design-tokens.md). Don't free-type `padding: 37px`.

A note on combos and breakpoints: spacing often needs to shrink on smaller screens. Set the base (desktop) value, then **override downward** at tablet/mobile — consistent with Webflow's desktop-base cascade. (With Variable Modes, do this on the breakpoint modes instead of combo classes.)

## Variables (design tokens)

Webflow Variables support **five types**: Color, Size, Percentage, Number, and Font Family. They are real CSS custom properties. Make a variable for any value that is reused across the site *and* worth changing in one place — not for one-off or context-specific values, which stay hardcoded as rem in the class. (Older Client-First guidance said only color variables existed — that's out of date. Size, number, percentage, and font-family variables are all available now.) The collection structure (seven collections, slash-grouped names, decided 22 Sep 2026) is in design-tokens.md and, in full, in the `variables` Webflow skill inside `webflow-agent-instructions/template/webflow-skills/variables.md`.

Variables to set up, by type:

- **Color** (Color type) — Primitives ramps (`colour/navy/500`) and Theme tokens by role (`background/primary`, `text/primary`), with Light and Dark modes on Theme.
- **Heading sizes** (Size type) — one variable per heading level, `heading/display`, `heading/h1` … `heading/h6`. The power move: bind the same variable to **both** the bare element tag and the matching class. So `h1` (the tag) and `heading-style-h1` (the class) both reference `heading/h1`. Change the variable once and every h1 and every `heading-style-h1` updates together. This is exactly how Client-First/Flowkit keeps tag styles and class styles in sync.
- **Body / text sizes** (Size type) — `text/tiny` … `text/xlarge`, bound to the `text-size-*` utilities and the base `p`/body.
- **Font families** (Font Family type) — role-named: `font/heading`, `font/body`, `font/mono`. Update the font for the whole site from one variable. Add only the ones the project uses (often just `font/heading` + `font/body`). Custom, Google, and Adobe fonts on the site are all selectable.
- **Font weights, line heights, letter spacing** — `weight/regular` (400) … `weight/bold` (700); `line-height/heading` (1.1), `line-height/body` (1.5), `line-height/relaxed` (1.7); `letter-spacing/tight`, `normal`, `wide`. Plain words, no jargon like leading or tracking.
- **Spacing** (Size type) — the Primitives `spacer/` scale, 13 steps: `xxtiny` 0.125rem · `xtiny` 0.25 · `tiny` 0.5 · `xxsmall` 0.75 · `xsmall` 1 · `small` 1.5 · `medium` 2 · `large` 3 · `xlarge` 4 · `xxlarge` 5 · `huge` 6 · `xhuge` 8 · `xxhuge` 12. The Spacing collection (`padding-global`, `padding-section/*`, `gap/*`, `content/*`) aliases these; only the Spacing tokens get bound. Don't invent a parallel numbered scale.
- **Container widths** (Size type) — Layout `container/large` (80rem), `container/medium` (64), `container/small` (48), `container/semi-full` (120rem, the cap for `container-semi-full` past 1920px). `container-full` has no token. One variable per capped container class.
- **Button style** (mix) — `Components/button/padding-y`, `padding-x`, `radius`, `gap` (Size, aliasing spacers and radius) and `Theme/button/*` colours, so a button restyle is a token edit, not a per-instance change.
- **Animation** (Number and Size) — `duration/`, `stagger/`, `distance/`, `scale/`, `marquee/`, `parallax/` in an Animation collection that is the timing table native IX3 presets are authored to. Not bound in the style panel.

Use the **rem system for the values themselves** (see design-tokens.md) — variables hold the rem values; they don't replace the rem scale, they make it editable in one place.

### Modes — responsive (breakpoints) + theming

Variable **Modes** let one variable hold different values per context. Two uses:
- **Responsive (breakpoint module):** assign a mode to each Webflow breakpoint and a Size variable (e.g. `heading/h1`, `padding-section/large`, `container/large`) resolves to a different value per breakpoint — the type scale, spacing, and widths shrink on mobile with no per-class override. Typography, Spacing and Layout each carry four modes (Desktop base, 991, 767, 479); the desktop value is the base and the smaller modes override downward. For a one-off element that needs different responsive spacing than the global rule, the Client-First `is-` combo (`spacer-large is-home-tabs`) is still the approved override. Full detail in design-tokens.md (Modes section).
- **Theming:** a Color variable resolves to one value in light mode and another in dark/brand mode. Pair with the `data-variant="light|dark"` attribute — a `[data-variant="dark"]` wrapper switches the active token set for everything inside it.

### Color tokens — two tiers

**1. Primitive tokens** — raw palette, the base building blocks, in the Primitives collection as `colour/navy/500`, `colour/neutral/100`, `colour/green/500`, one folder per hue. Descriptive names for what the colour is. Never bound to an element.

**2. Semantic tokens** — describe *purpose*, not colour. This is what you actually apply. Naming: `[element]-[style]-[identifier]`:
```
background-color--background-primary
background-color--background-secondary
text-color--text-primary
text-color--text-alternate
border-color--border-primary
```
- **Never** name a semantic token after its colour (`background-white`). That breaks theming — a dark-mode swap would force renames. Name by role so the value can change without renaming.
- **Primary/alternate concept:** set your default theme as the reference. If `background-primary` is dark, `background-alternate` is its inverse (light). Same for text: `text-primary` light on dark, `text-alternate` dark on light.
- Semantic tokens can also be exposed as utility classes (`background-color-primary`, `text-color-primary`).
- If a client has an existing colour system/naming, conform to it.

The same primitive → semantic two-tier idea applies beyond colour: the `spacer/` and `number/` primitives are referenced by `padding-section/medium`, `weight/bold` and so on. The seven collections (Primitives, Theme, Typography, Spacing, Layout, Animation, Components) with slash groups inside keep the panel navigable.

## Folders

Client-First v2.1 supports folder organization (and the Finsweet Extension's virtual folders) to group related classes. Group by component/section so the class panel stays navigable. Folders are organizational only — they don't change how classes apply.

## Semantic HTML

Use correct tags: `header`, `nav`, `main`, `section`, `footer`, real heading hierarchy (one `h1` per page, no skipping levels for styling). Decouple visual size from semantic level using `text-size-*` utilities — a visually large subhead can still be an `h2`. This matters for accessibility and SEO.

## Quick do/don't

| Do | Don't |
|---|---|
| `home_legacy_section > padding-section-large > padding-global > container-large > home_legacy_content` | dump content straight into a section |
| `home_legacy_section` (static) · `template_blog_section` (CMS) · `component_product_card` (reusable) | same prefix on every page / generic `section_hero` |
| `home_legacy_list_wrap > home_legacy_list > home_legacy_item` | a single ad-hoc grid div |
| wrap images in `home_legacy_image_wrap` | raw `img` with inline ratio hacks |
| wrap CTAs in `button-group` | loose buttons in the content flow |
| `text-size-large`, `margin-bottom` | `font-size: 28px` typed inline |
| `home_team_item`, `home_team_name` | `div-block-7`, `card2` |
| `<h2 class="heading-style-h4">` when size ≠ level | `h3` chosen because it "looks right" |
| semantic tokens: `text-color--text-primary` | color-named tokens: `text-black` |
| tokens → Variables (color, size, number, font), rem for values | hardcoding repeated sizes/fonts that should be one variable |
| one `h1`, proper heading order | skipping levels for visual size |
| `is-secondary` combo on a `button` base | five stacked combo classes |
| `data-variant="dark"` for a colour/theme swap | a parallel `.card.is-dark` rule set to keep in sync |
