---
name: variables
description: The site's variable (design token) system. Seven collections, slash-grouped names, breakpoint modes on Typography, Spacing and Layout, Light and Dark modes on Theme, and an Animation collection the IX3 presets are authored to. Reference this skill before touching the Variables panel, binding a value in the style panel, proposing a new token, or reading a token from custom code.
---

# Variables

Every value that repeats lives in a variable. The style panel holds bindings, not raw values. This skill is the token map; the `client-first-builder` skill says where to bind them.

## 1. The seven collections

| # | Collection | Types | Modes | Bound to elements? |
|---|---|---|---|---|
| 1 | **Primitives** | Color, Size, Number | Tablet, Mobile landscape, Mobile portrait as **manual** modes, applied on the Body tag per breakpoint, for the large spacer steps only | **Never.** Source values only. |
| 2 | **Theme** | Color, Percentage | Light, Dark | Yes |
| 3 | **Typography** | Size, Number, Font Family | Desktop, Tablet 991, Mobile landscape 767, Mobile portrait 479 (**automatic**, bound to the breakpoints) | Yes |
| 4 | **Spacing** | Size | the same four, as **manual** modes applied on the Body tag per breakpoint | Yes |
| 5 | **Layout** | Size, Number | the same four, as manual modes applied on the Body tag per breakpoint | Yes |
| 6 | **Animation** | Number, Size | none | No. The timing table every IX3 preset is authored to. |
| 7 | **Components** | any | none | Yes. Starts with `button/` only. |

