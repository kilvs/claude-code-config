---
name: webflow-agent-instructions
description: Deploy and manage the standard Webflow agent-instruction kit (Client-First rules + skills) on any Webflow site via the Webflow MCP connector. Runs automatically, without being asked, at the start of every Webflow project (a new or cloned site, or the first session on a site whose Instructions panel lacks the kit). Also use whenever the user asks to set up agent instructions, add skills or rules to a Webflow site, deploy the Client-First instruction set to a new client site, customize instruction placeholders, or update/extend existing site instructions. Covers the bundled template (5 skills + 13 rules), placeholder filling, per-site configuration, MCP deployment mechanics (create/update, required kind field, the script-tag 406 workaround), zip import, Shared Library distribution, and the post-deploy checklist (variable collections, reference tokens, IX3 presets, state helper, test build).
---

## Changes

- 30 Sep 2026: the state helper is nav-only (accordions and tabs left the standard) and now uses the section 3 attribute names `data-nav-toggle` / `data-nav-panel`; the old copy looked for `data-nav-item` / `data-nav-trigger` and could never find a nav. New lines: never animate the LCP element, image classes `object-fit: contain` with an `is-cover` combo for photos (links-and-media rule), the Password page exception for the global components (builder section 9), Primitives manual modes in builder section 8. Stack README helper line fixed.
- 30 Sep 2026: full kit (13 rules, 5 skills, en-AU) deployed to Client First MK-1, the template, not the "- Test" copy. Stale lines fixed first: the animation rule no longer lists `data-accordion` / `data-tabs` as behaviours, interactions sections 4 and 6 drop the accordion examples, the variables description and builder section 8 say the Animation collection is the table IX3 presets are authored to (not "read by the GSAP script"), and the duplicated "body tag refuses the manual modes" bullet in variables is merged into one.
- 29 Sep 2026 (official skills check): loops (action-level `repeat`/`yoyo`) and a stagger on the trigger's children (`filterBy: ["wf:trigger-only", ""]`) are accepted by the API, pending a Preview to prove playback; interactions frontmatter and section 3 no longer mention accordions/tabs or a footer helper.
- 29 Sep 2026: interactions skill gains cursor effects on the native Mouse Move trigger (section 5a, never a pointer script), animated variables (`wf:variable`, section 7), component-scope and Set-action class toggle notes (section 5), and the API re-test results for loops and stagger (section 2). The section 9 example no longer uses `:not()`, which contradicted the plain-selector rule.
- 29 Sep 2026: the slider kit now matches the kit's own rules. The named-config and `slider:ready` examples run inside the `Webflow.push` ready gate; no `console.log` in examples; no hex in the Designer example; arrows are real `button` elements with `aria-label` (swiper-slider skill, sliders rule); `window.Slider` and `window.SliderConfig` are named as the only allowed globals beside `window.Webflow` (builder section 14, performance rule).
- 29 Sep 2026: new `webflow-skills/swiper-slider.md` and `rules/sliders.md`. Every slider is Swiper 14 through `data-swiper-element` roles, layout in Designer classes (`slidesPerView: 'auto'`), one kit script in Global Scripts with `data-swiper-*` attributes, named configs (`window.SliderConfig`), grid-to-slider by class and a `Slider` API. Tested on staging (Sample Slider Test 51, docs page `/slider-docs`). The kit CSS banner for Swiper's own classes is `SLIDER (SWIPER): RUNTIME CLASSES`, not state classes. Swiper code in the skill has no raw script tags (406).
- 29 Sep 2026: Site Settings holds third-party code only (gtag, CDN libraries such as Lenis and Swiper); Global Scripts holds the scripts we write. Embed scripts run inline before jQuery, `webflow.js`, GSAP and the footer libraries, so every script we write runs inside the `Webflow.push` ready gate (builder section 14, rules/performance.md).
- 29 Sep 2026: the kit auto-deploys at project start (Workflow step 0). Components are built slot-ready with group, description, prop tooltips and Navigator display names (rules/components.md, rules/naming.md, builder section 12). Every SVG is assessed: animated inside → Custom Element, static → SVG image (rules/animation.md, builder section 13). Section scripts go in a `section-script` Code Embed, `display: none`, ES6, lightweight (rules/performance.md, builder section 14). Not yet deployed to any site.
- 22 Sep 2026 (rounds five to seven): motion is native IX3, not custom-code GSAP. `gsap-animation.md` moved to `interactions.md`: site-scoped presets targeted by `data-animate`, nav in the panel, an exclusive-group helper that emits `wf:custom` events, playback rules, Animation collection kept as the timing table.
- 22 Sep 2026 (rounds three and four): breakpoints (base + 991/767/479 only, contained ultrawide, `container-semi-full` and `container-full`), utilities all token-bound, section padding at Client-First 3/5/7rem (designer uses Relume templates), Components for anything repeated with variants instead of `is-*`, Global Styles embeds per concern. New `rules/components.md`.
- 22 Sep 2026: variables standard decided by questionnaire: seven collections, slash groups, breakpoint modes on Typography/Spacing/Layout, Light+Dark on Theme, Animation tokens read by GSAP, 13-step spacer scale. New `variables.md` Webflow skill; builder §8, sizing, naming and gsap files updated to match. Guinea-pig site, not yet built.
- 22 Sep 2026: editable master moved to `~/Documents/AI Agent Config/skills/`. Synced claude.ai copy is the published twin; re-upload after improvements.

