# Design Tokens Reference

The numeric foundation for Webflow-ready design. All sizing is rem-based (1rem = 16px). These scales keep output consistent and let a developer rebuild it in Webflow without guessing values.

## Variable structure (how tokens map to Webflow Variables)

Decided by the user on 22 Sep 2026 and applied on every build unless the project says otherwise. The full map, values and MCP build order live in the `variables` Webflow skill (`webflow-agent-instructions/template/webflow-skills/variables.md`); this section is the short version.

**Seven collections.** Names are slash-grouped (`heading/h1`), which the Variables panel shows as folders.

| Collection | Holds | Modes | Bound? |
|---|---|---|---|
| Primitives | `colour/<hue>/<step>` ramps (descriptive hue folders), `spacer/` scale, `number/` weights and line heights | none | never |
| Theme | `background/`, `text/`, `border/`, `surface/`, `button/`, `status/`, `opacity/`; every value aliases a Primitive | Light, Dark | yes |
| Typography | `font/`, `heading/display,h1…h6`, `text/tiny…xlarge`, `weight/`, `line-height/`, `letter-spacing/` | Desktop, 991, 767, 479 | yes |
| Spacing | `padding-global`, `padding-section/`, `gap/`, `content/` rhythm gaps; every value aliases a spacer | Desktop, 991, 767, 479 | yes |
| Layout | `container/`, `max-width/`, `radius/`, `border-width/`, `icon/`, `navbar/`, `z/` | Desktop, 991, 767, 479 | yes |
| Animation | `duration/`, `stagger/`, `distance/`, `scale/`, `marquee/`, `parallax/` | none | read by the GSAP script |
| Components | `button/` at setup; other groups only when a component needs its own knob | none | yes |

**Variables for reused values only — not variable-everything.** A value earns a variable when it's reused across the site *and* worth changing in one place. Do **not** make variables for one-off values or context-specific spacing (the bottom margin on one heading); hardcode those as rem in the class. A variable referenced once is just indirection.

**Which Webflow type** (five available — Color, Size, Percentage, Number, Font Family):
- Colours → **Color**. Sizes/spacing/widths/font-sizes/distances → **Size**. Font families → **Font Family**. Font weights, unitless line heights, durations in seconds, scale factors → **Number**. Opacity → **Percentage**. A value can also be an alias to another variable or a raw CSS expression (`clamp()`, `color-mix()`); log any expression per token.

**Spacing — the spacer scale, 13 steps, in Primitives.** Named by size, never numbered:

| Variable | rem | px | Variable | rem | px |
|---|---|---|---|---|---|
| `spacer/xxtiny` | 0.125 | 2 | `spacer/large` | 3 | 48 |
| `spacer/xtiny` | 0.25 | 4 | `spacer/xlarge` | 4 | 64 |
| `spacer/tiny` | 0.5 | 8 | `spacer/xxlarge` | 5 | 80 |
| `spacer/xxsmall` | 0.75 | 12 | `spacer/huge` | 6 | 96 |
| `spacer/xsmall` | 1 | 16 | `spacer/xhuge` | 8 | 128 |
| `spacer/small` | 1.5 | 24 | `spacer/xxhuge` | 12 | 192 |
| `spacer/medium` | 2 | 32 | | | |

Spacing tokens alias the spacers: `padding-section/small` → `spacer/large` (3rem), `padding-section/medium` → `spacer/xxlarge` (5rem), `padding-section/large` 7rem static (Client-First values, since the designer works from Relume templates), `gap/medium` → `spacer/medium`. The `spacer-*`, `margin-*` and `padding-*` utility classes bind the spacer primitives directly, because the utility is the scale. Don't invent a parallel numbered `space-N` scale.

**Font families — role-named** (Font Family type): `font/heading`, `font/body`, `font/mono` only when the site shows code or figures.

**Backgrounds — by role, never by tone:** `background/primary`, `secondary`, `tertiary`, `brand`, `inverse`. Role names survive the Dark mode flip; `background-light` would be a lie in dark mode.

**Binding tags + classes to one variable.** Bind each `heading/*` size to **both** the bare tag and the matching class (`h1` and `heading-style-h1` both reference `heading/h1`); same for body (`p` and `text-size-regular` → `text/regular`). One edit updates both, tags and classes never drift.

