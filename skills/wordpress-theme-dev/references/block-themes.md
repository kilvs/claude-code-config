# Block (FSE) Themes

Reference for Full Site Editing themes. For classic PHP themes see `classic-themes.md`. For hooks/enqueue/i18n see `wp-apis.md`. For building custom/dynamic blocks, binding dynamic data into core blocks, ACF blocks, block style variations, and deeper pattern control (categories, locking, synced overrides), see `gutenberg-blocks.md`.

## Contents
1. File structure
2. theme.json — the heart of a block theme
3. Templates and template parts (HTML)
4. Block patterns
5. functions.php in a block theme
6. Common pitfalls

---

## 1. File structure

```
my-theme/
├── style.css          REQUIRED — header only; styling lives in theme.json
├── theme.json         REQUIRED in practice — global settings & styles
├── templates/         REQUIRED — HTML templates (index.html mandatory)
│   ├── index.html
│   ├── single.html
│   ├── page.html
│   ├── archive.html
│   ├── 404.html
│   └── home.html
├── parts/             template parts
│   ├── header.html
│   └── footer.html
├── patterns/          block patterns (PHP files, registered automatically)
│   └── hero.php
├── functions.php      optional — enqueue, supports, pattern categories
├── styles/            optional — style variations (alternate theme.json)
│   └── dark.json
├── screenshot.png
└── assets/
```

`style.css` still needs the header comment (same fields as classic, see `classic-themes.md`) — it identifies the theme — but visual styling is driven by `theme.json`, not CSS rules here.

The templates are made of block markup. `templates/index.html` is the only strictly required template; the rest follow the same hierarchy names as classic themes (`single`, `page`, `archive`, `404`, etc.).

## 2. theme.json — the heart of a block theme

