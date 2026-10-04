# Critique Checklist

A rubric for reviewing an existing design (a screenshot, a live URL, a Webflow project, or a mockup). Use it two ways: to critique others' work, and to self-check this skill's own output before delivering. Be specific and actionable — point to *what* and *how to fix*, not just "needs work."

When critiquing, organize feedback by severity: **blockers** (breaks usability/accessibility/build), **improvements** (clear wins), **polish** (nice-to-have). Lead with what works before what doesn't.

## 1. Visual hierarchy
- Is there one clear focal point per view? Does the eye know where to go first?
- Does type hierarchy (size, weight, color) match content importance?
- Is the most important action (primary CTA) visually dominant over secondary ones?

## 2. Typography
- Coherent scale, or arbitrary sizes? (Should map to a `text-size-*` scale.)
- Body measure 60–75 chars, or full-bleed unreadable lines?
- Line height comfortable (~1.5 body, ~1.1–1.25 headings)?
- ≤2–3 weights and ≤2 families? More reads as inconsistent.
- Heading levels semantically correct (one H1, no skips), not chosen by looks?

## 3. Color & contrast
- Does body text meet WCAG AA (4.5:1; 3:1 for large)? Flag any failures explicitly — this is a blocker.
- Is color used purposefully (one brand accent doing the heavy lifting) or scattered?
- **Are saturated colours used with restraint?** Full-saturation colour on large surfaces or as long-form text strains the eye. The most saturated colour should own one high-impact role (e.g. primary CTA); others should be sparse accents. If colours vibrate against each other or reading feels effortful, it needs toning — comfort is a requirement, not a nicety.
- Are tokens semantic (role-based) rather than color-named?
- Do interactive elements have visible hover/focus/active states?

## 4. Spacing & rhythm
- Consistent spacing scale, or random gaps?
- Enough breathing room — generous section padding, or cramped?
- Is related content grouped (proximity) and unrelated content separated?
- Aligned to a consistent grid/gutter?

## 5. Layout & responsiveness
- Is it genuinely responsive? Built desktop-base, but check it holds all the way down to mobile portrait (479px), not just desktop.
- Does the page have a complete header (logo, nav, primary CTA) and footer (links, social, contact, copyright, legal)? A page missing either reads as unfinished.
- Do touch targets meet ~44×44px minimum on mobile?
- Does the layout adapt sensibly at tablet/desktop, or just stretch?
- Is content width capped on large screens, or does it sprawl edge-to-edge?

## 6. Usability & UX
- Is the primary task obvious and frictionless?
- Are labels/CTAs clear and specific ("Get the quote" > "Submit")?
- Is feedback provided for states (loading, error, success, empty)?
- Is navigation predictable and consistent?

## 7. Accessibility (beyond contrast)
- Logical heading structure and landmark tags?
- Visible focus states for keyboard users?
- Alt text considered for meaningful images?
- Not relying on color alone to convey meaning (e.g. error = red + icon/text)?

## 8. Webflow / Client-First buildability
- Does the structure map to `section_* > padding-section-* > padding-global > container-*`?
- Are class names human-readable and Client-First, or cryptic (`div-block-12`)?
- Sizing in rem on the approved scale, or arbitrary px?
- Color via semantic variables, or hardcoded hex everywhere?
- Could another developer rebuild this from the structure alone?

## 9. Craft & intentionality
- Does it look considered, or like an untouched template default?
- Consistent corner radii, border treatments, shadow usage?
- Is imagery quality consistent and on-brand?
- Do the details (icon weight, button padding, alignment) hold up under zoom?

## Delivering the critique
1. One-line overall read.
2. What's working (2–4 specifics).
3. Blockers (with fixes).
4. Improvements (with fixes).
5. Polish (optional).
Keep each point concrete: name the element, the issue, and the change. Prose, not just a wall of checkboxes.
