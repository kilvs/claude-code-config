---
name: webflow-ui-design
description: Design UI/UX for marketing sites, landing pages, brand sites, and (occasionally) web-app interfaces in a way that hands off cleanly to Webflow using Finsweet's Client-First system. Use this skill whenever the user wants to design a website or page, create a layout or mockup, build a style guide or design tokens, define typography/spacing/color systems, critique an existing design, or plan a UI that will be built in Webflow — even if they don't say "Webflow" or "Client-First" explicitly. Trigger on phrases like "design a landing page," "make a hero section," "build a style guide," "set up design tokens," "mobile-responsive layout," "review/critique this design," "I'm building this in Webflow," "an HTML file I'll convert to Webflow," "pre/post-launch checklist," "add schema/JSON-LD," or "make this SEO/accessibility/performance ready." Defaults to desktop-base, mobile-responsive, rem-based, Client-First-named output.
---

## Changes

- 29 Sep 2026: stale motion lines fixed (no `data-animate-trigger`, no accordion/tabs presets, IX3 specs not a GSAP init script); cursor effects point at the IX3 Mouse Move trigger.
- 29 Sep 2026: "Visual quality" now points at the `design-craft-check` skill instead of `frontend-design`.
- 29 Sep 2026: sliders point at the kit's Swiper slider kit (`swiper-slider` skill, `sliders` rule) in "Porting to Webflow".
- 29 Sep 2026: sites built before 29 Sep 2026 keep their old nest; runtime `is-*` state classes are anchored on the Style Guide page (kit builder section 10a).
- 29 Sep 2026: new section "Porting to Webflow": the kit auto-deploys at project start, every SVG is assessed as image or Custom Element, section scripts go in a `section-script` embed, and components are built slot-ready and client-guided. Mirrors the kit (`webflow-agent-instructions`, builder sections 12 to 14).
- 22 Sep 2026: editable master moved to `~/Documents/AI Agent Config/skills/`. Synced claude.ai copy is the published twin; re-upload after improvements.

# Webflow UI/UX Design (Client-First)

Design work that is visually intentional **and** structurally honest — every layout, token, and class is something that can be rebuilt in Webflow without rework. The north star: a designer-developer should be able to look at the output and reconstruct it in the Webflow Designer using Client-First conventions with no guesswork.

> **Companion skill:** this pairs with `page-quality-auditor` (shipped alongside it). This skill owns design, structure, tokens, and the Webflow-conversion launch layer (`launch/`); the auditor owns the deep per-criterion SEO / a11y / performance / best-practices detail. Install both. Where this skill says "see page-quality-auditor," that skill should be present.

## The non-negotiables

These are baked into every output unless the user explicitly overrides them:

