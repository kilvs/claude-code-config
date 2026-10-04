# Webflow playbook

**Status:** daily. Finsweet Client-First on every site.

## What it is used for
Every client site. Some go through a static HTML preview repo first, some are built in the
Designer directly.

## Conventions
These apply to every Webflow build unless an org says otherwise:

- Structure (vertical padding outermost, the user 29 Sep 2026; sites built before then keep
  their old nest and are never migrated) `section-[page]_[element]` >
  `padding-section-*` > `padding-global` > `container-large` > `[page]_[element]_content`; shared pieces `component_*`, variants
  `is-*`. Name by role, no abbreviations, no auto-generated classes.
- Use the site's utilities (`heading-style-*`, `text-size-*`, margin and padding). Bare tag when
  a heading needs nothing else. No empty or single-child wrapper divs.
- Styles live in classes, never in page custom code: the user reviews the Designer canvas, which
  does not run custom code. Only an Embed's `<style>` renders on the canvas.
- No Custom Elements for spans; block pieces are Div or Text Blocks. SVGs are uploaded assets
  placed as Image elements, one file per colour. Graphics: if any part
  animates it is never an image; build it as divs (or Custom Elements when an SVG shape itself
  moves), one element per moving part. A static graphic is one outlined SVG uploaded as an Image,
  never WebP/PNG. Assess every
  SVG ported from a preview (29 Sep 2026): read its CSS, keyframes, hover states and scripts;
  anything inside moves → Custom Element, nothing moves → SVG image (kit builder section 13).
- Breakpoints 991 / 767 / 479 only at setup; 1280 added per site when a design needs it, never
  1440 or 1920 (22 Sep 2026). Ultrawide stays contained: centred container, full-bleed grounds,
  fixed type. Containers: large 80rem (default), medium, small, semi-full (edge to edge to
  1920px, capped at 120rem beyond), full (never capped). Grids collapse 4/3 → 2 → 2 → 1; the nav
  goes to the hamburger from 991 down and must fit at 992. Rem by default; px only where an
  org asks for it.
- Utilities all bind tokens (22 Sep 2026): text, colour, background, max-width, container,
  spacer / margin / padding, section and global padding. Section padding is Client-First's
  3 / 5 / 7rem (mobile 2 / 3 / 4) because the designer works from Relume templates in Figma.
- Components (22 Sep 2026): nothing pre-created at the start of a build, every site starts
  different. A block becomes a Webflow Component once it repeats on two pages, three times, or
  inside a section; variation through variants, never `is-*` (combos stay for non-component
  classes). Dark grounds: `data-variant="dark"` on the section; selector CSS goes
  in the Global Styles component's embed under its own comment banner.
- Relume (22 Sep 2026): when a designer works from Relume templates in Figma: Relume names
  never enter Webflow; translate to the kit's names and record the mapping. Relume's type scale
  (h1 3.5rem to h6 1.25rem, mobile 2.5 to 1.125) and section padding are the defaults. Global
  Styles component keeps one embed; the standard's CSS is appended under comment banners
  (base, grounds, canvas hooks) after the untouched starter code.
- Navbar: never the native Webflow Navbar element. Divs, links and real `button`s (DOM `dom_tag: button`), the state helper for state and ARIA, IX3 custom events for motion (interactions skill sections 3 and 8). The Navbar is a Component (group Navigation).
- Colour primitives (1 Oct 2026): the design file's swatches only, no generated tints, no leftover template ramps or starter `default` collection (variables skill sections 2 and 10).
- Variables (22 Sep 2026): seven collections, Primitives (never bound, hue folders), Theme
  (Light + Dark), Typography (automatic breakpoint modes), Spacing and Layout (manual modes of
  the same names applied on the Body tag per breakpoint, because Webflow lets one collection
  bind a breakpoint), Animation (the IX3 timing table), Components (button only at setup).
  Slash-grouped names. Manual modes go on the body tag per breakpoint through the style API
  (`set_style_variable_mode`); utilities bind tokens with `variable_as_value` and lose their
  per-breakpoint overrides. Full spec:
  `skills/webflow-agent-instructions/template/webflow-skills/variables.md`.
