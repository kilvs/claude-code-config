# Sizing and tokens

- All sizing in rem (1rem = 16px). Allowed exceptions only: `1px` borders, `0.125rem` micro-spacing, `0.875rem` small type.
- If a value exists as a variable, bind the variable — never re-type the raw value. No hardcoded hex colors, no px font sizes, no free-typed spacing like `padding: 37px`.
- Bind **semantic** tokens (Theme, Typography, Spacing, Layout, Components collections) to elements. Never bind a Primitives variable directly — a primitive binding will not follow theme changes.
- Spacing values come from the Spacing collection only (`padding-global`, `padding-section/*`, `gap/*`, `content/*`), which alias the Primitives `spacer/` scale. Responsive changes happen through Variable Modes per breakpoint (Desktop base, 991, 767, 479), overriding downward from the desktop base.
- Every utility class binds a token: `heading-style-*` and `text-size-*` to Typography, `text-color-*` and `background-color-*` to Theme, `spacer-*`, `margin-*`, `padding-*`, `padding-section-*` and `padding-global` to Spacing or the Primitives spacer scale, `max-width-*` and `container-*` to Layout. A value change happens in the Variables panel, never on the utility class or the style guide page.
- Primitives colours are the design file's swatches only, slotted by lightness. No generated tints, no leftover template ramps, no starter `default` collection. Details: `variables` skill sections 2 and 10.
- Token names are slash-grouped (`heading/h1`, `button/primary-background`). The full map is the `variables` skill.
- If a needed value does not exist as a token, propose it to the site owner (name, collection, value, where it's used). Do not invent a hex code or a one-off size in the style panel in the meantime.
