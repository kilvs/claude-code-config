---
name: design-compilation
description: Generate 5–10+ genuinely distinct, on-brand design versions as Webflow-ready Client-First HTML/CSS/JS markup, filed into the design-references/designcompilation folder tree with a comparison gallery. Use this skill whenever the user asks for a design reference, design idea, design options, mockups, variations, concepts, or "show me some designs" for any page, section, element, widget, or component — hero, cards, forms, blurbs, pricing, testimonials, nav, footer, CTA, image treatments, video, canvas, anything visual. Also trigger when they say "give me more versions", "I'm not sold on these", or asks to redesign or explore alternatives for something. Even a casual "got any ideas for the hero?" counts.
---

## Changes

- 29 Sep 2026: the creativity standard now runs the `design-craft-check` skill (plan review per version, Refuse / Prefer / Verify) instead of pointing at `frontend-design`, which is not installed here.
- 22 Sep 2026: editable master moved to `~/Documents/AI Agent Config/skills/`. Synced claude.ai copy is the published twin; re-upload after improvements.

# Design Compilation

Generate multiple genuinely different design concepts for a target (a section, element, component, or full page), grounded in the project's real branding, output as Client-First markup that converts cleanly to Webflow via MCP. This is a design *exploration* tool: the deliverable is a set of options plus a gallery to compare them, not one final build.

**Non-negotiable: no slop.** Every version must be a deliberately designed concept, not a template permutation. See "Creativity standard" below — it is the heart of this skill.

## Workflow

### 1. Find the branding source (in priority order)

1. **Branding guidelines file** — look for an MD or PDF of brand guidelines in the project (search for files like `brand*`, `branding*`, `style-guide*`, `guidelines*`). This is the primary source.
2. **Local CSS / style guide files** — existing `tokens.css`, global styles, or a style guide page in the repo.
3. **Webflow variables via MCP** — if the Webflow connector is available, pull the site's variable collections (Base Colour, Theme, Spacing, Font Family, Typography, Layout).
4. **Ask the user** — if none of the above exist, ask them to paste or describe the branding. Never invent a brand.

Extract from the source: color palette (map to Theme token roles), font families and type scale, spacing scale, radii, container widths, and any stated brand personality (e.g. "bold and editorial", "clean and clinical"). Brand personality drives the creative direction of every version — a playful brand and a law firm should never receive the same ten concepts.

**Maintain a `_brief.md`** next to `_tokens.css` at the compilation root. It records what the guidelines *don't*: surface preference, brand personality in one line, known client dislikes, contrast findings (including any failing pairs in the brand sheet itself), and a short feedback log per round ("R1: client wants light surfaces; contrast tightened"). Read it at the start of every round and honor it — preferences stated once bind all future rounds.

**Inspiration references:** when the user or the client shares inspo (screenshots, site names, URLs), don't just admire it — distill each reference into 3–6 concrete, reusable attributes (type scale and weight, surface treatment, background texture/atmosphere, composition, CTA style, imagery approach) and record them in `_brief.md` under "Inspiration". Subsequent batches channel those attributes as a shared vocabulary while staying structurally distinct from each other — never clone any single reference, and never let all versions collapse into one look because the inspo shares one.

### 2. Establish or update the shared tokens file

All versions consume branding through CSS custom properties, never raw values. Maintain **one** `_tokens.css` at the compilation root: `design-references/designcompilation/_tokens.css`.

- Structure it to mirror the six Webflow variable collections so MCP conversion is 1:1. The full property list and naming is in `references/client-first-dialect.md` — read it before writing tokens.
- If `_tokens.css` already exists, reuse it; only update it if the branding source changed, and tell the user what changed.
- Versions may add *version-scoped* custom properties in their own `<style>` for concept-specific values, but core brand values always come from `_tokens.css`.

### 3. Resolve the identifier and output path

Determine what's being designed and name it in the site dialect (full rules in `references/client-first-dialect.md`):

| Target | Identifier example |
|---|---|
| Page section | `home_hero`, `about_team`, `pricing_plans` |
| Reusable component | `component_product-card`, `component_testimonial` |
| CMS template section | `template-blog_hero`, `template-case-study_header` |

Output path: `design-references/designcompilation/[Page Name]/[Section Name]/[Element Name]/`