1. **Desktop-base, mobile-responsive-oriented.** Webflow's base breakpoint is **Desktop**, and styles cascade down to tablet/mobile (and up to 1280/1440/1920). Design the full layout at the desktop base, then work *down* through tablet → mobile landscape → mobile portrait (≤479px), treating every smaller breakpoint as a first-class concern. The goal is a genuinely responsive result that holds on phones — not mobile-up authoring, which fights Webflow's cascade. See the 7-breakpoint table in `references/design-tokens.md`.
2. **rem-based sizing.** 1rem = 16px. Use Client-First approved rem values (see `references/design-tokens.md`). Exceptions: `1px` borders stay `1px`; `14px` (0.875rem) is allowed for small type; `2px` (0.125rem) for tiny spacing.
3. **Client-First naming.** Classes, structure, and folders follow Client-First v2.1. Full rules in `references/client-first.md`.
4. **Tokens via Variables across all five types.** Webflow Variables now support **Color, Size, Percentage, Number, and Font Family** — not just color. So typography sizes, spacing, container widths, font families, line heights, and font weights can all be variables, not just hardcoded class values. Use variables for any value reused across the site and worth changing in one place; keep the rem system for the values themselves. Variable **Modes** handle responsive/theme switching (a Size variable can hold one value on desktop, another on mobile; a Color variable one value in light mode, another in dark). See `references/design-tokens.md` for the full token-to-variable mapping. (This supersedes older Client-First guidance that said size variables don't exist — they do now.)
5. **Structurally honest mockups.** Mockups are HTML/CSS built from div-and-class structures that map 1:1 to Webflow elements — not SVG art or absolute-positioned trickery that can't be rebuilt.
6. **Launch-ready by construction.** When the output is a designed HTML *reference file* (the deliverable the user rebuilds in Webflow — think Figma design, but already best-practices-correct), bake in the SEO/a11y/perf attributes, meta, and JSON-LD so the developer ports them straight across. Run the pre-launch checklist as it's built and provide the post-launch checklist. See `launch/` and the `page-quality-auditor` skill.

## Pick the task, then route

This skill produces these kinds of output. Identify which the user wants (often more than one) and follow the matching path. When unsure, ask once; otherwise infer and state your assumption.

| User wants | Output | Read first |
|---|---|---|
| A design / layout / page / section | **Visual mockup** (HTML/CSS, renderable) + structure notes | `references/client-first.md`, `references/design-tokens.md` |
| A build-ready HTML reference file to convert to Webflow | **Designed HTML file** with attributes, meta, JSON-LD + checklist | `launch/checklist.md`, `launch/attributes.md`, `launch/schema-templates.md` |
| Tokens, type scale, spacing, color system | **Design spec** (tables of values + Webflow variable names) | `references/design-tokens.md` |
| A full style guide | **Client-First style guide** (tokens + components + class list) | both references + `references/style-guide.md` |
| Feedback on an existing design | **Critique** against a rubric | `references/critique-checklist.md` |
| Motion / scroll / hover animations on a build | **IX3 preset specs** (`data-animate` per element) | `references/animation.md` |
| A slider, carousel or scrolling card row | **Slider spec**: roles, slides across per breakpoint, settings | kit skill `webflow-agent-instructions/template/webflow-skills/swiper-slider.md` |
| Pre/post-launch QA (SEO, a11y, best practices, schema, perf) | **Launch checklist** + JSON-LD templates | `launch/checklist.md`, `launch/schema-templates.md` |

Always read the relevant reference file(s) before producing output — they hold the exact approved values and naming rules. Don't reconstruct them from memory.

## Workflow

### 1. Frame the design problem (briefly)
Before designing, get clear on: the page/section's job, the audience, the brand feel (1-2 adjectives), and any existing brand assets (colors, fonts, logo). If the user gave a brief, extract these from it rather than re-asking. For client work, ask whether the client has an existing style guide — if so, conform to it (Client-First explicitly defers to a client's established color/naming system).

### 2. Establish tokens first, always
Even for a single mockup, define the foundation before drawing: color tokens (primitive → semantic), the type scale, and the spacing scale. This is what makes the output Webflow-ready instead of arbitrary. Use `references/design-tokens.md` for the scales and `references/client-first.md` for variable naming. A mockup built on undefined values is a redo waiting to happen.

**Brand colours are anchors, not literal fills.** When a client/project provides brand colours, treat them as the *starting palette* to build a comfortable system around — not exact values to apply at full saturation everywhere. Provided colours are usually saturated and high-energy; using all of them at full strength fights the eye. Instead:
- Keep the brand colours as **primitive tokens**, then derive **semantic tokens tuned for comfort and contrast** from them. A saturated brand navy can be deepened/desaturated for large surfaces; a brand colour can spawn lighter/darker shades for text, borders, and hover states.
- **One accent at a time, on a bed of neutrals.** A polished design is mostly neutral surfaces — white, off-white/"dirty white," light and muted greys (or, in a dark theme, deep neutrals with tinted off-white text) — with the most saturated brand colour reserved for a single high-impact role (usually the primary CTA) so it reads as "the thing to do." Demote other saturated colours to sparse accents (badges, small links, thin borders). The neutrals give the eye rest and make the accent pop; a page built only from brand colours exhausts the eye. See the neutral ramp in `references/design-tokens.md`.
- **Comfort is a requirement, not a nicety.** Body text against its background must be easy to read for sustained periods — meet WCAG AA, and beyond that, avoid full-saturation colour on large areas or as long-form text. If a combination vibrates or strains, tone it.
- Map each brand colour to a token by its **role**, never its name (a brand colour becomes `background-primary` or `brand-accent` by function). Project-provided colours are scoped to that project only — never carry them into other projects or store them as skill defaults.

If no brand colours are given, derive a palette that fits the stated brand feel, following the same comfort principles.

