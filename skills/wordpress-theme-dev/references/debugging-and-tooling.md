# Debugging, Tooling & Custom Post Types

Practical setup for running and troubleshooting a theme, plus registering the post types and taxonomies that theme examples assume exist. For escaping/security see `security.md`; for hooks see `wp-apis.md`.

## Contents
1. Debug configuration
2. Query Monitor & debugging workflow
3. Local development environments
4. WP-CLI for theme work
5. Custom post types & taxonomies (create, update, modify)

---

## 1. Debug configuration

You can't fix what you can't see. Before judging whether a theme "activates without warnings," turn debugging on. In `wp-config.php` (development only — never on production):

```php
define( 'WP_DEBUG', true );          // surface PHP notices/warnings
define( 'WP_DEBUG_LOG', true );      // write them to wp-content/debug.log
define( 'WP_DEBUG_DISPLAY', false ); // don't render them into the page
define( 'SCRIPT_DEBUG', true );      // load unminified core JS/CSS
@ini_set( 'display_errors', 0 );
```

With `WP_DEBUG_LOG` on, tail the log while developing:
```bash
tail -f wp-content/debug.log
```

A theme that throws notices under `WP_DEBUG` is not done — undefined array keys from custom fields, calling template tags outside the Loop, and missing escaping often show up here first. The goal is a clean log on every page type (front page, single, archive, 404, search).

## 2. Query Monitor & debugging workflow

**Query Monitor** (free plugin) is the single most useful theme-debugging tool. It surfaces, per request: database queries (and which ones are slow or duplicated), the template file WordPress chose from the hierarchy, hooks fired, enqueued scripts/styles, HTTP API calls, and PHP errors. When a theme loads the "wrong" template or an asset isn't enqueuing, Query Monitor tells you why far faster than guessing.

Typical loop: reproduce the issue → open Query Monitor → check the "Template" panel (is the expected file being used?) and the "PHP Errors" / "Queries" panels → fix → recheck. Pair it with `debug.log` for errors that happen before the page renders.

## 3. Local development environments

Themes should be built against a real local WordPress, not guessed at. Common options, roughly easiest-first:

- **Studio by WordPress.com** — free, fast, GUI, good default for most theme work.
- **LocalWP** — free, GUI, popular, easy SSL and one-click admin.
- **wp-env** — official, Docker-based, config-as-code (`.wp-env.json`); ideal when you want the environment in version control and reproducible across a team. Start with `npx @wordpress/env start`.
- **DevKinsta** — free, GUI, geared toward Kinsta hosting.

For a theme that must run on a specific PHP/WP version (per the `style.css` `Requires` headers), pick a tool that lets you set those — wp-env and LocalWP both do. Put the theme in `wp-content/themes/<slug>/` (or symlink your repo there) and activate it.

## 4. WP-CLI for theme work

WP-CLI is the command-line interface to WordPress and removes a lot of click-through. The commands that matter for theme dev:

```bash
# Scaffold an underscores-style classic theme (alternative to our script for classic only)
wp scaffold _s my-theme --theme_name="My Theme" --author="You"

# Generate the translation template after wrapping strings in __()/_e()
wp i18n make-pot . languages/my-theme.pot

# Create test content to exercise templates (archives, pagination, single)
wp post generate --count=30 --post_type=post
wp post generate --count=15 --post_type=property   # if the CPT is registered

# Activate / list / check themes
wp theme activate my-theme
wp theme list

# Flush rewrite rules after registering a CPT/taxonomy (see §5)
wp rewrite flush

# Tail nothing? Check for fatals quickly
wp eval 'echo "ok";'
```

`wp post generate` is especially valuable — most template bugs (broken pagination, empty archives, bad excerpt handling) only appear with realistic content volume. Generate some before reviewing a build.

## 5. Custom post types & taxonomies (create, update, modify)

Theme examples here reference a `property` post type; this is how it's registered. A note on placement first: **registering content types in a theme couples that content to the theme** — deactivate the theme and the "properties" become inaccessible. The portable practice is to register CPTs/taxonomies in a small site-specific *plugin* (or mu-plugin) so content survives theme changes, and keep only the *presentation* in the theme. That said, theme devs register them in `functions.php` constantly for theme-bound content; do it knowingly. Whichever file it lives in, the API is identical.

### Create

Register on `init`:

```php
add_action( 'init', 'mytheme_register_property' );
function mytheme_register_property() {
	$labels = array(
		'name'          => __( 'Properties', 'my-theme' ),
		'singular_name' => __( 'Property', 'my-theme' ),
		'add_new_item'  => __( 'Add New Property', 'my-theme' ),
		'edit_item'     => __( 'Edit Property', 'my-theme' ),
	);
	register_post_type( 'property', array(
		'labels'       => $labels,
		'public'       => true,
		'has_archive'  => true,                      // enables archive-property.php
		'menu_icon'    => 'dashicons-admin-home',
		'rewrite'      => array( 'slug' => 'properties' ),
		'supports'     => array( 'title', 'editor', 'thumbnail', 'excerpt' ),
		'show_in_rest' => true,                       // REQUIRED for block editor + REST
	) );
}
```

Register a taxonomy (e.g. property type) and attach it:

```php
add_action( 'init', 'mytheme_register_property_type' );
function mytheme_register_property_type() {
	register_taxonomy( 'property_type', 'property', array(
		'labels'            => array(
			'name'          => __( 'Property Types', 'my-theme' ),
			'singular_name' => __( 'Property Type', 'my-theme' ),
		),
		'hierarchical'      => true,                  // true = category-like, false = tag-like
		'public'            => true,
		'show_admin_column' => true,
		'show_in_rest'      => true,
		'rewrite'           => array( 'slug' => 'property-type' ),
	) );
}
```

Two things that cause "404 on my new post type" every time:
- **Flush rewrite rules** after first registering (or changing slugs): visit Settings → Permalinks once, or run `wp rewrite flush`. Don't call `flush_rewrite_rules()` on every `init` — that's a performance bug; flush once on theme/plugin activation.
- `has_archive => true` is what makes `archive-property.php` in the hierarchy work.

### Update / modify

Modifying an existing type is just changing the `register_post_type`/`register_taxonomy` args and re-flushing rewrites if you touched `rewrite`/`has_archive`/`public`. To adjust a type you *don't* own (a plugin's, or core's), don't re-register — filter its args:

```php
// Add excerpt support and archive to an existing CPT registered elsewhere.
add_action( 'init', function () {
	add_post_type_support( 'product', 'excerpt' );
}, 11 ); // priority after the original registration

// Change labels/args of a CPT registered by a plugin.
add_filter( 'register_post_type_args', function ( $args, $post_type ) {
	if ( 'product' === $post_type ) {
		$args['has_archive'] = true;
	}
	return $args;
}, 10, 2 );
```

To change *which* of these posts appear on their archive (per-page count, ordering), use `pre_get_posts` — see `wp-apis.md` §7. To add editable fields to the type (price, address), use custom fields — see `custom-fields.md`. Output in `single-property.php` / `archive-property.php` per the template hierarchy in `classic-themes.md`.

Placement in the theme: put this in an `inc/` file (e.g. `inc/property.php`). The classic scaffold auto-requires every `*.php` in `inc/` from `functions.php`, so dropping the file in is enough — no manual `require` line to add.