- Motion (22 Sep 2026): native Interactions with GSAP (IX3) only, no IX2, no custom-code tweens.
  Site-scoped presets targeted by `data-animate="fade-up"` and friends; nav authored in the panel;
  a compact state helper in Global Scripts keeps in-bar nav dropdowns to one open at a time (accordions and tabs left the standard, 22 Sep 2026). Fail visible: the
  from-state lives in the interaction, never `opacity:0` in a class. Spec:
  `skills/webflow-agent-instructions/template/webflow-skills/interactions.md`.
- Agent-instruction kit (29 Sep 2026): deployed automatically at the start of every Webflow
  project, no ask needed; existing kit files that differ are listed, not overwritten
  (`webflow-agent-instructions` step 0). This is the Instructions panel, never a site publish.
- Components (29 Sep 2026): built slot-ready and client-guided: group, plain-language
  description, a tooltip on every prop. Pattern: text and
  media pieces are Base Element components (Eyebrow, Heading, Description, Button, Image,
  Button Group) with props bound through; slots named `Slot: <what goes in, plural>`
  (`Slot: Buttons`) via `set_display_name`, "Slot:" reserved for slots; divs keep class names.
  Kit builder section 12.
- State classes (29 Sep 2026): runtime-only `is-*` classes (added by IX3 or a script) are
  Designer combo classes anchored by a labelled sample in a State classes section on the Style
  Guide page, because Clean Up unused styles deletes classes no element carries and IX3 can
  only pick classes that exist (kit builder section 10a).
- Code embeds (29 Sep 2026): site CSS in the Global Styles component, the site's own JS in a
  Global Scripts component (last child of `page-wrapper`, class `global-scripts`), both one
  embed with comment banners. Section-only code in `section-script-css` / `section-script-js`
  embeds, last child of the section. All `display: none`. Site Settings holds third-party code
  only: gtag (`async`) and site-wide library CSS in the head, site-wide CDN libraries (Lenis) in
  the footer; a library only some pages use (Swiper) loads from those pages' code. Section JS
  stays in its `section-script-js` embed so it ships only where the section is; the IX3 state
  helper lives in Global Scripts.
  Embed scripts run inline before jQuery, `webflow.js`, GSAP and the footer libraries (read off
  a live page), so every script we write sits inside `Webflow.push(() => { … })`.
- Sliders (29 Sep 2026): Swiper 14 through `data-swiper-element` roles, Designer classes own layout, one kit script in Global Scripts, named configs for breakpoints, grid-to-slider by class. Rule `rules/sliders.md`, manual `webflow-skills/swiper-slider.md` in the kit; demo and copyable docs on Sample Slider Test 51 (`/slider-docs`).
- Publish only on the user's explicit word, one yes per publish. Staging first where it exists.

## Accounts and tools
| MCP server | Workspace | Chrome profile |
|---|---|---|
| `webflow` | Your workspace. Add one server per Webflow account, each named for it. | The profile logged in to that account |

Call `webflow_guide_tool` once per session before other Webflow tools. Query the style list
(`data_style_tool query_styles`) before creating a class.