- **Page Name** — the page it belongs to (`Home`, `About`, `Pricing`). For reusable components use `Components`; for CMS templates use `Templates`.
- **Section Name** — the section (`Hero`, `Team`, `Plans`).
- **Element Name** — the element type being explored (`Hero`, `Cards`, `Forms`, `Blurbs`, `Images`, `Video`, `Canvas`, etc.). When the target *is* the whole section, Element Name repeats the section type (e.g. `Home/Hero/Hero/`).

If the request is ambiguous about page or element, make the reasonable call and say what you assumed — don't interrogate the user over folder names.

### 4. Generate the versions

**Generate SVG assets when concepts call for them.** Versions are not limited to CSS-drawn visuals and placeholder images — create bespoke SVG artwork wherever it lifts a concept: abstract geometric compositions, line work, brand-motif derivatives (e.g. a logo's dot or angle turned into a pattern), textures, dot matrices, flow illustrations, decorative outlines, masked shapes. Rules:

- Shared, reusable assets live in `design-references/designcompilation/_assets/` as standalone `.svg` files (these upload to Webflow as-is); one-off art can be inline `<svg>` in the version.
- Color through the system: inline SVGs use `currentColor` or `var(--…)` tokens; standalone files use the Theme hex values with a comment noting the source token.
- Derive shapes from the brand's own geometry and motifs, not generic decoration — the banned-defaults list (blobs, etc.) applies to SVG art too.
- Purely decorative SVGs are `aria-hidden="true"`; meaningful ones get `role="img"` + `aria-label`. Keep files lean (no editor metadata, minimal path data).
- Photographic placeholders remain placehold.co, but prefer designed SVG art over placeholder photos whenever the concept doesn't genuinely need photography.

Default count: **5–10 per round**. Follow-up rounds continue the numbering — if 10 exist and they ask for more ideas, the next file is `11`, and existing files are **never renamed, renumbered, or overwritten**.

**File naming:** `NN-[identifier]-[concept-slug].html`

- `NN` — zero-padded sequence number, continuous across rounds (`01`–`09`, then `10`, `11`…).
- `[identifier]` — the dialect identifier from step 3 (`home_hero`, `component_product-card`, `template-blog_hero`).
- `[concept-slug]` — 2–4 hyphenated words naming the design concept (`split-editorial`, `stacked-marquee`, `asymmetric-grid`).

Example: `03-home_hero-split-editorial.html`

**Each version file is self-contained** (one HTML file with its own `<style>` and, when needed, `<script>`), except that it links the shared `../../../_tokens.css` first via a relative path. This keeps GitHub/Vercel previews working and gives Webflow MCP everything in one read.

Markup requirements per version — these make or break MCP conversion, so treat them as law:

- Full Client-First structure and naming per `references/client-first-dialect.md`: `section-[identifier]` wrapper → `padding-section-*` → `padding-global` → `container-*` → content (vertical padding outermost, 29 Sep 2026); `_list_wrap > _list > _item` for repeats; images in `_image_wrap`; every CTA inside `button-group`.
- All sizing in rem; all colors, spacing, type, radii via `var(--…)` tokens. No hardcoded hex, no px font sizes (1px borders excepted).
- Semantic HTML. Sections use `h2` for their heading. No skipped heading levels within the version.
- Accessibility floor: visible `:focus-visible` states, real `<button>`/`<a>` elements, `aria-label` on icon-only controls, `prefers-reduced-motion` guard around any animation.
- **Contrast is computed, never eyeballed.** Before generating, verify every text/background pairing the batch will use against WCAG AA (4.5:1 body, 3:1 large text and UI) — actually calculate the ratios. The usual offenders are accent-on-light and light-on-accent (bright brand accents like oranges/yellows almost never carry white text legally). If the brand sheet itself contains a failing pair, don't reproduce it: use the nearest compliant treatment (e.g. dark text on the accent, or a darkened accent shade added as a proposed token), and note the finding in `_brief.md` and the version's Webflow-notes comment so the user can raise it with the client.
- Keep JS vanilla and minimal — behavior demos only (a working tab, an accordion, a marquee). GSAP via CDN is allowed when the concept is motion-led; when used, gate it behind `prefers-reduced-motion` and keep the animation code in one clearly-commented block so it can be lifted into the site's data-attribute preset system later.
- Placeholder content must look real: plausible copy in the brand's voice, `https://placehold.co` images sized to the actual layout (never broken image links), realistic nav/label text. Lorem ipsum is banned.

**Version header comment.** Open every file with a comment block:

```html
<!--
  NN — Concept Name
  Direction: one sentence on the design idea and why it suits the brand.
  Layout: one line on the structural approach (grid, composition).
  Webflow notes: anything the MCP conversion should know (e.g. "marquee is a
  GSAP candidate", "cards map to a CMS Collection List").
-->
```

### 5. Build/refresh the gallery

After writing the versions, regenerate **one** `index.html` in the element folder (`…/[Element Name]/index.html`) containing every version in that folder — including ones from earlier rounds.

- Copy `assets/gallery-template.html` from this skill as the base and fill in the version list; don't hand-roll a new gallery design each time.
- **Embed, don't link.** Each version is inlined into its `<iframe>` via the `srcdoc` attribute (HTML-escaped), with the contents of `_tokens.css` substituted in place of the version's `<link>` tag. This makes `index.html` fully self-contained — it works double-clicked from anywhere, with no server and no `file://` iframe restrictions. Never generate the gallery with `src="file.html"` iframes; local-file security blocks them unpredictably.
- Each entry: the number + concept name as a heading, the one-line direction, the embedded frame (lazy-loaded, generous min-height, resizable), plus a plain "open file" link to the real file for tab-sized viewing when the tree is intact.
- The gallery lists versions in numeric order and is regenerated from the actual files on disk — never from memory — so late additions and the user's own deletions are always reflected.

### 6. Present and iterate

Tell the user: how many versions, one line per concept (number + name + hook), and the gallery path to open. Don't paste the markup into chat.

The loop is expected to continue. When they respond:

- **"More ideas" / "not sold"** — ask nothing unless direction is truly unclear; generate the next batch continuing the numbering, deliberately moving *away* from the rejected directions.
- **"More like #4"** — treat #4's direction as the axis and explore variations along it; still no near-duplicates.
- **"Combine 2 and 7"** — new numbered version, concept slug reflecting the merge.
- Never delete or modify existing versions unless they explicitly ask. Token-level fixes (e.g. a contrast correction) are the exception since `_tokens.css` is shared — apply them, and tell the user which existing versions they visually affect.
- After every feedback round, append one line to `_brief.md`'s feedback log capturing the direction ("liked 3's overlap, wants lighter surfaces, less gray text"). Future rounds start by reading it.

## Creativity standard

The reason this skill exists is that default AI output converges on the same centered-headline, three-card, gradient-blob layouts. Hold every batch to this standard:

1. **Run the `design-craft-check` skill.** Its Pass 1 (plan, then review the plan) applies to every version, and its Refuse, Prefer and Verify lists to the whole batch.
2. **Structurally varied batch.** Versions may share a family resemblance, but across the batch vary the fundamentals: symmetry vs asymmetry, grid density, type scale drama (oversized display type vs restrained), image treatment (full-bleed, framed, masked, none), light vs dark surface, whitespace philosophy, motion vs static. If two versions would look like siblings at thumbnail size, push one further apart.
3. **Every version has a defensible idea** — expressible in one sentence ("editorial split with an oversized serif numeral anchoring the copy column"). If the sentence is "a nice hero with a heading and image", it's slop; redesign it.
4. **On-brand is the boundary, not the ceiling.** Stay inside the tokens — but creativity lives in composition, scale, rhythm, and unexpected-but-appropriate choices, not in inventing new colors.
5. **At least one wildcard per batch** — a version that takes a real risk (unusual composition, bold type experiment, unexpected interaction). Label it as the wildcard in its direction line.
6. **Banned defaults** unless the user asks or the brand demands it: purple-to-blue gradients on dark, glassmorphism cards, identical three-column icon-blurb rows, centered-everything, floating blob shapes, emoji as icons.

## Reference files

- `references/client-first-dialect.md` — **read before generating markup.** The full naming dialect (section wrappers, identifiers, components, templates), the six token collections mapped to CSS custom property names, structure skeleton, and the button-group / list-chain laws.
- `assets/gallery-template.html` — the gallery base file for step 5.