### Modes — the responsive (breakpoint) module + theming

A variable normally holds one value. With **Modes**, it holds several and Webflow picks the active one by context.

**1. Breakpoint modes.** Typography, Spacing and Layout each carry four modes: Desktop (base), Tablet 991, Mobile landscape 767, Mobile portrait 479. Webflow lets only one collection bind a breakpoint automatically, so Typography holds the automatic modes and Spacing and Layout hold manual modes of the same names, applied on the Body tag at each breakpoint in the Style panel (once per site). `heading/h1` → 3.5rem on desktop, 2.25rem on mobile portrait, no combo class, no per-element override. Set the desktop value as the base and override **downward**. Nothing above desktop unless the project adds a 1280 or 1920 mode. Primitives, Theme, Animation and Components carry no breakpoint modes.

- **Instance exception:** when one element needs different responsive spacing than the global rule, the Client-First `is-` combo (`spacer-large is-home-tabs`) is still the approved override. Breakpoint **modes** for the global scale, `is-` combo for one-offs.
- A token may hold a `clamp()` expression where a stepped value looks wrong (often the display heading). Log it per token.

**2. Theme modes.** Theme carries Light and Dark on every site from day one; dark values can be filled later. A `[data-variant="dark"]` wrapper activates the dark token set for everything inside it, so a dark section is a token flip, never a second class set. Hover is a CSS state, not a mode: `button/primary-background-hover` binds inside the class's Hover state.

**3. Animation.** Webflow has no time or easing type, so the Animation collection holds Numbers (seconds, stagger, scale) and Sizes (distances) as the timing table every native IX3 preset is authored to. Neither the Interactions panel nor the transition panel can bind a variable to a duration, so a token change means re-authoring the presets that use it. Ease is recorded as the IX3 index (power2.out = 5).

Naming: lowercase, slash groups, hyphens inside a segment, role-named at the semantic tier, ordered small→large within a group. Plain words (`line-height`, `letter-spacing`), never jargon (`leading`, `tracking`).

## Approved rem scale

Client-First approved rem values (with px at 16px base). Use these; avoid long decimals like 8.4375rem.

| rem | px | rem | px |
|---|---|---|---|
| 0.125 | 2 | 3 | 48 |
| 0.25 | 4 | 3.5 | 56 |
| 0.5 | 8 | 4 | 64 |
| 0.75 | 12 | 5 | 80 |
| 0.875 | 14* | 6 | 96 |
| 1 | 16 | 7 | 112 |
| 1.25 | 20 | 8 | 128 |
| 1.5 | 24 | 10 | 160 |
| 2 | 32 | 12 | 192 |
| 2.5 | 40 | 16 | 256 |

**Three exceptions** to the scale:
1. **14px (0.875rem)** is allowed and common for small body/caption text when 16px is too large. 12px is usually too small for body type.
2. **2px (0.125rem)** for tiny spacing — the floor for anything under 4px.
3. **1px stays 1px** — never convert to rem (used for borders; avoids retina scaling issues).

Webflow tip to relay in build notes: you can type `100/16rem` directly in a Designer input and it computes the rem value.

## Type scale

Relume's scale, because the designer works from Relume templates in Figma; a display step sits above it. Each step is a Typography token bound to both the tag and its class. The desktop value is the base; the smaller values sit on the breakpoint modes.

