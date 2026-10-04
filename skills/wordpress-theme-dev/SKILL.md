---
name: wordpress-theme-dev
description: Build custom WordPress themes from scratch, both classic PHP themes (functions.php, template hierarchy, the Loop) and block/FSE themes (theme.json, templates, patterns). Scaffolds a starter theme and covers hooks, enqueueing, i18n, security (escaping, sanitizing, nonces), custom fields with ACF, Secure Custom Fields (SCF), and Carbon Fields, custom post types and taxonomies, debugging and tooling (WP_DEBUG, Query Monitor, WP-CLI), version control, the Finsweet Client-First naming convention for classic themes, and the PHP side of Gutenberg blocks (Block Bindings API, dynamic blocks via block.json, ACF blocks, block style variations). Trigger on creating or structuring a theme, editing functions.php or theme.json, custom fields, metaboxes, CPTs, taxonomies, custom or dynamic blocks, bindings, debugging, or terms like child theme, FSE, ACF, Carbon Fields, Client-First, Gutenberg, block.json. Do NOT use for JS or React block development (edit.js, @wordpress/scripts), non-block plugins, or non-WordPress PHP.
---

## Changes

- 22 Sep 2026: editable master moved to `~/Documents/AI Agent Config/skills/`. Synced claude.ai copy is the published twin; re-upload after improvements.

# WordPress Theme Development

Build production-quality custom WordPress themes. This skill covers two theme types and helps you pick the right one, scaffold it correctly, and write it to WordPress standards.

## First: classic or block?

WordPress has two theme architectures. Choosing wrong means rebuilding, so decide deliberately before scaffolding.

**Block theme (Full Site Editing / FSE)** — the modern default. The whole site (header, footer, templates) is editable in the Site Editor through `theme.json` + HTML templates made of blocks. Choose this when: the project is new, the client/editor wants to control layout without code, you want to align with where WordPress is heading, or the design maps cleanly onto blocks and patterns.

**Classic theme (PHP)** — template files (`index.php`, `single.php`, etc.), `functions.php`, and the Loop. Choose this when: you need precise PHP control over markup, you're integrating tightly with custom plugins / ACF / custom queries, the client has an existing classic ecosystem, or the design needs logic that's awkward to express as blocks.

If the user hasn't said which, ask once. If they describe editor-driven layout control → lean block. If they describe custom PHP/query logic → lean classic. When genuinely unsure, default to a **block theme** since it's the current WordPress direction, but say why.

## Workflow

1. **Confirm theme type** (above) and gather: theme name, text domain (lowercase-hyphenated, usually matches folder), author, minimum WP/PHP versions. If the design needs content types beyond posts/pages (e.g. "properties," "events"), note that custom post types/taxonomies are involved — register them per `references/debugging-and-tooling.md` §5, ideally in a site plugin so content outlives the theme.
2. **Scaffold** using the appropriate script — don't hand-type boilerplate:
   - Classic: `python scripts/scaffold_classic.py --name "My Theme" --slug my-theme --output <dir>`
   - Block: `python scripts/scaffold_block.py --name "My Theme" --slug my-theme --output <dir>`
   Run `--help` on either for all options (author, description, URI, etc.). The scripts emit a valid, activatable theme with correct headers, enqueueing, i18n setup, and security-clean templates.

   **Minimal by default — no brand bloat.** Both scaffolds ship deliberately empty of styling opinions: the block `theme.json` has empty `palette`/`fontFamilies`/`fontSizes` (WordPress defaults switched off) and no `styles` block, and no `layout` sizes; the classic theme omits decorative supports. This is intentional — the user sets brand color, container/content size, fonts, and other global styles themselves. **Do not invent placeholder palettes, fonts, or container sizes.** If the user wants those filled in, either pass `--with-samples` (adds an example palette/fonts/sizes and a hero pattern) or, better, ask them for their actual values and write those into `theme.json`. When a build needs global styling and the user hasn't given values, ask for them rather than guessing.
3. **Read the relevant reference** before customizing. Don't rely on memory for hook names, escaping function choices, or `theme.json` keys — they're easy to get subtly wrong. See "Reference files" below.
4. **Build out** the templates/styles the user needs, applying the hard rules below to every line.
5. **Sanity-check**: confirm `style.css` header is complete, every dynamic output is escaped, every enqueue is hooked correctly, all user-facing strings are translatable, and the theme activates without warnings (`WP_DEBUG` on).

## Hard rules (these are what separate amateur themes from professional ones)

These aren't bureaucracy — each one prevents a real, common failure. Apply them everywhere.

**Escape on output, every time.** Untrusted data rendered to the page is the #1 theme vulnerability. Use `esc_html()`, `esc_attr()`, `esc_url()`, `wp_kses_post()` at the point of output — even for data you think is safe, because themes get reused in contexts you didn't anticipate. This includes **custom field values** (ACF/SCF/Carbon Fields): they're user input, and the convenient echo helpers (`the_field()`, `carbon_get_*`) don't reliably escape — prefer the value-returning function wrapped in the right `esc_*`. See `references/security.md` for which function to use where, and `references/custom-fields.md` §5 for the field-output specifics.

