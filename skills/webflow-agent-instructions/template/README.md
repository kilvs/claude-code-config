# Webflow Agent Instructions — Template Kit

A portable, site-agnostic instruction set for Webflow's AI agent Instructions panel: **5 skills + 13 rules** encoding a Client-First (custom dialect) build system. Deploy to any Webflow site so every agent (Webflow AI Assistant, Claude via MCP, Cursor, etc.) builds to the same standard.

```
webflow-skills/
  client-first-builder.md    ← the build playbook (naming, structure, tokens, decision trees)
  variables.md               ← the token system (seven collections, modes, MCP build order)
  interactions.md            ← motion system (native IX3 presets via data-animate, behaviours, state helper, MCP authoring)
  pre-launch-checklist.md    ← final sweep + post-launch steps, report format
  swiper-slider.md           ← the slider kit (Swiper 14 via data-swiper-element roles, install code, settings, grid-to-slider, API, MCP recipe)
rules/
  naming.md              sizing-and-tokens.md    core-structure.md
  edit-safety.md         links-and-media.md      seo-essentials.md
  animation.md           responsive-quality.md   performance.md
  accessibility.md       forms.md                components.md
  sliders.md
```
Each `webflow-skills/*.md` deploys to the Webflow path `<name>/SKILL.md`; its frontmatter `description` becomes the skill description.

Rules are read before every agent action (keep them short and absolute). Skills are referenced when relevant to the task.

---

## 1. Placeholders — must be filled per site

Search the kit for `{{` and replace:

| Placeholder | Meaning | Example |
|---|---|---|
| `{{SITE_LOCALE}}` | The Webflow primary locale | `English (Australia)` |
| `{{LANG_CODE}}` | The lang attribute it renders | `en-AU` |
| `{{SPELLING_VARIANT}}` | Spelling standard for all copy | `Australian English (colour, organise, centre)` |

"The site owner" appears wherever approval/publishing authority is referenced (token proposals, publish decisions, sign-offs). Optionally replace with a person's name per site.

## 2. Per-site review (defaults are sensible; confirm or adjust)

- **Primitives ramp names** (`colour/brand-50…900`, `colour/accent-50…900` are placeholders) → rename to the actual hues (`navy`, `sand`). Keep them descriptive (what the colour *is*), never role-based.
- **Container widths** — defaults `container-large/medium/small` = 80/64/48rem.
- **Spacer scale** — Primitives `spacer/xxtiny` 0.125rem → `xxhuge` 12rem, 13 steps (stepped rem + Variable Modes per breakpoint; a fluid `clamp()` backdoor is documented in the builder skill appendix, off by default).
- **Units** — rem by default; px when the client asks for it (same names, same structure).
- **Section padding** — `padding-section-small/medium/large` values.
- **Spam protection standard** — Turnstile / reCAPTCHA / honeypot (forms rule says "per project standard"; pick one).
- **Schema types** — seo-essentials lists Organization/LocalBusiness + per-type; trim to what the site actually needs.
- **Breakpoint list** in edit-safety (base + 1280/1440/1920 + tablet/landscape/portrait) — adjust if the project uses different large breakpoints.

## 3. Deploying

**Option A — via MCP (recommended).** Use the Webflow MCP `data_agent_instructions_tool` with the target `site_id`:
- Rules → `create_instruction` with `kind: "rule"`, path `rules/<name>.md`.
- Skills → `kind: "skill"`, path `<skill-name>/SKILL.md`. Pass the SKILL.md frontmatter `description` as the `description` param and the body (without frontmatter) as `markdown`.
- ⚠ Webflow's API rejects raw `<script>` tags in instruction markdown (HTTP 406). Keep code as fenced ```js blocks with loading instructions in prose (the interactions skill is already formatted this way).

**Option B — zip import.** Rebuild the import layout first — `skills/<name>/SKILL.md` from each `webflow-skills/<name>.md` (frontmatter kept) plus `rules/*.md` — then zip only those two folders (exclude this README) for the Instructions panel's import button. Only `.md`/`.mdc` files are accepted.

**Option C — Shared Library.** Deploy once, then push the instruction set to a Workspace Shared Library so every site installs and receives updates from one place.

## 4. After deploying

1. Open the Instructions panel and verify tables/code blocks rendered cleanly.
2. Build the seven variable collections (Primitives, Theme, Typography, Spacing, Layout, Animation, Components; spec and MCP build order in the `variables` skill), then use the panel editor to insert **reference tokens** pointing at the live collections in the builder skill's variables section.
3. Create the IX3 presets through the interactions MCP tool (interactions skill §9) and add the state helper (§8) to the Global Scripts component; verify on staging.
4. Test: fresh agent session → "build a test section" → verify it produces `section-[page]_[element] > padding-section-* > padding-global > container-* > …` with token bindings and correct image attributes.
5. When collections exist, author the CMS guidelines skill against the live CMS (architecture, standard field set, Rich Text rules, reference patterns, empty states, editor experience).

## Design principles baked in

- One naming dialect: `section-[page]_[element]` wrappers · `[page]_[element]_[tag]` customs (`_description` for paragraphs) · `component_[name]_[tag]` · hyphen-only utilities · Component variants (`is-*` combos only on non-component classes).
- Tokens over values: semantic Theme bindings, primitives never bound, no hardcoded hex/px.
- Native IX3 motion, preset-driven through `data-animate`, reduced-motion rules and fail-visible mandatory; no custom-code tweens.
- Performance and CLS discipline: WebP everywhere (incl. CMS uploads), width/height attributes, eager+fetchpriority hero / lazy below fold.
- Component-ready builds: repeating blocks become Components with slots, a plain-language description, prop tooltips and Navigator display names, so clients are guided.
- Every SVG is assessed: animated inside → Custom Element, static → uploaded SVG image.
- Code embeds: CSS in the Global Styles component, JS in the Global Scripts component, each under comment banners; section-only code in `section-script-css` / `section-script-js` embeds; all `display: none`, ES6, lightweight, state only.
- One slider system: Swiper 14 through role attributes, layout owned by Designer classes, one kit script in Global Scripts.
- Agents never publish — they stage, report, and hand off.