## Gotchas that became rules
| Date | What happened | Rule |
|---|---|---|
| 18 Sep 2026 | Layout only showed on the published site | Styles in classes, not custom code |
| 21 Sep 2026 | Canvas-only styling needed for sliders | Key off `html:not(.w-mod-js)` inside a section Embed |
| 21 Sep 2026 | Sticky scroll block never stuck | Runway is content height (`min-height`), never padding; never read `offsetTop` of the sticky element |
| 21 Sep 2026 | Bulk rem to px, 2,500 values | 20 actions per `update_style` call; tag styles, component variants and embeds need separate passes |
| 29 Sep 2026 | A failed nested `data_element_builder` call still created the parent | Read the parent back after any builder error; `width`/`height` are reserved image attributes; `add_page_script` 404s on a page with no code, use `set_page_scripts` |
| 29 Sep 2026 | Native Tabs stuck at three tabs through the API; a multi-group click stuck on `play` | Build tab-like UI as buttons plus one single-group IX3 click interaction per step on `restart`; `multiline` props must be `textContent` |
| 29 Sep 2026 | `update_style` turned a gradient into a flat colour and `calc(-1 * var())` into a positive margin | The style API binds any value containing `var()` to its first variable: bind only single-token properties (`variable_as_value`), write gradients and `calc()` as literals |
| 29 Sep 2026 | WHTML builder refused `:focus-visible`, `:last-child`, `@keyframes`; `id` attributes stored as custom attributes; native Tabs builds three tabs only | Add those pseudos with `update_style` `pseudo`, keyframes in a section embed; set ids with `set_dom_id`; build tabs as divs when a fourth tab or split columns are needed |
| 29 Sep 2026 | Componentising a section through the API | `create_prop` has no slot type, so a repeating block goes in as its own Component (rows) inside page-level wrappers; an instance picks a variant through its `Variant` prop (value = variant id, `base` for the base); the WHTML builder skips classes that have no CSS, so `create_style` them first; read instance props back after writing (one readback showed a stale value) |
| 29 Sep 2026 | Inline SVG through the WHTML builder | An `<svg>` in WHTML html becomes Webflow Custom Elements (DOM `svg`, `g`, `use`, `symbol`, `filter`), attributes kept, so IX3 can target each group; tags are stored lowercase (`fedropshadow`) and the HTML parser restores the casing. `fill` and `stroke` cannot bind a colour variable: leave the raw `var(--…)` string |
| 29 Sep 2026 | The Custom Element SVG never showed on the canvas or in preview; the canvas does not render `<use>`/`<symbol>` | Animated graphics: boxes as divs (token grounds, box-shadow), glyphs as uploaded SVG assets in Image elements, IX3 on the divs with `xPercent`/`yPercent`. Inline SVG only for shapes with no `use`, and check the canvas before building motion on it |
| 29 Sep 2026 | A state combo added by IX3 (`is-looping`) kept the old `display: block` after the base went flex; the row stacked only on the published page | When a base class changes layout, read its combos back too; test IX3 class adds on staging, the canvas never runs them |
| 29 Sep 2026 | Binding a custom attribute to a component prop through the API fails on Block and DOM elements ("value must be a string or a binding") | Carry the prop as hidden text (a text element bound to the prop, class `display:none`) and let the section script read it; or bind the attribute by hand in the Designer panel |
| 29 Sep 2026 | CSS-only shapes (a zero-size border triangle, a border-top dotted line) collapsed on the Designer canvas, which draws empty divs as placeholder boxes | Static shapes are an SVG image; keep divs only for parts that move, and give them real width/height or absolute position |
| 29 Sep 2026 | Mobile PageSpeed 71: the mobile hero image variant (hidden on desktop) was lazy and unsized, so it was a late LCP and pushed the next section down | Per-breakpoint image variants: the phone one gets `loading=eager` + `fetchpriority=high` as attributes; every SVG image gets CSS `aspect-ratio` from its viewBox (Webflow prints no width/height for SVG assets); `<html lang>` needs the Localization primary locale set in the Designer |
| 29 Sep 2026 | Section code embeds | Classes `section-script-js` and `section-script-css` (`display:none`), last child of the section; ES6, scoped, lightweight, state-only scripts; shared code in the Global Styles / Global Scripts components (kit builder section 14) |
| 29 Sep 2026 | `set_visibility` (and `set_settings` visibility) on a new Section returned "[Conflict] ... component map" three times | Hide it with a combo (`is-hidden`, display none) and log it; the owner can swap to the Visibility setting in the Designer |
| 29 Sep 2026 | A local render of the live page missed utility classes (padding, eyebrow) that the new section uses | Published CSS carries only classes already on the page: add any newly used site class to the harness CSS from `query_styles` before comparing |
| 29 Sep 2026 | Lenis smooth scroll on a Webflow site with IX3 | Site Settings code: `lenis.css` in head, `lenis.min.js` + init in footer (jsDelivr, SRI), init on DOMContentLoaded; drive `lenis.raf` from `gsap.ticker` and `lenis.on('scroll', ScrollTrigger.update)` (Webflow loads GSAP + ScrollTrigger for IX3); keep Lenis `anchors: false`, webflow.js already glides in-page links; stop Lenis while a menu or modal is open |
| 29 Sep 2026 | Swiper sample build on Sample Slider Test 51 | A `ComponentSlot` reports `tag: div` and has an `attributes` setting, so a slot is a real element that takes custom attributes (published HTML not yet checked). The API cannot put starter content in a slot inside a definition (`move_element` internal error; `data_component_builder` into the slot: "Missing element"); fill slots on instances with `insert_in_slot`, nested slots named by display name (`Slot: Content`) work in one call. Attribute-to-prop binding failed again on a Block root; visibility-to-boolean-prop binding works |
| 29 Sep 2026 | Swiper round two on Sample Slider Test 51 | `display: grid` with no template draws as a 2x2 grid on the canvas, so single-column wrappers use flex column. A Collection List's own styles beat a zero-specificity `:where()` default, so set `display` on the list's class. Without Swiper's CSS, the a11y `.swiper-notification` span becomes a flex item (eats a gap, shows text); hide it in the embed. Collection List sort cannot use created date through the API; add a Number `order` field. Kit docs: https://claude.ai/artifact/HV9wVqPs8JMA6PzYbZA47j |
| 29 Sep 2026 | IX3 API re-test on Sample Slider Test 51 (test interactions "Kit test T1/T3/T4", page-scoped to /slider-docs, targeting `data-kit-test`, which no element carries) | `wf:mouse-move` needs `config: {}` and a `triggerMetadata.role` per timeline; timeline `settings: {repeat, yoyo}` is stored but unproven at runtime; a child target relative to the trigger still needs a real class, and a `wf:selector` child target is page-wide. Follow-up the same day: action-level `timing: {repeat: -1, yoyo: true}` (Webflow's documented surface) and a trigger-children target `wf:any-element "*"` + `filterContext {relationship: "direct-child-of", filterBy: ["wf:trigger-only", ""]}` are both accepted (tests T5, T6). Loops and stagger stay panel-authored until a Preview proves playback |
| 29 Sep 2026 | Slider docs page on Sample Slider Test 51 | WHTML `<pre><code>` becomes a DOM `pre` plus fragmented InlineCode; use the native `CodeBlock` element (builder type), whose only content setting is `code` (no language through the API; newlines kept). `set_dom_id` on new blocks returned the "[Conflict] component map" error and an `id` custom attribute fails too, so in-page anchors use `data-*` plus a tiny scroll script. The published component slot renders as a bare `<div>` with no class. The style panel keeps only the first family of a font stack (`Menlo, Consolas` saved as `Menlo`); put stacks in an embed |
| 2 Oct 2026 | Socials slider | Custom attribute values cannot contain double quotes, so Swiper object settings go in a named config (`data-swiper-config` + `section-script-js` embed). Page footer code goes in with `data_scripts_tool` `set_page_freeform_code`; check the SRI hash against cdnjs with `openssl dgst -sha512 -binary \| openssl base64 -A`. Embeds do not render as script tags in the canvas; to test a slider, load Swiper into the canvas frame and run the setup by hand, then reload. `set_display_name` takes `element_id`, not `id` |
| 2 Oct 2026 | Static / Slotted section variants | Variants cannot add or remove elements, so put two classed wrappers in the component and let the variant hide one (`display: none`). `move_element` takes `id`, `anchor_element_id`, `creation_position` and `scope_component_id`; `insert_component_instance` and `set_component_instance_prop_values` work inside a definition with `scope_component_id`. Slider kit: a hidden mask is skipped |
| 2 Oct 2026 | Contact form | The builder takes FormBlockLabel, FormTextInput, FormTextarea, FormSelect, FormRadioInput, FormCheckboxInput, FormButton; type `Form` brings Name/Email defaults, move them rather than delete. Settings keys: name, domId, required, type, groupName, value, buttonText, redirect, text; `placeholder` and select choices are Designer only (Settings panel), and `placeholder` is a reserved attribute. `for` works as a custom attribute. `accent-color` cannot take a color variable: set `color` to the token and `accent-color: currentColor`. `create_style` makes a combo with `parent_style_names`. Never type in the Designer without a focused field: letters fire shortcuts (C opens comments) |
| 2 Oct 2026 | Insights list + CMS colours | Collection List settings by API: `source` static_json {"collectionId"}, `limit` static_number, `pagination` static_json {"itemsPerPage":6}, `filters` static_json [{"fieldSlug":"featured","operator":"isOn"}] (booleans take isOn / isOff). Option field choices can be added only in the CMS settings UI. Page-level CMS prop bindings work by API, including a reference sub-field as "refFieldId:::subFieldId"; links to the item page and anything inside a component definition need the Designer. Attributes can bind to props: `{"name_static":"data-colour","value_binding":{"source_type":"prop","prop_id":...}}`. Finsweet v2 list: published HTML omits w-dyn-empty when items exist, so add a custom `fs-list-element="empty"`; test pages need a `Webflow.push` shim or the list module never starts |
| 2 Oct 2026 | Blog template | Rich text binds with settings key `richText` (not `text`). A nested list on a template takes source static_json {"collectionId","fieldId"} for a multi-reference; the read-back shows only collectionId but the list renders the item's references. System dates (Published On) bind only in the Designer, where the date format is set. `transform_element_to_component` takes `id`, not `element_id`. Inserting relative to a component instance is rejected: append to its parent. A collection's template page cannot be deleted; set it to draft |
| 2 Oct 2026 | Blog section | `transform_element_to_component` refuses a section holding a bound Collection List, and a source cannot be cleared by API: build the section without the list, convert, then add `CMSCollection` inside the definition (`data_element_builder` with `scope_component_id`), set `source` (`static_json {"collectionId"}`) and `limit` (`static_number`). Card props inside it still bind to CMS fields only in the Designer (purple dot > Connect > collection field; Link > URL Path). The "suggested props" Review button creates section props, not CMS bindings. IX3 targets inside the hovered element: `filterContext.relationship: "within"` with `filterBy: ["wf:trigger-only", ""]`. CMS image fields take `{fileId, url}` and copy the file into the CMS |
| 2 Oct 2026 | Newsletter section | An image prop has no default through the API (`update_prop` takes no image key): set it in the Designer (bound field > Edit settings > Default Image). Instance image values go in as `type: "string"` with the asset id. Image bindings use `set_settings` keys `assetId` and `altText` with `binding`. FormButton text is the `buttonText` setting. The form State switch (Normal / Success / Error) in Form settings previews the messages in the canvas. A right-edge bleed inside a centred container: `margin-right: calc((100% - 100vw) / 2)` on the flex item, section `overflow: hidden` |
| 2 Oct 2026 | Animated CTA pile | `data_element_builder` builds inside a component definition when the action carries `scope_component_id` (without it: "Parent element not found"). Many same-size art pieces at fixed spots: export each as a full-frame SVG (same viewBox) stacked with one class, so no per-piece position classes; give the viewBox spare room past every clip edge (the SVG box clips its own content, so a moving piece shows a flat cut otherwise) and let the card's overflow do the clipping; only hoverable pieces get positioned combos. Drop (`y`) and parallax (`yPercent`) compose on one element; hover rotation and scroll rotation do not, so put one on a wrapper. IX3 rejects `timing.delay` on an action: use `timing.position`; stagger `from: "random"` is accepted. In the Designer, Shift+P opens the Publish dialog, not Preview: use the Preview button. Claude in Chrome input (scroll, click, keys) never reaches the Preview frame, so Preview checks are the person's job |
| 1 Oct 2026 | CTA and accordion | `set_style_variable_mode` accepts `variant_id`: apply the Theme Dark mode to a class inside one component variant and nested Buttons flip through their tokens. A Figma group export carries the parent card's drop-shadow `<filter>`s and canvas `<rect>`s: strip both before svgo or every shape gets a halo on light grounds. `width`/`height` are reserved image attributes in `set_settings`; `loading` is allowed. Prop binding through: `type: "bindable"`, `binding_source_type: "prop"`, `binding_prop_id`. Block elements cannot be `details`; use a DOM element with tag details/summary and `name` for one-open-at-a-time. Designer Preview is cross-origin and did not respond to scripted clicks, so check interactions there by hand or on staging |
| 1 Oct 2026 | Theme Light-mode updates all returned "internal error" with `mode_id: "base"`; Dark-mode updates in the same call went through | Omit `mode_id` to write the base mode; pass it only for named modes. On the MK-1 clone, `.button` was still bound to the starter `default` collection, so check the button classes' bindings on every clone. Variable order: the API has no reorder for variables, and delete-and-recreate does not control where a variable lands (a recreated `pink/200` came back first); order them by drag in the Variables panel. Renaming a variable changes its compiled CSS name, so check embeds before renaming. A `TextBlock` built through `data_element_builder` ignores `set_text` and keeps "This is some text inside of a div block.", and `set_text` later fails ("doesn't support text"); write it with `data_element_settings_tool` > `set_settings` key `text` (`static_text.value`), then query the page for the placeholder string |
| 1 Oct 2026 | Font upload through the MCP | `data_fonts_tool` > `create_font` (md5 of the file, family, weight, `font_display: swap`) returns a presigned S3 POST valid 15 min; send every `upload.fields` entry as a multipart field, then the file as `file` (curl `-F`), expect 201, then curl the `hostedUrl` and `list_fonts` to confirm. Upload static WOFF2 per weight the design uses, cut from variable TTFs with fontTools `instancer` |
| 1 Oct 2026 | Navbar build | `data_element_builder` refuses `creation_position: after` a component instance ("Cannot insert elements directly into a component instance"): anchor `before` the next sibling. A combo named `w--current` compiles to `._w--current` and never matches; style the current state in the Global Styles embed. `row-gap` will not bind a variable through `create_style`; `grid-row-gap` does. The Designer canvas never adds `w--current`, so the active-page state is checked on staging |
| 1 Oct 2026 | Footer hover | An IX3 hover built in the split form (two `wf:hover` triggers with `assignedGroupId`) only accepts `control: play`, so it plays once and never again. For a fluid, replayable hover use one timeline with both triggers on the same `assignedGroupId`: enter `play`, leave `reverseFlipEase` (a single group allows any control), so leaving mid-hover reverses from where it is |
| 1 Oct 2026 | Footer build | `placeholder` is a reserved attribute and not an API setting on form inputs: set it in the Designer's input settings. A `Form` built by the API arrives with Name and Email fields, labels and Webflow's own messages: trim them and label the messages as placeholders. Builder `set_text` on a `TextBlock` is ignored (links take it): set `text` with `set_settings`. Component variant styles (`set_variant_styles`) handle Light / Dark swaps, including `display` swaps and `filter`; a pseudo (placeholder) cannot be read back |
| 1 Oct 2026 | Button fill hover in the class | The style API turns a `background-image` gradient containing `var()` into a bare variable reference (renders nothing). The Designer's Custom properties panel does not offer `background-image` (or other properties with a native control), and an API-set `transition` string is live CSS but does not appear in the Transitions section. So a hover that should stay editable in the Designer is built with the native controls: Backgrounds layer (gradient stops can take variable swatches) and Transitions entries; the API sets only plain values and hover colours. Driving the style panel through Claude in Chrome failed (the panel would not scroll) |
| 30 Sep 2026 | MK-1 live check: the link setting's `rel` published a stray `<link rel="noopener">` element after the button, and the rebuilt hero's eyebrow sat under the fixed nav at 768 and 390 | Put `rel="noopener"` in custom attributes, never in the link setting's `rel`; a hero under a fixed nav takes `padding-top` bound to `navbar/height` so the overlap lands on padding. Measure nav bottom against the first content top at every width |
| 2 Oct 2026 | Asset upload 403 AccessDenied | `create_asset` returns `uploadDetails` in camelCase; S3 needs the real names: `xAmzAlgorithm` -> `X-Amz-Algorithm`, `xAmzCredential`, `xAmzDate`, `xAmzSignature` likewise, `successActionStatus` -> `success_action_status`, `contentType` -> `Content-Type`, `cacheControl` -> `Cache-Control`; file last. Many images in one `data_element_builder` call hit 429 (one asset GET per image): build the skeleton, then add images in batches of about 8 |
| 2 Oct 2026 | Mouse-move parallax without IX2 | IX3 `wf:mouse-move` trigger targeting the section (`wf:inst`), `config.pluginConfig.smoothness`, two timelines with `triggerMetadata.role` `mouseX` / `mouseY` and `canvasDuration: 1`, FromTo `x` / `y` px pairs per depth layer. Scroll parallax on the same layers uses `yPercent`, so the two never fight. `dont-animate` (not skip-to-end) for reduced motion and small/tiny |
| 2 Oct 2026 | Slotted cards stacked in one column | A `ComponentSlot` renders as its own div, so a grid parent sees one child. Give the slot a class with `display: contents` (`set_style` on the slot in the definition); the slotted items then become the grid's items. Fill slots with `data_component_builder` `insert_in_slot`; a section instance gets a new id after `transform_element_to_component`, so re-query it (`query_elements` with `component_filter`) |
| 2 Oct 2026 | Optional parts of a reusable card | Boolean props (`create_prop` type `boolean`) bind to an element's `visibility` setting, but not on a nested component instance ("Element does not support setSettings"): wrap the instance in a classed div and bind the div. `move_element` cannot anchor after a component instance; anchor on a plain sibling and move the instance instead. `get_variant_styles` reads back only the base breakpoint, so check a variant's breakpoint styles in the canvas |
| 2 Oct 2026 | Count-up numbers | IX3 animates transforms, styles and variables, not text, so a count-up is one of the few jobs for a Global Scripts block: mark the number with `data-count-up`, parse its own text (keep prefix, suffix, commas, decimals), set 0 only when JS runs, count on IntersectionObserver, skip under reduced motion. Read the embed's code with `get_settings` type `all_raw_settings`, append, write back the whole string, read back to confirm |
| 2 Oct 2026 | Map tabs | Native Tabs build through the API (builder type `Tabs` gives wrapper, menu, 3 links, content, 3 panes; tab links can hold a component). Default tab, easing and fades are Designer-only (Tabs settings). Tab links have no Current state in the Designer states list and the style API saves `w--current` as `_w--current`, so style the active tab with one Global Styles rule on `.your-tab.w--current` |
| 2 Oct 2026 | Reordering a page full of section instances | `move_element` refuses before/after anchors on a component instance, but `creation_position: append` with the main wrapper as anchor moves anything (instances included) to the end, so append the sections in the target order and read the order back |

## Pointers
Memory files `webflow-build-conventions.md` (the long version of every gotcha above),
`webflow-two-accounts.md`, `gsh-webflow-project.md`, `gsh-px-over-rem.md`. Skills: editable masters `skills/webflow-ui-design/` and `skills/webflow-agent-instructions/`
(synced twins carry the `anthropic-skills:` prefix), plus `design-compilation/`, `pre-launch-checklist/` and `page-quality-auditor/`. Webflow's official skills, only the nine that do not contradict the standards, are vendored as `skills/webflow-official-*` (29 Sep 2026; list and exclusions in `skills/README.md`). The kit and this playbook win over them.
