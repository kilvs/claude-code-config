# Gutenberg: Dynamic Blocks, ACF Blocks, Bindings & Editor Extensions

The PHP-side of extending the block editor — everything you can do **without a JavaScript build step**. This is the theme-dev sweet spot: dynamic data into blocks, custom blocks rendered in PHP, ACF blocks, block style variations, and deeper pattern control. For block-theme structure (theme.json, templates, parts) see `block-themes.md`; for custom fields see `custom-fields.md`; for escaping see `security.md`.

This file deliberately does **not** cover full JS/React block development (`@wordpress/scripts`, `edit.js`/`save.js`, JSX, the npm pipeline). That's a separate discipline. Everything here is PHP-first.

## Contents
1. The decision: do you even need a custom block?
2. Block Bindings API — dynamic data into core blocks (no block at all)
3. Dynamic blocks with block.json + render.php (PHP render, no build)
4. ACF Blocks
5. Block style variations (register_block_style)
6. Deeper patterns: categories, locking, synced overrides
7. Security across all of these

---

## 1. The decision: do you even need a custom block?

Most "I need a custom block" requests are better solved without one. Walk this ladder top-down and stop at the first that fits:

1. **A pattern** (`block-themes.md` §4) — if it's just a fixed arrangement of existing blocks, it's a pattern, not a block. Cheapest option.
2. **Block bindings** (§2) — if you need *dynamic data* (a custom field, post data) shown through an existing core block (Paragraph, Heading, Image, Button), bind it. No custom block needed.
3. **A dynamic block via block.json + render.php** (§3) — if you need custom server-rendered markup/logic (a "latest properties" list, a computed value) with its own editor presence.
4. **An ACF block** (§4) — same as above but you want to define the block's fields with ACF and render with a template, skipping JS entirely.
5. **A full JS/React block** — only when you need rich custom editor UI/interactions. Out of scope here; that's a dedicated build-tooling task.

Choosing the lowest rung that works keeps the theme simple and avoids a build pipeline.

## 2. Block Bindings API — dynamic data into core blocks

Introduced in WP 6.5, the Block Bindings API connects a block attribute (e.g. a Paragraph's `content`, an Image's `url`) to a data **source**, so the block renders dynamic data without a custom block. A binding stores a *reference* to the source, not the value — update the source and every bound block updates.

Version timeline worth knowing (state it from here, but if a current-version detail matters, verify by search since this is evolving): 6.5 shipped the API + `core/post-meta` source (developers only, no UI); 6.6 added pattern-override bindings; 6.7 added the editor "Attributes" UI so editors can bind Heading/Paragraph/Button/Image to custom fields via a dropdown; 6.9 added `core/post-data` and `core/term-data` sources and a filter to extend supported attributes. Bindable core blocks started as Paragraph, Heading, Image, Button and have expanded since.

**Bind a core field (no PHP beyond registering the meta).** First register the post meta so it's available:

```php
add_action( 'init', function () {
	register_post_meta( 'property', 'price', array(
		'show_in_rest' => true,   // required for the editor
		'single'       => true,
		'type'         => 'string',
		'label'        => __( 'Price', 'my-theme' ), // 6.7+ shows this in the UI
		'auth_callback'=> function () { return current_user_can( 'edit_posts' ); },
	) );
} );
```

Then in a block template or post, the Paragraph block binds its content to that meta:

```html
<!-- wp:paragraph {"metadata":{"bindings":{"content":{"source":"core/post-meta","args":{"key":"price"}}}}} -->
<p>Fallback price</p>
<!-- /wp:paragraph -->
```

If the field is an **ACF** field (ACF PRO 6.2.8+), the source is `acf/field` instead of `core/post-meta`.

**Register a custom binding source** for computed/external values (e.g. a copyright year, an API value). Use `register_block_bindings_source` on `init`:

```php
add_action( 'init', function () {
	register_block_bindings_source( 'my-theme/copyright', array(
		'label'              => __( 'Copyright', 'my-theme' ),
		'get_value_callback' => function ( $source_args, $block_instance, $attribute_name ) {
			return '© ' . esc_html( gmdate( 'Y' ) ) . ' ' . esc_html( get_bloginfo( 'name' ) );
		},
	) );
} );
```

```html
<!-- wp:paragraph {"metadata":{"bindings":{"content":{"source":"my-theme/copyright"}}}} -->
<p>© Fallback</p>
<!-- /wp:paragraph -->
```

The source name must be namespaced (`my-theme/...`), lowercase, dashes/slash only. The callback receives the block's `args` and returns the value; escape inside the callback since the result is injected into block output.

## 3. Dynamic blocks with block.json + render.php (PHP render, no build)

When bindings aren't enough — you need custom markup or query logic with its own block in the inserter — a **server-rendered block** does it with zero JavaScript build. The block is defined by a `block.json` and rendered by a PHP file.

Layout in the theme (e.g. under `blocks/latest-properties/`):

```
blocks/latest-properties/
├── block.json
└── render.php
```

`block.json` (note `"render"` points at the PHP file; no `editorScript`/build needed for a purely server-rendered block):

```json
{
	"$schema": "https://schemas.wp.org/trunk/block.json",
	"apiVersion": 3,
	"name": "my-theme/latest-properties",
	"title": "Latest Properties",
	"category": "widgets",
	"icon": "admin-home",
	"description": "Lists the most recent properties.",
	"attributes": {
		"count": { "type": "number", "default": 3 }
	},
	"render": "file:./render.php",
	"supports": { "html": false }
}
```

