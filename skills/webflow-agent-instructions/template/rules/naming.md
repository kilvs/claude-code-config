# Naming

All class, variable, and interaction names on this site follow these laws. No exceptions.

- Lowercase only. Hyphens separate words within a level. Underscores separate levels in custom classes — never sit inside a word pair.
- **Section wrappers:** `section-[page]_[element]` → `section-home_hero`, `section-about_team`. The wrapper carries no trailing tag. CMS template pages use `template-[collection]` as the page identifier → `section-template-blog_header`. Site-wide sections use `global` → `section-global_cta`.
- **Custom classes inside a section:** `[page]_[element]_[tag]` → `home_hero_content`, `home_projects_list_wrap`, `home_projects_item`.
- **Description text:** paragraph / supporting copy always uses the `_description` tag → `home_hero_description`. Never `_text` or `_paragraph`.
- **Reusable components:** `component_[name]_[tag]` → `component_project-card`, `component_project-card_content`. The established `navbar_component` and `footer_component` names stay as-is.
- **Utility classes** never contain an underscore: `text-size-large`, `padding-global`, `button-group`, `container-large`.
- **Variants:** a Component varies through Webflow **variants**, never `is-` combos. On a non-component class, a one-off variation is an `is-` combo (`home_hero_image is-wide`). Maximum one or two combos — never deep-stack classes.
- **State classes** added only at runtime (by IX3 or a script: `is-open`, `is-active`) are Designer combo classes, each anchored by a labelled sample in the **State classes** section of the Style Guide page, so style clean-up cannot delete them and IX3 can pick them.
- Name by role, never by appearance: `card_title`, not `card_blue-18px`. No numbered suffixes as versioning — `hero_wrapper-2` is forbidden.
- Never leave an element on an auto-generated class (`Div Block 12`, `Heading 4`). Assign a proper class or remove the element before finishing.
- **Variables** are slash-grouped: `group/name`, lowercase, hyphens inside a segment, ordered small to large. Primitives carry descriptive names — what the value *is*: `colour/navy/800`, `spacer/small`. Role-based names (`background/primary`, `button/primary-background`) live only in the semantic collections (Theme, Typography, Spacing, Layout, Components).
- **Relume layer names** (`section_header1`, `layout241`) never become classes. Translate to the kit's names on build and record the mapping in the build note.
- **Navigator display names** (labels, not classes): slots are named `Slot: <what goes in, plural>` (`Slot: Buttons`, `Slot: Content`); no Component name starts with "Slot:". Divs keep their class name as the label. Never rename a class to get a nicer label.
- **Code embeds:** `global-styles` and `global-scripts` on the embeds inside the Global Styles and Global Scripts components; `section-script-css` and `section-script-js` on a section's own embeds. All `display: none`.
- **Interactions:** `[Element] [Action] [State]` → "Navbar Dropdown Open".
