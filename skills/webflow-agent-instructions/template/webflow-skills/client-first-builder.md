---
name: client-first-builder
description: How to build and edit pages, sections, components, and styles on this site using our Client-First system. Reference this skill whenever creating or modifying layout, sections, grids, typography, spacing, colors, buttons, variables, components, slots, SVGs, code embeds, or any page structure — even for small edits. If a task touches the canvas, the style panel, or the Variables panel, read this first.
---

# Client-First Builder

This site is built on Finsweet's Client-First system with site-specific conventions defined here. The goal: anyone — human or agent — can read the Navigator and the class panel and understand the build without a meeting.

The site Rules are the law — every rule applies to every task. This skill is the manual for applying them. For motion, see the `interactions` skill; before any launch or handoff, run the `pre-launch-checklist` skill.

## 1. Philosophy

- Utility system first: shared, single-purpose utility classes handle typography, spacing, containers, and common backgrounds. Custom classes handle everything specific to one block.
- Ideally a text element carries **no class at all** — it inherits the defaults styled on the `body` and `h1`–`h6` tags. Add a utility class only to customize past the default.
- Never deep-stack classes: one base class plus at most one or two `is-*` combos, and only on elements that are not Components. A Component varies through **variants**, never combos.
- Every styling decision that repeats belongs in a variable. The style panel holds bindings, not raw values.

## 2. Naming system (complete)

| Thing | Pattern | Examples |
|---|---|---|
| Section wrapper | `section-[page]_[element]` | `section-home_hero`, `section-about_team` |
| CMS template section | `section-template-[collection]_[element]` | `section-template-blog_header` |
| Site-wide section | `section-global_[element]` | `section-global_cta` |
| Custom class in a section | `[page]_[element]_[tag]` | `home_hero_content`, `home_projects_item` |
| Reusable component | `component_[name]_[tag]` | `component_project-card_content` |
| Utility class | hyphens only, never an underscore | `text-size-large`, `padding-global` |
| Variant | Component **variant** on a Component; `is-` combo only on a non-component class | Button component, variant Secondary · `home_hero_image is-wide` |
| Interaction | `[Element] [Action] [State]` | "Navbar Dropdown Open" |

Common tags: `_content`, `_wrap`, `_list_wrap`, `_list`, `_item`, `_card`, `_image_wrap`, `_heading-wrap`, `_description`. Paragraph / supporting copy always uses `_description` (`home_hero_description`) — never `_text` or `_paragraph`. Words within one level are hyphenated (`home_hero_heading-wrap`); underscores only separate levels. The established `navbar_component` and `footer_component` stay as-is.

**Relume files (22 Sep 2026):** the designer works from Relume templates in Figma, whose layers carry Relume names (`section_header1`, `header1_component`, `layout241`). Those names never enter Webflow. Translate on build to the kit's names (`section-home_hero`, `home_hero_content`) and record the mapping in the build note (`layout241 → section-home_services`). Relume's Client-First values (type scale, section padding) are the kit's defaults, so only the names change.

## 3. Core structure recipe