| Token | Class | Desktop | Tablet 991 | Mobile L 767 | Mobile P 479 | Typical use |
|---|---|---|---|---|---|---|
| `heading/display` | `heading-style-display` | 4.5rem (72) | 4 | 3.5 | 3 (48) | Hero headline |
| `heading/h1` | `heading-style-h1` | 3.5rem (56) | 3 | 2.75 | 2.5 (40) | Page title |
| `heading/h2` | `heading-style-h2` | 3rem (48) | 2.75 | 2.5 | 2.25 (36) | Section title |
| `heading/h3` | `heading-style-h3` | 2.5rem (40) | 2.25 | 2 | 2 (32) | Subsection |
| `heading/h4` | `heading-style-h4` | 2rem (32) | 1.75 | 1.5 | 1.5 (24) | Card title |
| `heading/h5` | `heading-style-h5` | 1.5rem (24) | 1.5 | 1.25 | 1.25 (20) | Small heading |
| `heading/h6` | `heading-style-h6` | 1.25rem (20) | 1.25 | 1.125 | 1.125 (18) | Label heading |
| `text/xlarge` | `text-size-xlarge` | 1.5rem (24) | same | same | same | Lead paragraph |
| `text/large` | `text-size-large` | 1.25rem (20) | same | same | same | Intro copy |
| `text/medium` | `text-size-medium` | 1.125rem (18) | same | same | same | Emphasised body |
| `text/regular` | `text-size-regular` | 1rem (16) | same | same | same | Default body |
| `text/small` | `text-size-small` | 0.875rem (14) | same | same | same | Caption, label |
| `text/tiny` | `text-size-tiny` | 0.75rem (12) | same | same | same | Legal, fine print |

- Headings shrink from desktop **down** through the modes; body text stays constant.
- **Line height:** `line-height/heading` 1.1 for display and h1–h2, `tight` 1.2 for h3–h6, `body` 1.5, `relaxed` 1.7 for long reads.
- **Measure (line length):** cap body text around 60–75 characters with `max-width-text` (42rem), never full-bleed paragraphs.
- **Weights:** `text-weight-*` bound to `weight/*`. Limit to 2–3 weights for coherence.
- **Pairing:** one heading family + one body family is plenty. If using a single family, vary weight and size for hierarchy.

## Spacing scale

Reuse the rem scale as named steps. Mental model:

| Step | rem (px) | Use |
|---|---|---|
| xs | 0.5 (8) | Tight gaps, icon-to-label |
| sm | 1 (16) | Between related elements |
| md | 1.5 (24) | Within a component |
| lg | 2.5 (40) | Between components |
| xl | 4 (64) | Mobile section padding |
| 2xl | 6 (96) | Desktop section padding |
| 3xl | 8 (128) | Generous desktop sections |

- **Section padding (vertical):** map to `padding-section-small/medium/large`. Typical: desktop 6–8rem (96–128px), reduced to ~4rem (64px) on mobile. Set the desktop value as base and override down at the smaller breakpoints.
- **Global padding (horizontal gutter):** `padding-global`. Typical: mobile 1.25rem (20px) → desktop 2.5rem (40px).
- Keep spacing on the scale. Consistency reads as intentional; arbitrary values read as sloppy.

## Color tokens

Structure colors as primitive → semantic (full naming rules in client-first.md).

**Primitive palette to define per project:**
- Brand: a primary brand hue with ~3–5 shades (e.g. 300/500/700) for hover/active states.
- Neutral: a gray ramp from near-white to near-black (~6–8 steps) for text, backgrounds, borders. **This ramp carries most of the design** — see below.
- System: success (green), warning (amber), error (red) — only if the project needs status states.

**Neutrals do most of the work.** A polished interface is mostly neutral surfaces with the brand accent used sparingly. Don't build a page out of saturated colour — build it out of neutrals and let one accent pop. A practical neutral ramp:

| Role | Light theme | Notes |
|---|---|---|
| Page background | white `#FFFFFF` or dirty white `#FAFAF8` | barely-warm off-white reads softer than pure white |
| Alternating section band | light grey `#F2F2F0` | separates sections without hard borders |
| Card / raised surface | white on a grey page, or a hair darker on white | subtle elevation |
| Border / divider | light grey `#E5E5E2`, thin | quiet separation |
| Body text | near-black / dark grey `#1A1A1A`–`#2C2C2A` | avoid pure `#000` — it's harsh |
| Secondary text | muted grey `#6B6B68` | captions, labels, meta |
| Hint / disabled | light grey `#A0A09C` | de-emphasized |

For a **dark theme**, the same logic inverts: a deep neutral (or a deepened, desaturated brand colour) is the foundation, a tinted off-white is body text, and mid-greys are secondary text. Either way: mostly neutral, accent sparingly.

**Semantic tokens to map (minimum viable set):**
```
background-color--background-primary
background-color--background-secondary
background-color--background-alternate
text-color--text-primary
text-color--text-secondary
text-color--text-alternate
border-color--border-primary
```