`theme.json` defines global settings (what's available to editors), styles (defaults applied), and how everything maps to CSS. It's the single most important file and the one most error-prone to write from memory — check keys against this.

**Minimal scaffold posture**: the scaffold script ships `theme.json` with empty `palette`, `fontFamilies`, and `fontSizes` (and `defaultPalette`/`defaultFontSizes` set to `false` so WordPress's own presets don't appear), no `layout` sizes, and no `styles` block — `appearanceTools: true` keeps the editor controls available. This is so the developer chooses brand color, container size, and fonts deliberately rather than deleting placeholders. The example below is the *fully-populated* shape to grow into; fill it from the user's actual brand values, not invented ones.

Top-level shape (schema version 3, WP 6.6+; use 2 for 6.0–6.5):

```json
{
  "$schema": "https://schemas.wp.org/trunk/theme.json",
  "version": 3,
  "settings": {
    "appearanceTools": true,
    "layout": { "contentSize": "640px", "wideSize": "1200px" },
    "color": {
      "palette": [
        { "slug": "primary", "color": "#1a73e8", "name": "Primary" },
        { "slug": "base", "color": "#ffffff", "name": "Base" },
        { "slug": "contrast", "color": "#111111", "name": "Contrast" }
      ],
      "custom": false,
      "customDuotone": false
    },
    "typography": {
      "fluid": true,
      "fontFamilies": [
        {
          "slug": "body",
          "name": "Body",
          "fontFamily": "system-ui, sans-serif"
        }
      ],
      "fontSizes": [
        { "slug": "small", "size": "0.875rem", "name": "Small" },
        { "slug": "medium", "size": "1rem", "name": "Medium" },
        { "slug": "large", "size": "1.5rem", "name": "Large" }
      ]
    },
    "spacing": {
      "spacingScale": { "steps": 7 },
      "units": ["px", "em", "rem", "vh", "vw", "%"]
    }
  },
  "styles": {
    "color": { "background": "var(--wp--preset--color--base)", "text": "var(--wp--preset--color--contrast)" },
    "typography": { "fontFamily": "var(--wp--preset--font-family--body)", "lineHeight": "1.6" },
    "elements": {
      "link": { "color": { "text": "var(--wp--preset--color--primary)" } },
      "button": {
        "color": { "background": "var(--wp--preset--color--primary)", "text": "var(--wp--preset--color--base)" }
      }
    },
    "blocks": {
      "core/heading": { "typography": { "fontWeight": "700" } }
    }
  },
  "templateParts": [
    { "name": "header", "title": "Header", "area": "header" },
    { "name": "footer", "title": "Footer", "area": "footer" }
  ],
  "customTemplates": [
    { "name": "page-no-title", "title": "Page (no title)", "postTypes": ["page"] }
  ]
}
```

Key mental model: every preset you define becomes a CSS custom property following the pattern `--wp--preset--{category}--{slug}` (e.g. `--wp--preset--color--primary`). Reference those in `styles` and in your own CSS rather than repeating hex values. `settings` controls *what editors can do*; `styles` sets *the defaults*. `appearanceTools: true` is a shortcut that switches on border, link-color, spacing, and typography controls in one line.

**Style variations**: drop additional partial `theme.json` files in `styles/` (e.g. `styles/dark.json`) — they show up as one-click alternate looks in the Site Editor.

## 3. Templates and template parts (HTML)

Templates are HTML files containing block markup (block grammar = HTML comments). You rarely hand-author these from scratch — build in the Site Editor and export, or scaffold — but you must be able to read and edit them.

A minimal `templates/index.html`:

```html
<!-- wp:template-part {"slug":"header","area":"header","tagName":"header"} /-->

<!-- wp:group {"tagName":"main","layout":{"type":"constrained"}} -->
<main class="wp-block-group">
	<!-- wp:query {"queryId":1,"query":{"perPage":10,"postType":"post"}} -->
	<div class="wp-block-query">
		<!-- wp:post-template -->
			<!-- wp:post-title {"isLink":true} /-->
			<!-- wp:post-excerpt /-->
		<!-- /wp:post-template -->
		<!-- wp:query-pagination -->
			<!-- wp:query-pagination-previous /-->
			<!-- wp:query-pagination-numbers /-->
			<!-- wp:query-pagination-next /-->
		<!-- /wp:query-pagination -->
	</div>
	<!-- /wp:query -->
</main>
<!-- /wp:group -->

<!-- wp:template-part {"slug":"footer","area":"footer","tagName":"footer"} /-->
```

Rules: block comment attributes are JSON and must be valid (a stray comma breaks the template silently). Self-closing blocks use `/-->`. The Query Loop block replaces the classic Loop. Template parts referenced here must exist in `parts/` and be declared in `theme.json` `templateParts` for proper area assignment.

## 4. Block patterns

Patterns are reusable block layouts. As of WP 6.0+, any PHP file in `patterns/` is auto-registered — no manual `register_block_pattern()` needed. Use a header docblock:

```php
<?php
/**
 * Title: Hero
 * Slug: my-theme/hero
 * Categories: featured, my-theme
 * Description: Full-width hero with heading and button.
 */
?>
<!-- wp:cover {"minHeight":480,"layout":{"type":"constrained"}} -->
<div class="wp-block-cover">
	<!-- wp:heading {"level":1} -->
	<h1><?php esc_html_e( 'Welcome', 'my-theme' ); ?></h1>
	<!-- /wp:heading -->
</div>
<!-- /wp:cover -->
```

Because patterns are PHP, you can use `esc_html_e()` etc. for translatable strings — do this for any user-facing text. Register a custom pattern category in `functions.php` if you used one:

```php
add_action( 'init', function () {
	register_block_pattern_category( 'my-theme', array( 'label' => __( 'My Theme', 'my-theme' ) ) );
} );
```

## 5. functions.php in a block theme

Block themes need far less PHP, but `functions.php` still handles enqueueing (e.g. a small `style.css` or editor styles), theme supports not covered by `theme.json`, and pattern categories.

```php
<?php
defined( 'ABSPATH' ) || exit;

add_action( 'after_setup_theme', function () {
	add_theme_support( 'wp-block-styles' );      // core block default styles
	add_theme_support( 'editor-styles' );
	add_theme_support( 'responsive-embeds' );
	load_theme_textdomain( 'my-theme', get_template_directory() . '/languages' );
} );

add_action( 'wp_enqueue_scripts', function () {
	wp_enqueue_style(
		'my-theme-style',
		get_stylesheet_uri(),
		array(),
		wp_get_theme()->get( 'Version' )
	);
} );
```

Note `theme.json` already declares many supports implicitly — don't duplicate (e.g. don't `add_theme_support('align-wide')` if layout is set in `theme.json`).

## 6. Common pitfalls

- **Invalid JSON in block comments or theme.json** — fails silently or shows "this block contains unexpected content." Validate JSON.
- **Forgetting `templateParts` in theme.json** — parts render but aren't assigned to header/footer areas, breaking the Site Editor UX.
- **Wrong schema version** — `version: 3` features (like `settings.background`) silently no-op on older WP. Match the version to the `Requires at least`.
- **Styling in style.css instead of theme.json** — works but fights the editor; editors' changes won't reflect your CSS. Prefer `theme.json` and `styles/` variations.
- **Hardcoding colors instead of presets** — breaks style variations and the editor color picker. Use `var(--wp--preset--color--*)`.