### 3. Design desktop-base, verify down to mobile
Lay out the full desktop composition first (Webflow's base breakpoint). Then work *down*: define how it adapts at tablet (≤991px), mobile landscape (≤767px), and mobile portrait (≤479px) — what stacks to single column, where type and section padding shrink, what hides. Treat the smaller breakpoints as first-class: a desktop layout that breaks at 479px has failed. In mockups, show the desktop composition and make the responsive behavior real (see below) so the down-cascade is visible, not just described. Name the responsive intent in Client-First terms (which sections stack, which use `padding-global` vs `padding-section`, which Size variables shrink via breakpoint modes).

**A full page always includes a header and footer.** Unless the user explicitly asks for an isolated section/component, every page design has:
- **Header / nav** (`navbar_component`): logo, primary nav links, and the primary CTA. On mobile this collapses to a logo + hamburger; the nav links live in a menu. Use the semantic `nav` tag.
- **Footer** (`footer_component`): logo + short tagline, navigation/link columns, social links, contact, copyright, and any legal links (privacy, terms). Use the semantic `footer` tag. On mobile the columns stack; on desktop they sit in a multi-column row.
Render these in previews, not just describe them — a homepage without a footer looks unfinished. If space in a preview is tight, keep the header and at least a condensed footer rather than dropping either.

### 4. Build the output
- **Mockups:** Use the Visualizer (`show_widget`) to render inline HTML/CSS the user can see. Structure the markup as nested divs with Client-First class names as real `class` attributes, so the structure doubles as build documentation. See "Mockup construction" below.
- **Specs / style guides / critiques:** Produce as written deliverables. For a substantial style guide the user will keep, write it to a file; for an inline spec or critique, respond in chat.

### 5. Hand off
End design output with a short **Webflow build note**: the section/wrapper/container structure, the key classes introduced, which colors map to which variables, and any motion specs (see Animation below). This is the bridge from "design you can see" to "site you can build." Keep it tight — a developer's checklist, not an essay.

**The HTML reference file as the deliverable.** A core use of this skill is producing a *designed HTML reference file* the user converts to Webflow by hand — the role Figma plays for many teams, except this file is already best-practices-correct. When that's the deliverable, build the launch quality in from the start: semantic tags and heading order, the optimising attributes (`launch/attributes.md`), per-page meta/OG/canonical, and the JSON-LD blocks for the page type (`launch/schema-templates.md`) included in the `<head>`, clearly marked so the dev knows what to paste where. Then run the pre-launch checklist (`launch/checklist.md`) as you build and hand over the post-launch half.

**Quality is a build-time standard, not an afterthought.** For any real page HTML/CSS/JS (not a quick mockup), apply the `page-quality-auditor` skill in build-time mode so Performance, SEO, Accessibility, and Best Practices come out clean while writing. The `launch/` folder here is the Webflow-conversion layer on top of that; the auditor's references hold the deep per-criterion detail. Don't duplicate them — point to them.

## Porting to Webflow

When a design or a Vercel preview moves into a Webflow site:

1. **Kit first.** At the start of the project, deploy the agent-instruction kit to the site without being asked (`webflow-agent-instructions`, Workflow step 0).
2. **Assess every SVG.** Read the preview's CSS, keyframes, hover states and scripts for anything aimed at the SVG or its children. Something inside moves or changes → **Custom Element** (inline SVG, one `g` per moving part). Nothing inside moves → **uploaded SVG image**. The whole SVG fading or parallaxing as one piece still counts as static. Full table: builder section 13.
3. **Components, slot-ready.** Build every repeating block with one clean root so it can become a Component. Where the client adds, removes or reorders items, use a slot with starter content. Each Component gets a group, a plain-language description and a tooltip on every prop. Text and media pieces inside are Base Element components (Eyebrow, Heading, Description, Button, Image, Button Group), and slots are named `Slot: <what goes in, plural>` (`Slot: Buttons`, `Slot: Content`). Builder section 12.
4. **Code embeds.** Site CSS goes in the Global Styles component and the site's own JS in the Global Scripts component, each under comment banners. Section-only code goes in a Code Embed as the section's last child, classed `section-script-css` or `section-script-js`. Every embed is `display: none`; scripts are ES6, scoped, lightweight, state only. Builder section 14.

5. **Sliders.** Every slider, carousel or card row that scrolls sideways is the kit's Swiper slider (`swiper-slider` skill, `sliders` rule): parts marked with `data-swiper-element` roles, slide width and gap set by classes (so the design specifies slides across per breakpoint, not a Swiper number), arrows as real buttons, dots optional. A grid that becomes a slider on smaller screens is a class change, not a second design. Never the native Webflow Slider or another library.

The Webflow build note lists each SVG's verdict (image or Custom Element), each Component with its props and slots, and where each piece of CSS and JS lives.

## Animation (native IX3 presets)

Motion is built with **Webflow's native Interactions with GSAP (IX3)**, never Classic Interactions and never a custom-code GSAP script. Presets are site-scoped interactions that an element opts into with one attribute, so a design spec names the preset, not a tween:

- `data-animate="<preset>"` — `fade-in`, `fade-up`, `fade-down`, `fade-left`, `fade-right`, `scale-in`, `slide-left`, `slide-right`, `stagger` (children in sequence), `split-lines`, `split-words`, `split-letters`, `parallax`, `lift` (hover), `press` (click), `pulse` (active item loop), `ring` (hover), `marquee`.
- Hero reveals on load use the load variant `data-animate="fade-up-load"` (hero only); everything else reveals on scroll at `top 85%`.
- Behaviours: `data-nav="push|slide|dropdown"` with `-toggle` and `-panel` parts; the nav timeline is authored in the panel and a tiny state helper keeps in-bar dropdowns one-open-at-a-time. Accordions and tabs are not presets (dropped 22 Sep 2026); build them per site when needed.
- Cursor effects (tilt, magnetic, spotlight, follow) use the IX3 Mouse Move trigger (kit `interactions` skill, section 5a), never a script.
- **No per-element timing.** Durations, staggers and distances come from the Animation variable collection and are authored into each preset; a block that needs different timing gets a page- or component-scoped copy, logged.

Example spec line: `home_services_list` → `data-animate="stagger"`; `home_hero_heading` → `data-animate="split-lines"`; `home_hero_image_wrap` → `data-animate="parallax"`.

Reduced motion is set per interaction (reveals skip to their end state, loops and parallax do not animate), and the from-state lives in the interaction so content fails visible. The full preset table, behaviours, helper and MCP authoring live in the kit skill `webflow-agent-instructions/template/webflow-skills/interactions.md`; `references/animation.md` here is the short pointer.

## Mockup construction

Mockups are made with the Visualizer. Before the first `show_widget` call, silently load its `mockup` module via `read_me`. Then:

- Build with semantic structure: `[page]_[element]_section` wrapper → `padding-section-*` → `padding-global` → `container-large` → `[page]_[element]_content`. Mirror the Client-First core structure (see reference), including the `..._list_wrap > ..._list > ..._item` chain for grids, `..._image_wrap` for images, `heading-style-h*` for headings, and `button-group` around CTAs.
- Put Client-First class names in the actual `class` attribute. Use CSS custom properties for colors that map to the planned Webflow variables (e.g. `--background-primary`, `--text-primary`).
- Size in rem using approved values. Set `:root { font-size: 16px }` so rem math is literal.
- Default to rendering the **desktop** composition; show the responsive behavior by overriding downward with `@media (max-width: 991px)`, `@media (max-width: 767px)`, `@media (max-width: 479px)` so the user sees the actual down-cascade. Always verify the layout holds at mobile portrait (479px).
- Keep it self-contained: real type, real spacing, placeholder copy that fits the brand.
- **Image slots, not fake photos.** Never embed copyrighted/stock imagery or the client's own hosted assets into a mockup. Instead render an intentional placeholder block sized to the real aspect ratio (e.g. 4:3 hero, 1:1 cover/avatar) with a small label naming what it is and the Webflow/CMS field it maps to (e.g. "Hero image · 4:3", "Cover · 1:1 → episodes_image"). This documents the slot and ratio without pretending the art is final, which is more useful for handoff than a placeholder photo. Real imagery comes from the client's assets or licensed stock at build time.

A mockup that looks good but uses random px values and non-Client-First class names has failed the brief — it can't be handed off. Visual quality and structural honesty are both required.

## Visual quality

Webflow-ready does not mean generic. For aesthetic direction — typography pairing, color confidence, spacing rhythm, avoiding templated defaults — apply the principles in `references/critique-checklist.md` (the same rubric used to judge others' work judges yours) and the `design-craft-check` skill (plan review before building; Refuse, Prefer and Verify lists after). Intentional contrast, a clear type hierarchy, and generous, consistent spacing do most of the work.

## Notes on use inside Claude Design

This skill's methodology, tokens, and Client-First rules are portable: they work whether loaded as a formal skill, pasted into a Claude Design project as context, or used directly here. The Client-First handoff note is what makes any of those outputs translate into a real Webflow build.
