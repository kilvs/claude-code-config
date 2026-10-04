# Accessibility

- Every interactive element has a **visible focus state**. Never remove outlines without an equal-or-better `:focus-visible` replacement.
- Colour contrast meets WCAG AA — 4.5:1 for body text, 3:1 for large text and UI components. Enforce at the Theme token level: check token pairings once, inherit everywhere. Never convey meaning by colour alone.
- Everything is keyboard-operable: nav dropdowns, accordions, tabs, sliders, and modals work with Tab / Enter / Escape, with a logical tab order and no focus traps. Modals return focus to their trigger on close.
- Interactive elements are real `<button>`s and `<a>`s — never click-handlered divs.
- Icon-only buttons and links carry an `aria-label`; purely decorative icons are `aria-hidden`.
- Include a skip-to-content link for keyboard users.
- Tap targets ≥ 44×44px (responsive-quality rule) and `prefers-reduced-motion` (animation rule) apply here too — accessibility failures in those areas are failures of this rule as well.