`render.php` (receives `$attributes`, `$content`, `$block`; returns escaped HTML):

```php
<?php
$count = isset( $attributes['count'] ) ? absint( $attributes['count'] ) : 3;
$q = new WP_Query( array( 'post_type' => 'property', 'posts_per_page' => $count ) );
if ( ! $q->have_posts() ) {
	return;
}
?>
<ul <?php echo get_block_wrapper_attributes(); ?>>
	<?php while ( $q->have_posts() ) : $q->the_post(); ?>
		<li><a href="<?php the_permalink(); ?>"><?php the_title(); ?></a></li>
	<?php endwhile; ?>
</ul>
<?php
wp_reset_postdata();
```

Register it on `init` by pointing at the directory:

```php
add_action( 'init', function () {
	register_block_type( get_template_directory() . '/blocks/latest-properties' );
} );
```

Two details that matter: `get_block_wrapper_attributes()` outputs the class/style attributes the editor expects (alignment, custom classes) — include it on the root element. And `wp_reset_postdata()` after a secondary `WP_Query`, same as the classic Loop (`classic-themes.md` §3). Without a JS `edit.js`, the editor shows a server-side preview; that's fine for most theme blocks. If you later want a richer editor experience you'd add JS — but that crosses into build-tooling territory this skill leaves alone.

## 4. ACF Blocks

If the project already uses ACF and you want the block's controls to be ACF fields (no `block.json` attributes, no JS), ACF Blocks render via a template and the field values. Register on `acf/init`:

```php
add_action( 'acf/init', function () {
	if ( ! function_exists( 'acf_register_block_type' ) ) {
		return;
	}
	acf_register_block_type( array(
		'name'            => 'property-card',
		'title'           => __( 'Property Card', 'my-theme' ),
		'render_template' => 'blocks/property-card/render.php',
		'category'        => 'widgets',
		'icon'            => 'admin-home',
		'mode'            => 'preview',
	) );
} );
```

The render template uses the field functions, escaped as always:

```php
<?php // blocks/property-card/render.php
$price = get_field( 'price' );
?>
<div class="property-card">
	<h3><?php echo esc_html( get_field( 'heading' ) ); ?></h3>
	<?php if ( $price ) : ?>
		<p class="price"><?php echo esc_html( number_format( (float) $price ) ); ?></p>
	<?php endif; ?>
</div>
```

You attach an ACF field group to the block by setting its location rule to Block → your block (in the ACF UI or in the exported PHP). ACF also supports registering blocks via `block.json` with an `acf` key (`acfBlockVersion`) if you prefer that style. Choose ACF Blocks when the team already lives in ACF and wants editor controls without touching JS; choose §3 when you'd rather not depend on ACF.

## 5. Block style variations (register_block_style)

A lightweight way to offer editors visual variants of a core or custom block (e.g. a "bordered" Group, an "outline" Button) — it just adds a selectable class, styled in CSS. No JS:

```php
add_action( 'init', function () {
	register_block_style( 'core/quote', array(
		'name'         => 'fancy',
		'label'        => __( 'Fancy', 'my-theme' ),
		'inline_style' => '.is-style-fancy { border-left: 4px solid; padding-left: 1rem; }',
	) );
} );
```

Editors then pick "Fancy" in the block's Styles panel; the block gets `is-style-fancy`. Prefer putting the actual CSS in your stylesheet/`theme.json` and omitting `inline_style` for anything non-trivial. In block themes, `theme.json` can also define block style variations under `styles.blocks` and via the `/styles` variation files.

## 6. Deeper patterns: categories, locking, synced overrides

Building on `block-themes.md` §4:

**Custom pattern categories** group your patterns in the inserter:

```php
add_action( 'init', function () {
	register_block_pattern_category( 'my-theme-sections', array(
		'label' => __( 'My Theme Sections', 'my-theme' ),
	) );
} );
```

Reference it in a pattern's header (`Categories: my-theme-sections`).

**Block locking** stops editors from moving/removing parts of a layout — useful for patterns/templates you want kept intact. It's a per-block attribute in the markup:

```html
<!-- wp:group {"lock":{"move":true,"remove":true}} -->
```

`move` prevents reordering, `remove` prevents deletion. Apply `templateLock` at a container/template level (`"all"`, `"insert"`, or `false`) to control whether editors can add/remove children at all.

**Synced pattern overrides** (6.6+) let a synced pattern keep shared structure while allowing specific bound fields to be edited per instance — built on the Block Bindings API (§2). Mark the editable blocks in the pattern with the `core/pattern-overrides` binding. Reach for this when clients need "the same card layout everywhere, but each instance has its own text/image."

## 7. Security across all of these

Block output is rendered to the page, so the escaping rules in `security.md` apply everywhere here:
- In `render.php` / ACF render templates, escape every dynamic value by context (`esc_html`, `esc_attr`, `esc_url`, `wp_kses_post` for intentional rich text).
- In custom binding `get_value_callback`s, escape the returned value — it's injected into block markup.
- Sanitize/`absint()` block attributes before using them in queries (a `count` attribute going into `posts_per_page`, for instance).
- Use `get_block_wrapper_attributes()` rather than hand-building the wrapper, so block supports are output safely.