Laws:
- Bind semantic tokens (Theme, Typography, Spacing, Layout, Components). A Primitive bound to an element will not follow a theme or a rebrand.
- Every semantic value that has a matching primitive is an **alias** to it, never a retyped number.
- Names use **slash groups**: `heading/h1`, `button/primary-background`, and in Primitives a second level per hue, `colour/blue/500`. The panel shows each slash as a folder. Lowercase, hyphens inside a segment, ordered small to large.
- **A breakpoint binds to one collection only** (Webflow rule, confirmed 22 Sep 2026 in both the API and the Designer's New mode dialog with the same "[Conflict] ... style block store" message). Typography owns the automatic breakpoint modes. Primitives, Spacing and Layout carry **manual** modes with the same names, created without a breakpoint, and are made responsive by applying them on the **Body tag** in the Style panel at each breakpoint: Tablet mode on the Tablet breakpoint, Mobile landscape on 767, Mobile portrait on 479, nothing on Desktop. Set once per site; every page inherits. Verified live on 22 Sep 2026: padding-global 2.5 / 2.5 / 1.5 / 1.25rem, h1 3.5 / 3 / 2.75 / 2.5rem, navbar 5 / 5 / 5 / 4rem at 1196 / 896 / 696 / 416 wide. Through the API this is `data_style_tool` > `set_style_variable_mode` on `style_name: "body"` (the body tag) with `breakpoint_id` `medium` / `small` / `tiny` and the collection's mode id, so no Designer clicks are needed; `get_style_variable_modes` reads it back.
- **If the body tag refuses the manual modes** ("[Conflict] The operation could not be applied to the style block store", every try), apply them on the `page-wrapper` class instead, which wraps every page in Client-First, and log the deviation. Seen on two sites, 25 Sep 2026 (one a Client-First v2 cloneable starter), where Typography's automatic modes already sat on body at those breakpoints; the same call worked on the body tag of Client First MK-1.
- **A box-shadow cannot hold a variable.** `update_style` with `box-shadow: 0 0 0 4px var(--_theme---…)` is stored as a bare colour reference (an invalid shadow). Write shadows with literal rgba; a mode-dependent glow needs one rule in the Global Styles embed.
- **`update_style` collapses any `var()` into a plain binding.** A value such as `calc(var(--_layout---navbar--height) + 1rem)` is stored as a binding to that variable and the `calc` is dropped. Write such values as literals, or give the whole expression its own token (`custom_value`) and bind that. Renaming a variable changes its compiled name, so check for raw `var()` strings (for example from the WHTML builder) before renaming.
- Base-mode updates: leave `mode_id` out. `mode_id: "base"` returns an internal error. A mode added later starts empty and falls back to the base value until set.
- The `element_snapshot_tool` needs the Designer open in a browser; headless it returns `{status:false}`.
- Keep create batches near 20 actions: a 54-action batch timed out with 42 applied (re-read the collection before resending). A Color `custom_value` of `rgba(...)` was silently skipped; send `rgba(...)` as `static_value`.
- Breakpoint modes carry the desktop value as the base and override **downward**. Nothing above desktop base: sites start with no 1280, 1440 or 1920 breakpoint (22 Sep 2026). Add 1280 only when a design needs it, with the site owner's word, and give the three responsive collections a matching mode.
- Hover is a CSS **state**, not a mode. Bind `button/primary-background` on the default state and `button/primary-background-hover` inside the class's Hover state.
- A token may hold a raw CSS expression (`clamp()`, `calc()`, `color-mix()`) when a stepped value looks wrong. Log it per token in the site's decision log.

## 2. Primitives (never bound)

Ramp names are **descriptive per site**: what the colour is, never its role. `navy`, `sand`, `coral`; not `primary`. Hue folders keep the colour list navigable; `spacer/` and `number/` stay one level.

**The palette is anchored on the design file, then filled to full ramps**:
- Take the exact swatches from the Figma variables or brand guide and slot each into a step number by lightness (light 50–300, mid 400–500, dark 600–900). The swatches never move or change value.
- Fill every hue to the full ramp `50, 100, 200 … 900` (neutral also `0` white and `950`). Generate the missing steps in OKLCH from the swatch: same hue, lightness spaced between the swatches, chroma tapered at both ends and never above the lightest swatch on the light side. Neutrals stay pure grey unless the design tints them.
- The Theme aliases **only the design's own swatches**. Generated steps exist so the ramp reads in order and a later design step has a slot; bind one to the Theme only when the designer approves it. Primitives are never bound to elements, so the extra steps change nothing on the canvas.
- Create a hue's steps light to dark in one batch. The API's duplicate-name check treats a new `50` as clashing with an existing `500` in the same folder and saves it as `50-2`; rename it back to `50` with `rename_variable`. Variables cannot be reordered by API: create in order, or drag in the panel.
- The template ships placeholder ramps (`blue`, `pink`) so the Theme has something to alias. Once the client palette is in and every Theme token is re-pointed, delete the placeholder ramps (check no style, alias or embed uses them first). Leftover placeholder colours are a bug.
- The brand role may be a neutral. When the design's buttons and links are black, the Theme `brand`, `link`, `focus` and `button/primary-*` tokens alias `neutral/900` or `950`, and each decorative hue gets its own Theme token (`background/tangerine`) plus a `background-color-<hue>` utility.
- Status colours (`green`, `amber`, `red`) keep the template values until the design gives its own; say so in the decision log.

```
colour/                          one folder per hue; compiles to --_primitives---colour--<hue>--<step>
  <brand>/50 … 900               full ramp named by the real hue (navy, blue, coral), never "brand"; design swatches at their slots, the rest generated (OKLCH)
  <accent>/<step>                one folder per further hue the design uses
  neutral/0                      white
  neutral/50 … 950               11 greys, tinted toward the brand
  green/50 … 900                 success (template values until the design gives its own; Theme uses 100 and 500)
  amber/50 … 900                 warning
  red/50 … 900                   error
  info uses the brand ramp when the brand is blue; otherwise blue/100, blue/500
  alpha/black-10/20/40/60        rgba overlays
  alpha/white-10/20/40/60
spacer/                          the only raw spacing numbers on the site; huge / xhuge / xxhuge shrink per breakpoint, the rest stay constant
  xxtiny   0.125rem   2px
  xtiny    0.25rem    4px
  tiny     0.5rem     8px
  xxsmall  0.75rem   12px
  xsmall   1rem      16px
  small    1.5rem    24px
  medium   2rem      32px
  large    3rem      48px
  xlarge   4rem      64px
  xxlarge  5rem      80px
  huge     6rem      96px
  xhuge    8rem     128px
  xxhuge  12rem     192px
number/
  weight-400 / 500 / 600 / 700
  line-height-100 / 110 / 120 / 150 / 170     stored as 1, 1.1, 1.2, 1.5, 1.7
```

## 3. Theme (Color and Percentage; modes Light, Dark)

Every value aliases a Primitive. Dark values may be filled later, but the mode exists from day one so a dark section is a token flip on a `data-variant="dark"` wrapper, never a second class set.

```
background/  primary -> neutral-0 (Dark neutral-950) · secondary -> neutral-50 (Dark neutral-900)
             tertiary -> brand-50 (Dark neutral-800) · brand -> brand-500 · inverse -> neutral-950 (Dark neutral-0)
text/        primary -> neutral-950 · secondary -> neutral-700 · muted -> neutral-500 · inverse -> neutral-0
             brand -> brand-600 · link -> brand-600 · link-hover -> brand-800
border/      primary -> neutral-200 · subtle -> neutral-100 · strong -> neutral-400 · focus -> brand-500
surface/     card -> neutral-0 · card-hover -> neutral-50 · input -> neutral-0 · overlay -> black-alpha-60
             shadow-tint -> brand-900        (the colour inside box-shadow rgba; tinted shadows, never grey)
button/      primary-background -> brand-500 · primary-background-hover -> brand-700
             primary-text -> neutral-0 · primary-border -> brand-500
             secondary-background -> neutral-0 · secondary-background-hover -> neutral-50
             secondary-text -> neutral-950 · secondary-border -> neutral-300
status/      success-background -> green-100 · success-text -> green-500
             warning-background -> amber-100 · warning-text -> amber-500
             error-background -> red-100 · error-text -> red-500
             info-background -> blue-100 · info-text -> blue-500
opacity/     disabled 50% · muted 70%                                   (Percentage)
```

## 4. Typography (modes Desktop, 991, 767, 479)

Bind each `heading/*` size to **both** the bare tag and the matching class (`h1` and `heading-style-h1` both reference `heading/h1`); same for `text/regular` on `p` and `text-size-regular`. One edit moves both.

```
font/            heading · body · mono (only if the site shows code or figures)      Font Family
heading/         Desktop  T991   ML767  MP479      Relume's scale, display added above it
  display        4.5rem   4      3.5    3
  h1             3.5rem   3      2.75   2.5
  h2             3rem     2.75   2.5    2.25
  h3             2.5rem   2.25   2      2
  h4             2rem     1.75   1.5    1.5
  h5             1.5rem   1.5    1.25   1.25
  h6             1.25rem  1.25   1.125  1.125
text/                                             no breakpoint change (Relume keeps body constant)
  tiny 0.75rem · small 0.875rem · regular 1rem · medium 1.125rem · large 1.25rem · xlarge 1.5rem
weight/          regular -> weight-400 · medium -> weight-500 · semibold -> weight-600 · bold -> weight-700
line-height/     heading -> line-height-110 · tight -> line-height-120 · body -> line-height-150 · relaxed -> line-height-170
letter-spacing/  tight -0.02em · normal 0em · wide 0.05em
```

## 5. Spacing (modes Desktop, 991, 767, 479; every value aliases a spacer)

```
padding-global         2.5rem · T 2.5 · ML 1.5 · MP 1.25
padding-section/                   Client-First values (the designer works from Relume templates)
  small    -> spacer/large   (3)   · MP spacer/medium (2)
  medium   -> spacer/xxlarge (5)   · T spacer/xlarge (4) · MP spacer/large (3)
  large       7rem static          · T spacer/xxlarge (5) · MP spacer/xlarge (4)   (7 has no spacer; the one static value here)
gap/
  xsmall -> spacer/tiny (0.5) · small -> spacer/xsmall (1)
  medium -> spacer/medium (2) (MP spacer/xsmall) · large -> spacer/large (3) (MP spacer/medium)
content/                            vertical rhythm inside a section
  eyebrow-gap  -> spacer/tiny   (0.5)                       eyebrow to heading
  heading-gap  -> spacer/xsmall (1)                         heading to paragraph
  cta-gap      -> spacer/medium (2) (MP spacer/xsmall)      paragraph to button-group
  block-gap    -> spacer/large  (3) (MP spacer/medium)      header block to grid
```

## 6. Layout (modes on the tokens marked)

```
container/     large 80rem · medium 64rem · small 48rem · semi-full 120rem (edge to edge below 1920px, capped above)
               container-full has no token: no max-width at any breakpoint
max-width/     text 42rem (paragraph measure) · heading 36rem
radius/        small 0.25rem · medium 0.5rem · large 1rem · xlarge 1.5rem · round 62.5rem (pill)
border-width/  thin 1px · thick 2px
icon/          small 1rem · medium 1.5rem · large 2rem
navbar/        height 5rem (MP 4rem) · logo-height 2rem (MP 1.5rem)
z/             base 0 · dropdown 10 · sticky 20 · navbar 30 · overlay 40 · modal 50 · toast 60     Number
```

## 7. Animation (static; the timing table for IX3)

Webflow has no time or easing type, so durations are Numbers in seconds and distances are Sizes. Neither the Interactions panel nor the transition panel can bind a variable to a duration, so these tokens are the **values every IX3 preset is authored to** (`interactions` skill, section 7). Changing one means re-authoring the presets that use it, logged. Ease is recorded as the IX3 index (power2.out = 5).

```
duration/   instant 0.15 · fast 0.25 · base 0.6 · slow 1 · slower 2.4        seconds
stagger/    fine 0.02 · tight 0.05 · base 0.1 · loose 0.2
distance/   fade-up 1.5rem · fade-up-large 3rem · hover-lift 0.25rem · slide-in 2rem
scale/      hover 1.03 · press 0.97 · reveal 0.95 · pulse 1.04 · ring 1.4
marquee/    speed 40                                                            px per second
parallax/   amount 0.1                                                          ratio of travel each way
```

There is no per-element override: IX3 timing is per interaction, so a block that needs different timing gets a scoped copy of the preset (`interactions` skill, section 2).

## 8. Components (on demand)

Only `button/` exists at setup. Add a group when a component needs a knob that must vary independently of the global token. Component tokens alias Theme, Spacing or Layout, never Primitives.

```
button/   padding-y -> spacer/tiny (0.5) · padding-x -> spacer/xsmall (1)
          radius -> radius/round (pill sites) or radius/medium · gap -> spacer/tiny (icon to label)
later:    card/padding · card/radius · card/surface · input/height · input/radius · nav/link-gap
```

## 9. Utility classes bound to tokens

Every utility binds a token, so a value change happens in the Variables panel and never on the style guide page.

| Utility family | Binds |
|---|---|
| `heading-style-h1…h6`, `text-size-tiny…xlarge` | Typography `heading/*`, `text/*` (same tokens as the bare tags) |
| `text-weight-regular/medium/semibold/bold` | Typography `weight/*` |
| `text-color-primary/secondary/muted/inverse/brand` | Theme `text/*` |
| `background-color-primary/secondary/tertiary/brand/inverse` | Theme `background/*` |
| `max-width-text`, `max-width-heading` | Layout `max-width/*` |
| `container-large/medium/small/semi-full` | Layout `container/*` (`container-full` has no cap) |
| `padding-global`, `padding-section-small/medium/large` | Spacing `padding-global`, `padding-section/*` |
| `spacer-xxtiny…xxhuge`, `margin-xxtiny…xxhuge`, `padding-xxtiny…xxhuge` | Primitives `spacer/*` (the one place a primitive is bound, because the utility *is* the scale) |
| `text-align-left/centre/right` | no token |

## 10. Build order (MCP `data_variable_tool`)

1. `create_variable_collection` for each of the seven, then `reorder_variable_collection` into the order above.
2. `create_variable_mode` on Theme (`Dark`; the base mode is Light) and on Typography with `breakpoint_id` `medium` (991), `small` (767), `tiny` (479). On Primitives, Spacing and Layout create the same three names **without** `breakpoint_id` (manual), then apply them on the body tag per breakpoint with `data_style_tool` > `set_style_variable_mode`. The API has no delete or rename for modes; a wrong mode is removed from the panel's column menu.
3. Create Primitives first, statically. Then the semantic collections with `existing_variable_id` aliases. Modes are filled with `update_*_variable` plus `mode_id`.
4. `query_variables` with `css_name` to read the **compiled custom-property names** for the Global Styles embeds. Never guess a compiled name.
5. Bind the tag styles (`h1`–`h6`, `p`, `body`) and every utility family to their tokens with `data_style_tool` > `update_style` and `variable_as_value: <variable id>`, then remove the utilities' per-breakpoint overrides (`remove_properties` with `breakpoint_id`), since the tokens now carry the responsive values. Create the classes the starter lacks: `text-size-xlarge`, `container-semi-full`, `container-full`, `text-color-muted/inverse/brand`, `background-color-brand/inverse`, `max-width-text/heading`, and the `xxtiny` / `xtiny` spacer, margin and padding steps. Verified live on 22 Sep 2026: bare tags and utilities resolve through the tokens at every breakpoint.

6. **Starter clean-up**. The Client-First starter brings a `default` collection (`- Base Color - …`, `Background Color/…`, `Text Color/…`, `Link Color/…`, `Border Color/…`) and the classes `background-color-alternate` and `text-color-alternate`. The kit replaces all of it. Rebind every style still pointing at a `default` variable to its Theme token: `button` and its combos, `a`, `text-style-link`, `form_input` (border, placeholder), `form_input is-select-input`, `form_message-success/error`, and the style guide chrome (`fs-styleguide_header`, `_label`, `_label is-tag`, `_hero-label`, `_section-header`, `_message`). Find them by dumping `get_styles` with properties and searching for the `default` variable ids. Then delete the `default` variables (semantic first, then base), remove the empty collection in the Variables panel (the API cannot delete a collection), swap the `-alternate` classes on the Style Guide for `-inverse` and remove them. On the template itself this is done once, so a clone starts clean.

## 11. Adding or changing a token

If a needed value does not exist, propose it to the site owner: name, collection, group, value, modes, where it is used. Never hardcode in the meantime. Renames go through `rename_variable`, so bindings survive. Never delete a token that may be bound; rename it with a `deprecated-` prefix and report it.