**Sanitize on input, validate on use.** Anything from `$_POST`, `$_GET`, settings, or the Customizer gets sanitized when stored and validated when used.

**Never hardcode paths or URLs.** Use `get_template_directory()`, `get_stylesheet_directory_uri()`, `get_theme_file_uri()`. Hardcoded paths break the moment the theme moves or runs in a child theme.

**Enqueue, never inline `<link>`/`<script>`.** All CSS/JS goes through `wp_enqueue_style` / `wp_enqueue_script` on the `wp_enqueue_scripts` hook, with a version string for cache-busting. Inline tags bypass dependency management and break plugins.

**Everything user-facing is translatable.** Wrap strings in `__()`, `_e()`, `esc_html__()`, etc. with the theme's text domain. Load the text domain on `after_setup_theme`. Retrofitting i18n later is miserable.

**Prefix everything global.** Functions, globals, and handles get a unique theme prefix (e.g. `mytheme_setup`) to avoid collisions with plugins and core.

**Check for direct access.** Every PHP file starts with `defined( 'ABSPATH' ) || exit;` so files can't be hit directly.

**Child theme = override, don't edit.** When the task is customizing an existing theme, build a child theme (the block/classic scripts both support `--child --parent <slug>`). Editing a parent theme directly means updates wipe the work.

## Reference files

Read the file that matches what you're building. They carry the deep detail — hook signatures, the full template hierarchy, `theme.json` schema, escaping matrix — that's too error-prone to recall precisely.

- `references/classic-themes.md` — template hierarchy (which file WP picks and why), the Loop, conditional tags, `functions.php` patterns, template tags, `get_template_part()`.
- `references/block-themes.md` — `theme.json` structure and settings, `templates/` and `parts/` HTML, block patterns, registering patterns, theme supports for FSE.
- `references/wp-apis.md` — the hooks system (actions vs filters, priorities, common hooks), enqueueing in depth, i18n setup, the Settings API and Customizer, nav menus, widgets/block areas.
- `references/security.md` — the escaping function matrix (which to use for HTML vs attr vs URL vs JS), sanitization functions, nonces for forms/AJAX, capability checks.
- `references/scss-pipeline.md` — plain-CSS structure, the SCSS setup (7-1 pattern, compilation, sourcemaps), and how it ties into enqueueing.
- `references/custom-fields.md` — custom fields / metaboxes with ACF and Secure Custom Fields (SCF), and with Carbon Fields: choosing between them, the ACF/SCF fork situation, registering fields (UI export or code), retrieving and **safely outputting** values, options pages, repeaters, and version-controlling field definitions. Read this for any custom-field, metabox, or "extra content fields" task.
- `references/debugging-and-tooling.md` — turning on `WP_DEBUG`/`WP_DEBUG_LOG`, Query Monitor, local environments (wp-env, LocalWP, Studio), WP-CLI for theme work (scaffolding, `make-pot`, generating test content, flushing rewrites), and **registering/updating/modifying custom post types & taxonomies** (`register_post_type`, `register_taxonomy`, filtering existing types, rewrite flushing). Read this when running/troubleshooting a theme or when an example assumes a custom post type exists.
- `references/version-control-and-quality.md` — what to commit vs ignore, the theme `.gitignore` (the scaffolds drop one in), committing ACF `acf-json/` vs Carbon Fields PHP, and the **handoff to the page-quality-auditor skill** for performance/SEO/accessibility rather than duplicating it here.
- `references/client-first-naming.md` — porting Finsweet's Client-First class-naming convention and structure classes (`page-wrapper`, `container-*`, `padding-section-*`, dash-utility vs underscore-folder naming) into a **classic** theme's markup and SCSS, and why it should NOT be used on block themes. Read this when the user wants Client-First conventions in WordPress; the webflow-ui-design skill remains the authority for Client-First in Webflow itself.
- `references/gutenberg-blocks.md` — the PHP-side of extending the block editor with **no JS build step**: the Block Bindings API (dynamic data into core blocks via `core/post-meta`/`acf/field`/custom `register_block_bindings_source`), dynamic blocks with `block.json` + `render.php` (`register_block_type`), ACF Blocks (`acf_register_block_type`), block style variations (`register_block_style`), and deeper patterns (categories, locking, synced overrides). Read this for any custom block, "dynamic data in a block," bindings, or editor-extension task. Does NOT cover JS/React block development (edit.js/save.js, @wordpress/scripts) — that's out of scope.

When a task spans both theme types (e.g. a general "how do hooks work" question), `wp-apis.md` and `security.md` apply to both.