Every section on every page (29 Sep 2026: vertical padding outermost, which supersedes Client-First's padding-global > container > padding-section). **A site built before 29 Sep 2026 keeps its old nest**; never migrate a working site, and match the nest already on the site you are editing:

```
section-[page]_[element]        ← the <section> tag
└─ padding-section-large        ← vertical rhythm (or -medium / -small)
   └─ padding-global            ← horizontal page gutter (site-wide, edit once)
      └─ container-large        ← max-width, centered (or -medium / -small / -semi-full / -full)
         └─ [page]_[element]_content
            └─ headings, text, lists, buttons…
```

- `container-large` (80rem) is the default. `-medium` (64rem) for narrower layouts, `-small` (48rem) for prose and forms.
- `container-semi-full` is edge to edge on laptops and desktops and caps at `container/semi-full` (120rem, 1920px) on wider screens. `container-full` has no cap at any breakpoint. Both still sit inside `padding-global`. Use them for galleries, maps, full-width media and strips; never for text.
- **Breakpoints (22 Sep 2026):** desktop base plus 991 / 767 / 479. No 1280, 1440 or 1920 breakpoint at setup; add 1280 only when a design needs it and log it, because a larger breakpoint cannot be removed. Past 1440 the page is **contained**: content stays centred at its container, section grounds and hero media run full bleed, type does not scale.
- `padding-section-large` (7rem, mobile portrait 4rem) for heroes and major sections, `-medium` (5rem, 3rem) as the default band, `-small` (3rem, 2rem) for tight strips. These are Client-First's values because the designer works from Relume templates in Figma (22 Sep 2026); every value is a Spacing token, so a change happens in the Variables panel, never on the class.
- Do not skip layers. Do not add classless divs.

## 4. Which class do I create? (decision tree)

1. Typography, spacing, a container, or a common background? → use an existing **utility**. Check the panel first; never create a near-duplicate utility.
2. A one-off variation of an element that is not a Component? → an **`is-*` combo** on the base class. On a Component → a **variant**.
3. Structure or styling specific to one section? → a **custom class** `[page]_[element]_[tag]`.
4. A block that repeats on two or more pages, three or more times anywhere, or repeats inside one section (cards in a grid, steps, logos)? → **`component_[name]_[tag]`**, built as a Webflow **Component** with props, slots and variants, a description and prop tooltips (section 12 and the components rule).
5. Genuinely unique text no utility covers (e.g. footer copyright: tiny, grey, all-caps)? → a custom class is correct: `footer_copyright-text`.

## 5. Grids, lists, and CMS

Repeating items always use the three-layer chain, which maps 1:1 to Webflow CMS elements:

```
home_projects_list_wrap      ← wraps the list area (padding/constraints live here)
└─ home_projects_list        ← display:grid or flex — maps to Collection List
   └─ home_projects_item     ← one cell — maps to Collection Item
      └─ component_project-card             ← optional reusable card
         ├─ component_project-card_image-wrap
         └─ component_project-card_content
```

- Grid styles live on `_list` only. Gaps come from the Layout collection `gap-*` variables.
- The page owns the grid; the component owns the card's internals. The same component drops into any page's `_item` unchanged.

## 6. Typography

- Tag defaults do the heavy lifting: `h1`–`h6` and body are styled globally and bound to Typography variables. Unmodified text gets no class.
- Size ≠ semantics: pick the tag by document outline, the look by class. A visually-small heading that is semantically second-level is `<h2 class="heading-style-h5">`.
- Utilities, every one bound to a token so a Variables edit never touches the style guide: `heading-style-h1…h6` and `text-size-tiny…xlarge` (Typography sizes), `text-weight-light/regular/medium/semibold/bold/xbold` (Typography weights), `text-color-primary/secondary/muted/inverse/brand` (Theme text/), `text-align-left/centre/right`, `background-color-primary/secondary/tertiary/brand/inverse` (Theme background/), `max-width-text/heading` (Layout).
- All font sizes bind Typography variables; families bind Typography `font/heading` and `font/body`. Never type a px font size.

## 7. Spacing

- Between sections: `padding-section-*` (already in the recipe).
- Within a section: the Client-First margin and padding system, every size class bound to a Spacing or Primitives token: a direction class (`margin-top`, `margin-bottom`, `margin-vertical`, `margin-horizontal`, `padding-*` likewise) plus a size class (`margin-xxtiny … margin-xxhuge`, `padding-xxtiny … padding-xxhuge`), or a `spacer-xxtiny … spacer-xxhuge` div. `padding-section-*` and `padding-global` bind their Spacing tokens. Never type a spacing number into a class; change the token.
- The scale (Primitives `spacer/`): `xxtiny` 0.125rem · `xtiny` 0.25 · `tiny` 0.5 · `xxsmall` 0.75 · `xsmall` 1 · `small` 1.5 · `medium` 2 · `large` 3 · `xlarge` 4 · `xxlarge` 5 · `huge` 6 · `xhuge` 8 · `xxhuge` 12. Bind the Spacing tokens that alias them (`gap/*`, `content/*`, `padding-section/*`), not the primitives.
- Responsive: base values are desktop; Variable Modes shrink them per breakpoint automatically. For a one-off responsive exception, add an `is-*` combo — never edit the global utility for one instance.
- Card grids collapse **4 or 3 → 2 (tablet) → 2 (mobile landscape) → 1 (mobile portrait)** unless the build note says otherwise. Set the column count on `_list` at each breakpoint; never rely on auto-wrap.
- The nav switches to the hamburger menu from 991 down. The desktop nav must fit at 992, the first desktop pixel.

## 8. Variables (the token system)

Seven collections, fully specified in the `variables` skill. Read it before binding anything.

| Collection | Holds | Modes |
|---|---|---|
| **Primitives** | `colour/` ramps with descriptive names, `spacer/` scale, `number/` weights and line heights. **Never bound to an element.** | Tablet, Mobile landscape, Mobile portrait (manual, on the body tag; large spacer steps only) |
| **Theme** | `background/`, `text/`, `border/`, `surface/`, `button/`, `status/`, `opacity/`. Every value aliases a Primitive. | Light, Dark |
| **Typography** | `font/`, `heading/display,h1…h6`, `text/tiny…xlarge`, `weight/`, `line-height/`, `letter-spacing/` | Desktop, 991, 767, 479 |
| **Spacing** | `padding-global`, `padding-section/`, `gap/`, `content/` rhythm gaps. Every value aliases a spacer. | Desktop, 991, 767, 479 |
| **Layout** | `container/`, `max-width/`, `radius/`, `border-width/`, `icon/`, `navbar/`, `z/` | Desktop, 991, 767, 479 |
| **Animation** | `duration/`, `stagger/`, `distance/`, `scale/`, `marquee/`, `parallax/`. The table the IX3 presets are authored to, not bound. | none |
| **Components** | `button/` tokens at setup (variables only; no Webflow Component is pre-created); other groups only when a component needs its own knob. | none |

Names are slash-grouped (`heading/h1`, `button/primary-background`). Bind semantic tokens only; a Primitive binding will not follow a theme or a rebrand.

<!-- REF: In the Webflow Instructions editor, insert live reference tokens to the site's actual variable collections here so agents always resolve current values instead of this static table. -->

**Buttons + hover:** hover is a CSS *state*, not a variable Mode. Bind `button/primary-background` on the default state and `button/primary-background-hover` inside the class's **Hover state**. Modes handle *context* — light/dark (`data-variant` wrapper) and breakpoints — and every token, including hover tokens, can hold different values per mode.

**Dark and brand grounds:** put `data-variant="dark"` (or `brand`) on the section and apply the matching Theme mode to it, so text, borders and buttons inside follow with no per-element classes. Light tints use the `background-color-*` utilities. Any selector CSS this needs (for example `[data-variant="dark"]` rules for things a token cannot reach) goes into the **Global Styles component's embed** under its own comment banner (section 9), never into page custom code.

**Adding a token:** if a needed value doesn't exist, propose it (name, collection, value, where used). Never hardcode in the meantime.

## 9. Global Styles and Global Scripts components

One Webflow Component named **Global Styles**, placed once on every page (inside `page-wrapper`, first child). Its single Embed holds all site CSS in **comment-headed sections** (22 Sep 2026: put the styles in the embed with the `global-styles` class and separate them with comments). The Client-First starter code at the top stays verbatim; the standard's sections are appended after it under banner comments (`SITE STANDARD: BASE`, `GROUNDS`, `CANVAS HOOKS`). Add a new section for a new concern; never edit the starter block and never put site CSS in page custom code. Three sections exist at setup:

1. **Base** — `:focus-visible` ring bound to `border/focus`; `h1–h6 { text-wrap: balance }`, `p { text-wrap: pretty }`; `b, strong` to the bold face and `weight/bold`; `img { max-width: 100%; height: auto }` (the starter block already clears rich-text margins); and one reduced-motion switch, `@media (prefers-reduced-motion: reduce) { *, *::before, *::after { transition-duration: 0.01ms !important; animation-duration: 0.01ms !important; animation-iteration-count: 1 !important; } }`, so hover transitions set in the Style panel need no CSS of their own (1 Oct 2026). This is one of the few places `!important` is necessary (8 Oct 2026: specificity first, `!important` only when necessary): a reduced-motion override has to beat every class, combo and inline style, and only `!important` beats inline styles.
2. **Grounds** — `[data-variant="dark"]` and `[data-variant="brand"]` selectors for things a token cannot reach inside a themed section: `hr`, form fields, image filters, selection colour, scrollbar.
3. **Canvas hooks** — `html:not(.w-mod-js)` or `.wf-design-mode` rules for Designer-canvas-only styling (the slider kit uses `.wf-design-mode`, see the `swiper-slider` skill), and `@media (prefers-reduced-motion: reduce)` fallbacks so animated content fails visible.

Compiled custom-property names inside the embed (`var(--_theme---border--focus)`) are read from the live site with `query_variables` after the collections exist, never guessed. Verified live on the guinea pig on 22 Sep 2026.

**Global Scripts** (29 Sep 2026) is its twin for JavaScript: one Webflow Component named **Global Scripts**, placed once on every page as the **last child** of `page-wrapper`, holding one Code Embed with the class `global-scripts` (`display: none`). The scripts we write live in it, each under a comment banner (`// ===== HOME FAQ =====`), each guarded so it does nothing on a page without its target. Third-party code (Google tag, CDN libraries such as Lenis and Swiper) loads from Site Settings code, never from here. Load order and the ready gate: section 14.

**Utility pages.** The 404 page gets a `page-wrapper` around its content like any page. The Password page cannot: Webflow refuses to move its form into a wrapper ("Password button cannot be moved outside the Password Form"), so there Global Styles is the body's first child and Global Scripts its last (MK-1, 30 Sep 2026).

## 10. Buttons

```
button-group            ← always, even for a single button
├─ Button component     ← class `button`, variant Primary (default), props: label, link
└─ Button component     ← variant Secondary
```

The button becomes a Webflow Component once the design repeats it; nothing is pre-created at setup because every website starts different (22 Sep 2026). Once a Component, its looks vary through variants (Primary, Secondary, and later Tertiary or Small if the design has them), never through `is-*` combos.

Button padding, radius and gap bind `Components/button/*`; colours bind `Theme/button/*`. Restyle buttons from the Variables panel, never per-instance.

The `button` class itself binds the same way: padding to `button/padding-y/x`, all four corners to `button/radius`, background, text and a 1px border (`border-width/thin`) to `Theme/button/primary-*`, with `primary-background-hover` in the Hover state; `is-secondary` rebinds only the colours to `button/secondary-*`. Check it on every new site: until 1 Oct 2026 the template's `button` was still bound to the starter `default` collection (variables section 10, step 6).

Hover effects stay editable in the Designer (1 Oct 2026: "I don't want those kinds of hover to be edited via CSS"). A fill hover is a native Backgrounds layer (linear gradient, colour stops on variable swatches, layer size 201% / 100%, position 100% 0 at rest and 0 0 on Hover) plus Transitions entries for background position and text colour. Custom properties will not take `background-image` (it has a native control), and the style API flattens a `var()` gradient, so the gradient is set by hand in the Designer; the API sets only plain values and the hover text colour. Variation is a component variant (Primary, Secondary), never an `is-*` combo; `is-*` stays for contextual one-offs on a plain class element (`button is-navbar`).

## 10a. State classes live on the Style Guide page

A state class is an `is-*` combo that only IX3 or a script adds at runtime (`is-open`, `is-active`, `is-looping`, `is-scrolled`). No page element carries it in the Designer, so **Clean Up unused styles** would delete it, and the IX3 panel can only pick a class that exists in the style list. So (29 Sep 2026):

- Style every state class in the **Designer** as a combo on its base class, token-bound like any other class.
- Anchor it on the **Style Guide page** in a **State classes** section: one labelled sample per state, a plain div carrying the base class plus the combo (`component_faq_item is-open`), with the state's name as its label. The sample documents the state and keeps the class alive. For a class inside a Component, the sample is a plain div with the same classes, not an instance.
- Never write a state class in the Global Styles embed, and never keep one alive with a hidden element on a live page.

## 11. Worked example — "Home / Services", built correctly

```
section-home_services                        <section>
└─ padding-section-medium
   └─ padding-global
      └─ container-large
         └─ home_services_content
            ├─ home_services_heading-wrap
            │  ├─ h2                          (no class — inherits global style)
            │  └─ p.text-size-large
            ├─ home_services_list_wrap
            │  └─ home_services_list          (grid; gap bound to gap-medium)
            │     └─ home_services_item       (×N — or Collection Item)
            │        └─ component_service-card
            │           ├─ component_service-card_image-wrap
            │           │  └─ img              (width/height set, alt on the asset, lazy unless first viewport)
            │           └─ component_service-card_content
            │              ├─ h3.heading-style-h5
            │              └─ p
            └─ button-group
               └─ Button component (variant Primary)
```

Finish checklist: naming matches Section 2 · no auto-generated classes · no hardcoded values where tokens exist (see the `variables` skill) · structure matches Section 3 · one `h1` on the page, heading order intact · every breakpoint checked (edit-safety + responsive-quality rules) · images follow links-and-media · motion follows the animation rule (`interactions` skill: presets by `data-animate`, no custom tweens) · every SVG assessed as image or Custom Element (section 13) · CSS and JS in Global Styles, Global Scripts or a `section-script-css` / `section-script-js` embed (section 14) · every Component has a group, description, prop tooltips, Base Element pieces and named slots (section 12).

## 12. Components: slot-ready and client-guided

Build every block that could repeat as if it will become a Component, because it usually does. When it does (the components rule gives the trigger), finish it so a client can use it without a meeting:

1. **Root and internals.** One root element carrying `component_[name]`, internals `component_[name]_[tag]`. The page owns the grid; the Component owns its internals.
2. **Props or slots.** Content that changes per instance is a prop (text, rich text, image, alt text, link, visibility). A place where the client adds, removes or reorders items (cards, buttons, links, logos) is a **slot**, filled with starter content (for example the Button Group component with two Buttons in its `Slot: Buttons`). Keep props for fixed-order pieces (a zoom that needs tile 4 to be tile 4).
3. **Group and description.** `set_component_metadata`: a group (Global, Base Elements, Slots, Cards, Sections, Navigation) and a description in plain language: what it is, when to use it, what the slot takes. The Components panel sorts groups and names alphabetically.
4. **Tooltips and prop groups.** Every prop gets a `tooltip` and a `group` (`create_prop` / `update_prop`). Plain language, no class or token names. The API rejects tooltips on Variant and Heading Tag props; leave those and note it.
5. **Prop order.** Own Variant first, own toggles next, then content groups in visual order (Eyebrow, Heading, Description, Button Row, Image); inside a group Variant, text or heading, heading tag, link, image, alt text, visibility last. The API has no reorder action: order props in the Designer (Properties panel on the component canvas), or create them in this order in the first place.
6. **Base Elements.** Inside Cards and Sections, the text and media pieces are themselves small Components (group Base Elements): **Eyebrow, Heading, Description, Button, Image**, each with its own props (text, heading tag, link, image, alt text, visibility) and variants. The parent binds its props through to them, so the Navigator reads Eyebrow, Heading, Description, Button Group, Image instead of anonymous classes. A button row is **Button Group**, a Component (class `button-group`) that wraps `Slot: Buttons` with starter Buttons. They appear once the first card or section is componentised; nothing is pre-created at setup.
7. **Slot names** (29 Sep 2026). Every slot gets a Navigator label `Slot: <what goes in, plural>`: `Slot: Buttons`, `Slot: Content`, `Slot: Media`, `Slot: Cards`, `Slot: Links`. "Slot:" is reserved for slots, so no Component name starts with it (the wrapper of a button slot is the **Button Group** component). Set it with `data_element_tool` > `set_display_name` and `scope_component_id`. Divs keep their class names as labels; never rename a class to get a nicer label.
8. **Read back.** `get_all_components` with `includeProps` after writing, and check one instance on a page.

API notes: the element builder lists a `ComponentSlot` type for creating a slot inside a definition (build with `scope_component_id`; verify it on the canvas). `create_prop` has no slot type. An instance picks a variant through its Variant prop (value = the variant id, `base` for the base).

## 13. SVG: image or Custom Element

Assess every SVG before it enters the site, including SVGs built in a Vercel preview and ported across. Read the source's CSS, keyframes, transitions, hover states and scripts for anything that targets the SVG or one of its children.

| What the source does | Build it as |
|---|---|
| Nothing inside it moves or changes | **Image**: one optimised SVG file (text outlined, svgo), uploaded to Assets, placed as an Image element |
| Only the whole SVG fades, slides or parallaxes as one piece | **Image**: the motion goes on its wrapper |
| A path draws in, a group loops, a part recolours on hover, parts reveal in sequence | **Custom Element**: inline SVG inserted with the WHTML builder, which stores `svg`, `g` and `path` as Custom Elements; one `g` per moving part so IX3 can target it |
| Boxes, cards or text moving inside a mock UI | divs for the boxes and text, static glyphs as SVG images, Custom Elements only for shapes that move |

Custom Element SVG checks: flatten `use` and `symbol` first (the canvas does not render them), keep `fill` and `stroke` as literal values or raw `var(--…)` strings (they cannot bind a variable), and look at the canvas before building motion on it. SVG images get CSS `aspect-ratio` from their viewBox, because Webflow prints no width or height for SVG assets.

## 14. Code embeds: where CSS and JavaScript live

**Style panel first** (8 Oct 2026). Before any CSS goes in an embed, ask whether the style panel can do it. Class styles, states (hover, pressed, focus), transitions, breakpoints, combos and variants all go in the panel (or the style API, which writes the same thing), and a property with no native control goes in the class's Custom properties. Embed CSS is for what the panel cannot express: selectors beyond a class and its states (`:nth-child(3n)`, `:has()`, sibling and attribute selectors such as `[data-variant]`), `@keyframes`, `@supports`, font stacks (the panel keeps only the first family), canvas-only hooks, runtime state classes and third-party library classes. Its comment banner says why the panel could not do it. This is not a ban on CSS; it keeps the site editable in the Designer.

| Code | Home | Class on the embed |
|---|---|---|
| Site CSS, and CSS reused by more than one section | **Global Styles** component embed, under a comment banner per concern (section 9) | `global-styles` |
| JavaScript we write for site-wide behaviour (the state helper, nav, Lenis init) | **Global Scripts** component embed, under a comment banner per script (section 9) | `global-scripts` |
| CSS that belongs to one section only | a Code Embed as that section's **last child** | `section-script-css` |
| JavaScript that belongs to one section only | a Code Embed as that section's **last child** | `section-script-js` |
| Google tag (gtag), CSS of site-wide libraries | Site Settings **head** code (gtag `async`) | none |
| Site-wide CDN libraries (Lenis) | Site Settings **footer** code, plain script tags, no `async` | none |
| Libraries only some pages use (Swiper; the slider kit CSS in Global Styles replaces Swiper's own CSS) | that **page's** footer code, so other pages never download them | none |

Every embed class is `display: none`, so no embed takes space on the canvas or the page. CSS defaults to Global Styles (small, renders on the canvas, survives style clean-up). JavaScript lives with what uses it, for page speed: site-wide behaviour in Global Scripts; a section's own script in its `section-script-js` embed, so it ships only on pages that have the section and travels with the section Component. Never copy a script between pages; make the section a Component.

**Why this setup is fast and safe:** third-party code downloads only where it is used; our code is inline (no extra request) and runs after the page is parsed; nothing we write blocks rendering.

**Load order on a published page** (read from a live Webflow page, 29 Sep 2026): Site Settings and page head code → the body, where every embed script runs **inline at its position** → jQuery → `webflow.js` → GSAP, ScrollTrigger, SplitText (IX3) → Site Settings footer code → page footer code → `DOMContentLoaded`. An embed script therefore runs **before** GSAP, Lenis, Swiper and the Webflow runtime exist. Every script we write waits for them with the **ready gate**:

```js
window.Webflow ||= [];
window.Webflow.push(() => {
  // runs after webflow.js, GSAP and every footer library have loaded
});
```

One gate per banner block, so one failing script never stops the others. Never depend on an `async` script (gtag): push events onto `window.dataLayer` instead of calling `gtag()` directly. Never add `async` to a library our scripts use; it breaks the order.

Every script, global or section:

- is modern ES6: `const`/`let`, arrow functions, template literals, optional chaining;
- runs inside the ready gate and leaks no globals. The only allowed globals are Webflow's own `window.Webflow` queue and the slider kit's public API, `window.Slider` and `window.SliderConfig` (`swiper-slider` skill);
- runs once, even if the embed is duplicated (a `data-` flag on the section);
- does nothing on a page without its target (returns early);
- is lightweight: no jQuery, no library for one job, event delegation over one listener per item, passive scroll and touch listeners;
- holds state and fires IX3 custom events only; tweens stay in IX3;
- is refactored before handoff: no dead code, no `console.log`, no duplicated selectors.

```js
// ===== HOME FAQ =====
window.Webflow ||= [];
window.Webflow.push(() => {
  const section = document.querySelector('.section-home_faq');
  if (!section || section.dataset.scriptReady) return;
  section.dataset.scriptReady = 'true';

  section.addEventListener('click', (event) => {
    const trigger = event.target.closest('[data-accordion-trigger]');
    if (!trigger) return;
    const open = trigger.getAttribute('aria-expanded') === 'true';
    trigger.setAttribute('aria-expanded', String(!open));
  });
});
```

The embed wraps scripts in a script tag and styles in a style tag (written in the Designer, never in these instructions).

## Appendix — fluid spacing backdoor (OFF by default)

This site uses stepped rem values with per-breakpoint Variable Modes. If a future decision switches to fluid spacing: Webflow variables compile to real CSS custom properties, so the Spacing tokens can be overridden with `clamp()` expressions in the Global Styles embed — same tokens, same bindings, only the resolved values become fluid. Do not enable this without the site owner's explicit sign-off.