# Webflow Agent Instructions — Deploy Kit

This skill deploys a proven, site-agnostic instruction set into any Webflow site's **Instructions panel** (Skills + Rules for AI agents). The kit lives in `template/` and encodes the user's Client-First dialect, token system, GSAP-first motion, and quality rules.

**Kit contents** (`template/`):
- `webflow-skills/` — one file per Webflow skill: `client-first-builder.md` (build playbook) · `variables.md` (the seven-collection token system, decided 22 Sep 2026) · `interactions.md` (IX3 motion: presets, behaviours, state helper, MCP authoring) · `pre-launch-checklist.md` (launch sweep) · `swiper-slider.md` (the slider kit: install code, roles, settings, breakpoints, grid-to-slider, API, MCP recipe). Each file's frontmatter holds the Webflow `description`; the body is the markdown. On Webflow they deploy to path `<name>/SKILL.md`.
- `rules/` — `naming` · `sizing-and-tokens` · `core-structure` · `edit-safety` · `links-and-media` · `seo-essentials` · `animation` · `responsive-quality` · `performance` · `accessibility` · `forms` · `components` · `sliders`
- `README.md` — human-facing deploy guide (hand it over when exporting the kit standalone)

Rules are read before every agent action → keep every rule short and absolute. Skills are referenced when relevant → long-form teaching goes there. Never bloat a rule; extend the matching skill instead.

## Workflow

### 0. Auto-deploy at project start

