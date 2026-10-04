# Style Guide Reference

How to produce a Client-First style guide — the document/page that defines a project's design system so it can be built and maintained consistently in Webflow. Mirrors the structure of the official Client-First cloneable style guide.

A style guide is a bigger deliverable than a spec. If the user wants a keepable artifact, write it to a file (Markdown for reading, or an HTML page that renders the system visually). For a quick reference, inline is fine.

## What a Client-First style guide contains

Produce these sections in order:

### 1. Color
- Primitive palette: swatches with hex + token name (`Primitives: colour/navy/500`), grouped Brand / Neutral / System.
- Semantic tokens: each with its name, the primitive it references, and intended use (`text-color--text-primary` → Neutral/900 → default body text).
- Note any client-provided system being conformed to.

### 2. Typography
- Font families (heading + body), with fallback stacks.
- The full type scale as a rendered specimen: each `text-size-*` step shown at actual size with its rem/px value, mobile and desktop.
- Weights in use (`text-weight-*`).
- Line-height and max-width (measure) rules.

### 3. Headings & semantic tags
- H1–H6 shown, with the reminder that visual size (`text-size-*`) is decoupled from semantic level. One H1 per page.

### 4. Spacing
- The spacing scale (named steps → rem/px).
- Section padding classes (`padding-section-*`) and global padding (`padding-global`) with their values and breakpoint behavior.

### 5. Core structure
- The `section_* > padding-section-* > padding-global > container-large` pattern shown as a labeled diagram or nested code block, so anyone building knows the wrapper sequence.
- Container max-widths (large/medium/small).

### 6. Buttons & interactive elements
- Button base class + `is-*` variants (primary, secondary, ghost), with states (default/hover/active/disabled). Show the combo-class pattern.
- Links, inputs, and form fields if the project needs them.

### 7. Components (as the project grows)
- Each recurring block documented with its `[name]_component / _list / _item / _element` structure and the classes it introduces.

### 7a. State classes
- One labelled sample per runtime `is-*` state (`component_faq_item is-open`): a plain div with the base class plus the combo. It documents the state and keeps the class alive through Clean Up unused styles, and lets IX3 pick it.

### 8. Utility class index
- A scannable list of the global/utility classes available (text size, weight, color, alignment, visibility, max-width), so builders reuse rather than recreate.

## Principles
- The style guide is the single source of truth — every value traces back to a token or approved scale.
- Show, don't just tell: render swatches and specimens at real values where the format allows.
- Keep it buildable: every named thing should correspond to a real Webflow class or variable.
- If conforming to a client's brand, the style guide documents *their* system in Client-First structure — don't override their names.

## Build note to include
When delivering a style guide for Webflow, end with the setup order: (1) create primitive color variables, (2) create semantic color variables referencing them, (3) create the structure classes (`padding-global`, `container-*`, `padding-section-*`), (4) create text and utility classes, (5) build components on top. This is the order that avoids rework in the Designer.
