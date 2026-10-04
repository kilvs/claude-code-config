# Responsive quality

- **No horizontal overflow at any breakpoint, ever.** Nothing scrolls sideways. Check the usual culprits: wide grids and tables, embeds, marquees, absolutely-positioned decoration, negative margins. Fix the cause — `overflow: hidden` on a section is a last resort, not a solution.
- **Headings on mobile target a maximum of ~3 lines.** Fix by tightening the copy, stepping the heading size down through Variable Modes, or constraining width. If the heading genuinely can't fit in 3 lines after those fixes, exceeding the cap is acceptable — but never leave an orphan (a single word alone on the last line), and never shrink text below readable sizes just to force compliance.
- Body copy stays readable on mobile: line length constrained (use `max-width-text`), no text smaller than 0.875rem.
- Buttons and nav items never wrap mid-label. If a `button-group` doesn't fit horizontally on mobile, stack it vertically.
- Media scales with its wrapper (max-width 100%); no fixed pixel widths that break small screens.
- Tap targets are at least 44×44px on touch breakpoints.
- Grids collapse deliberately: the default for card grids is 4 or 3 → 2 (tablet) → 2 (mobile landscape) → 1 (mobile portrait). Define the column count per breakpoint on `_list`. Never rely on auto-wrapping to luck into a mobile layout.
- The nav switches to the hamburger menu from 991 down; the desktop nav must fit at 992, the first desktop pixel, with no wrapping.
- Breakpoints are desktop base plus 991 / 767 / 479 only. Do not add 1280, 1440 or 1920 without the site owner's word; they cannot be removed. Above 1440 the page stays contained (centred container, full-bleed grounds, fixed type).