The user's standing word: "add the skill and rule automatically on the webflow instructions once the project is started." No need to ask first.
- **When:** a Webflow site is created or cloned for a project, or the first session on any site that has no kit (`search_instructions` shows none of the kit's rules or skills).
- **What:** run steps 1 to 4 below. Fill the placeholders from the client card in `~/Documents/AI Agent Config/work/<org>/` or the project `CLAUDE.md`. Ask only for what neither source gives, then deploy.
- **Old-nest sites:** a site built before 29 Sep 2026 uses `padding-global > container > padding-section`. Deploy with the core-structure rule and builder section 3 set to that order, so the kit matches the site. Never migrate it.
- **Missing files** are created. Kit files already on the site that differ from `template/` are **not** overwritten: list the differences and ask, because per-site overrides may be deliberate.
- **Report** what was deployed (paths, `isDraft: false`) and log it in the project records. This covers the Instructions panel only; it is never a site publish.

### 1. Gather per-site inputs

Ask only for what's missing:
- **Site ID**.
- **Locale**: `{{SITE_LOCALE}}` / `{{LANG_CODE}}` / `{{SPELLING_VARIANT}}`. For Australian sites: `English (Australia)` / `en-AU` / `Australian English (colour, organise, centre)`.
- **Owner wording**: the template says "the site owner"; replace with a name if the user wants.
- **Per-site overrides** (all optional; template defaults are sensible): Primitives ramp names (rename `brand`/`accent` to the real hue, descriptive never role-based), units, container widths (80/64/48rem), section padding values, spam-protection standard (Turnstile/reCAPTCHA/honeypot), breakpoint list, schema types actually needed.

### 2. Fill placeholders

Search the template content for `{{` and replace all three placeholder tokens (they appear in `rules/seo-essentials.md` and `webflow-skills/pre-launch-checklist.md`). Apply any per-site overrides to the relevant files. Never deploy with an unfilled `{{...}}`.

### 3. Check existing state

`Webflow:data_agent_instructions_tool` → `search_instructions` with the site_id first. If a path already exists, use `update_instruction` for it (creates on an existing path fail). Leave unrelated pre-existing instructions untouched unless asked.

### 4. Deploy via MCP

Use `Webflow:data_agent_instructions_tool` with batched `actions`:
- **Rules** → `create_instruction` / `update_instruction` with `kind: "rule"`, path `rules/<name>.md`, markdown = file content.
- **Skills** → source `template/webflow-skills/<name>.md`; deploy with `kind: "skill"`, path `<name>/SKILL.md` (e.g. `client-first-builder/SKILL.md`). Pass the source file's frontmatter `description` as the `description` param and the **body without frontmatter** as `markdown`.
- `kind` is REQUIRED on both create and update.
- ⚠ **Raw `<script>` tags in markdown → HTTP 406.** Keep all code as fenced ```js blocks with loading instructions in prose (the interactions template is already formatted this way — keep it that way).
- The whole batched call validates together: a schema error anywhere means nothing ran. On partial failures, re-send only the failed actions.
- Verify the results report `isDraft: false` and echo the stored markdown.

### 5. Post-deploy checklist

1. Verify rendering in the Instructions panel (tables and code fences, especially in the builder, variables and interactions skills).
2. Build the seven variable collections — Primitives, Theme, Typography, Spacing, Layout, Animation, Components (full spec and MCP build order in the `variables` skill) — then insert **reference tokens** in the panel editor pointing at the live collections.
3. Create the IX3 presets through `data_interactions_tool` from the `interactions` skill section 9, add the state helper (section 8) to the Global Scripts component, and verify on staging that attribute-targeted scroll triggers, custom-event selectors and the loop presets actually play.
4. Test build: fresh agent session → "build a test section" → verify `section-[page]_[element] > padding-section-* > padding-global > container-* > _content`, token bindings, image width/height + loading attributes.
5. Once CMS collections exist: author the CMS guidelines skill against the live CMS (architecture, standard field set, Rich Text rules, reference patterns, designed empty states, editor experience, draft-only workflow).

### Alternative deploy paths

- **Zip import**: rebuild Webflow's import layout first — `skills/<name>/SKILL.md` (from each `webflow-skills/<name>.md`, frontmatter kept) plus `rules/*.md` — then zip those two folders only (no README) for the Instructions panel's import button. Only `.md`/`.mdc` accepted.
- **Shared Library**: deploy once, push the set to a Workspace Shared Library so all sites install and receive updates centrally.

## Maintaining the kit

When the user adds or changes a rule/skill mid-project: update the **site** via MCP, and ask whether the change is universal — if yes, update `template/` in this skill too so the next deployment inherits it. A change to the base builder, naming or core-structure file goes into the matching copy under `template/orgs/<org>/` as well, unless it is about naming. Keep the deployed site set and this template from silently drifting apart.

**MK-1 tracks the template**. Client First MK-1 is the clone source, so every template change is deployed to MK-1 in the same task, then read back.

**No person names in deployed files**. Rules and skills on a site carry dates and reasons, never who asked (`(8 Oct 2026)`, not ``). Attribution goes in this Changes log and the project records only.

Never publish a Webflow site. Agents stage, report, and hand the publish decision to the site owner — that law is inside the kit (edit-safety) and applies to this skill's own actions too.