**Contrast:** body text vs. background must meet WCAG AA (4.5:1 for normal text, 3:1 for large text ≥24px or bold ≥18.66px). Check before finalizing — a beautiful palette that fails contrast fails the brief.

## Breakpoints (Webflow's actual model)

Webflow has **7 breakpoints with Desktop as the base**, not mobile. Styles cascade **bidirectionally** from desktop: down to the smaller breakpoints (max-width queries) and up to the three larger ones (min-width queries). The site opens on the desktop breakpoint in the Designer.

**Policy:** a new site has desktop base plus 991 / 767 / 479 only. No 1280, 1440 or 1920 at setup; add 1280 only when a design needs it, because a larger breakpoint cannot be removed. Past 1440 the page is **contained**: centred container, full-bleed section grounds and hero media, no type scaling. Two extra container widths handle wide media: `container-semi-full` (edge to edge up to 1920px, capped at `container/semi-full` 120rem beyond) and `container-full` (never capped). Card grids collapse 4 or 3 → 2 → 2 → 1; the nav goes to the hamburger from 991 down and must fit at 992.

| Breakpoint | Applies to | Direction | Query |
|---|---|---|---|
| 1920px | screens ≥1920px | cascades **up** | min-width |
| 1440px | screens ≥1440px | cascades up | min-width |
| 1280px | screens ≥1280px | cascades up | min-width |
| **Desktop (base)** | all devices unless overridden | base | — |
| Tablet | screens ≤991px | cascades **down** | max-width |
| Mobile landscape | screens ≤767px | cascades down | max-width |
| Mobile portrait | screens ≤479px | cascades down | max-width |

- The three larger breakpoints (1280/1440/1920) are **opt-in** — add them only when the project needs ultrawide handling. Once added, a larger breakpoint can't be removed.
- A style set on a breakpoint overrides what it inherits and **stops inheriting further changes** from the breakpoints above it (for smaller) or below it (for larger).
- Only Style-panel changes cascade. Element order, content, and settings apply to all breakpoints at once.

### "Mobile-first" here means mobile-responsive-oriented

This skill *designs* at the **desktop base** (Webflow's native authoring direction — set the full layout there), then works **down** through tablet → mobile landscape → mobile portrait, treating every smaller breakpoint as a first-class concern and verifying the design holds all the way to 479px. It is not mobile-up authoring with min-width queries — that fights Webflow's desktop-down cascade. The priority is that the result is genuinely responsive and looks right on phones, not the authoring order.

Practical implications:
- Set base/desktop values, then **override downward** at tablet/mobile. Don't build the mobile layout first and scale up.
- Reductions on mobile (smaller type, tighter section padding, single-column stacks) are overrides on the smaller breakpoints.
- With Variable **Modes**, Typography, Spacing and Layout resolve smaller as you go down (desktop `heading/h1` 3.5rem → mobile portrait 2.25rem) — the modern alternative to per-breakpoint combo overrides. Default the variable to the desktop value and override on the smaller-breakpoint modes.

In mockup CSS (which is just for preview, not the Webflow build), it's fine to express this with `max-width` queries to mirror Webflow's cascade:
```css
:root { font-size: 16px; }
/* desktop base styles (no query) */
@media (max-width: 991px)  { /* tablet */ }
@media (max-width: 767px)  { /* mobile landscape */ }
@media (max-width: 479px)  { /* mobile portrait */ }
```
When writing build notes, state the desktop values as the base and describe what changes going **down**.

## Desktop reference width and ultrawide

- **Design the desktop composition against a 1440px reference width** — the standard canvas width designers and clients expect. Lay out the full grid at 1440 before worrying about extremes.
- **Always check ultrawide behaviour.** Many clients (especially Australian clients, who commonly use ultrawide monitors) view sites at 2560px–3440px+. Content must not stretch edge-to-edge: cap it with a `container-large` max-width (≈80rem/1280px), center it, and let the page background fill the side margins. Line length and layout stay constant; only the margins grow. A design that looks right at 1440 but sprawls at 3440 has failed the brief.
- When presenting, show the standard (1440-logic) view and an ultrawide preview that makes the containment visible (e.g. mark where the container caps and the background fills). If rendering in a fixed-width canvas, scale to fit and state that the point is layout logic, not literal pixels.
