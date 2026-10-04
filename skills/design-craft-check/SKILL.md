---
name: design-craft-check
description: "Keep web mocks from looking AI-generated: a plan-then-review pass before building and a Refuse / Prefer / Verify checklist after. Use before and after designing any page, section or component mock: claude.ai Artifact pages, static HTML preview repos (Vercel), Claude Design canvases, and every version in design-compilation or webflow-ui-design. Also use for a 'too loud', 'too plain', 'looks like AI', 'generic' or 'robotic' feedback round. The client's brief, brand guide and the org's standards always win over this list."
---

## Changes

- 29 Sep 2026: new. Built from two Apache 2.0 sources, both modified:
  Anthropic's `frontend-design` (github.com/anthropics/skills, commit 8a1541c; the AI-default
  clusters and the plan-then-review pass) and Paul Bakaus's `impeccable` (github.com/pbakaus/
  impeccable, commit 114ea1d; `craft-floor.md` Refuse and Verify lists, `quieter.md`). Dropped
  their copywriting guidance (the client owns every word), "take aesthetic risk", "cards are
  the lazy container" and "reach past transform and opacity". Added the user's liked patterns.
  Licences in `LICENSE-frontend-design.txt` and `LICENSE-impeccable.txt`.

# Design craft check

**Authority, highest first:** the client's own words and brand guide, the standards of the org
you are working under (`work/<org>/`), the project `CLAUDE.md`, then this list. Where the brief asks for something on the Refuse list, build it.

**Words are never ours.** Build copy verbatim. Missing copy is a visible labelled placeholder
(`[PLACEHOLDER: hero subline]`), never an invented line, name, number or claim. That holds
inside graphics and mock UI too.

## Pass 1: plan, then review the plan

Before any markup, write a short plan:
- **Colour:** 4 to 6 named hex values, all from the brand, mapped to token roles.
- **Type:** the brand guide's faces and weights only, with their roles and a clear scale.
- **Layout:** one sentence per section plus a small ASCII wireframe; say what is centred and
  what is left-aligned.
- **The one idea:** the single memorable thing on this page. Everything else stays quiet.

Then review it: would you have produced this plan for any similar page? Where the answer is
yes, revise that part and say what changed and why. Only then build.

## Refuse (unless the brief asks)

Page scaffolds:
- An eyebrow or kicker label above headings. Uppercase tracked labels generally.
- Section numerals (01 / 02 / 03) unless the content is a real sequence.
- Identical icon + heading + text cards as the whole page structure; nested cards.
- The hero-metric template: big number, small label, stat row, gradient accent.
- One word in a headline set apart by colour, italic or weight.
- Duplicated CTA bands; dead white space; cut-off backgrounds.

Surfaces:
- 1px grey frames around images, full-bleed hairline rules, ruled ledger frames, chamfers.
- One radius and one grey `rgba(0,0,0,.1)` shadow on everything.
- Glassmorphism and blur as decoration; gradient text; blobs; film grain; stripe or grid
  backgrounds with no subject reason.
- Coloured `border-left` stripes on cards, callouts or list items.
- Hard offset shadows (`4px 4px 0`) and zero-offset coloured glows.
- Monospace as a "technical" costume; three competing type styles.
- Emoji or Unicode glyphs as icons. Icons come from one real set, one stroke weight.
- Decorative marks with no job (an arrow or bar that invites "why is that there?").
- Colour used as the status itself so every row shouts.

AI-default looks to avoid when the brief leaves the axis free:
- Cream background (near `#F4F1EA`) with a serif display and a terracotta accent (near
  `#D97757`).
- Near-black with one acid-green or vermilion accent.
- Broadsheet layout: hairline rules, zero radius, dense columns.
- Meta strings joined with middle dots; `→` appended to every link and button; `#111` for black.

Motion:
- The same fade-up on every section, hover transitions on every card, marquees, ambient
  animated backgrounds, bounce and elastic eases.

## Prefer (when the brief leaves it open)

- **Cards that feel designed, never flat white:** a light gradient between two brand tints,
  and shadows tinted with the brand's dark hue, with a real offset and a soft blur.
- **Contrasting section grounds:** no two neighbours alike, never two saturated grounds
  touching, back to a light ground in between. Warmth, if any, stays subtle.
- **Graphics built in HTML and CSS** (or one SVG) instead of raster placeholders. Follow a
  supplied reference exactly.
- **Calm mock UI that reads as real:** white rounded rows on a tinted tray, initials badges,
  soft status pills with the colour behind the label, one typeface in sentence case. Sample
  names and figures are placeholders; list them as client flags.
- **Restrained motion:** one authored moment. A pulse or ring on the active or hovered item,
  idle items still, slow (about 2.4s loops).
- **Alignment:** centred section headers and grid CTAs; split sections stay left; strip items
  left-aligned on one top line.
- **Legibility:** larger supporting text, tight spacing to the CTA, strong contrast on small
  lines.

## Verify (on the built result, in the browser)

- **Contrast:** body text at least 4.5:1, large text 3:1, quoted as ratios. On a coloured
  ground, tint secondary text from that hue, never grey.
- **Type:** body measure about 65 to 75 characters; `text-wrap: balance` on headings, `pretty`
  on paragraphs; no orphans from 360 to 1440.
- **Spacing:** tight groups, generous separation, more space above a heading than below.
- **Widths:** 1440, 1100, 992, 768 and 390 with no horizontal overflow.
- **States:** hover, focus-visible rings, disabled, empty and error where they exist.
- **Browser surfaces:** text selection colour, focus ring colour and link underline offset come
  from the palette, not browser defaults.
- **Accessibility:** one h1, a skip link on full pages, tap targets of at least 44px,
  `role="img"` and `aria-label` on built graphics, reduced motion respected.
- **Coverage:** every item in the brief is on the page and findable in seconds.
- **The mirror test:** remove one thing before calling it done.

## When feedback says "too loud"

Reduce intensity without going generic:
- Desaturate the palette a step and use fewer colours; neutrals do more work.
- Drop weights where the brand allows; build hierarchy with size and space instead.
- Remove decoration that has no job: extra shadows, gradients, glows, patterns.
- Shorten motion distances (10 to 24px), gentler ease-out, never bounce.
- Keep the anchors: hierarchy, one accent, the page's one idea.

"Too plain" is the opposite round: add depth (the designed cards, tinted shadows, contrasting
grounds), not decoration.

## Where it applies

- **Artifact pages:** use alongside the `artifact-design` skill; tokens live on `:root` with
  dark-mode overrides.
- **Preview repos:** Client-First classes and tokens, per `webflow-ui-design`.
- **Claude Design:** where this skill can't be loaded, paste the Refuse and Prefer lists into
  the design system's notes or the project prompt.
- **design-compilation:** run Pass 1 on each version and Verify on the batch.
