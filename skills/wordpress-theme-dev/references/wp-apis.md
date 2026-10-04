# WordPress APIs

Applies to both classic and block themes. For type-specific structure see `classic-themes.md` / `block-themes.md`. For escaping/sanitizing see `security.md`.

## Contents
1. The hooks system (actions & filters)
2. Enqueueing styles & scripts
3. Internationalization (i18n)
4. The Settings API & Customizer
5. Nav menus
6. Widget / block areas
7. pre_get_posts

---

## 1. The hooks system

Hooks are how themes plug into WordPress's execution without editing core. Two kinds:

**Actions** — fire at a moment so you can *do* something (output markup, enqueue, register). They don't return; they act.
```php
add_action( 'wp_enqueue_scripts', 'mytheme_assets' );
function mytheme_assets() { /* enqueue here */ }
```

**Filters** — let you *modify* a value as it passes through. You receive data and must `return` it (returning nothing = breaking the site).
```php
add_filter( 'excerpt_length', 'mytheme_excerpt_length' );
function mytheme_excerpt_length( $length ) { return 25; }
```

**Signature**: `add_action( $hook, $callback, $priority = 10, $accepted_args = 1 )`. Priority orders callbacks (lower runs earlier). `$accepted_args` must match how many arguments your callback wants — a frequent bug is requesting more args than declared.

```php
add_filter( 'the_content', 'mytheme_after_content', 10, 1 );
```

Hooks you'll use constantly in themes:
- `after_setup_theme` — register supports, menus, text domain.
- `init` — register post types/taxonomies, pattern categories.
- `wp_enqueue_scripts` — front-end CSS/JS. **The** place to enqueue.
- `enqueue_block_editor_assets` / `enqueue_block_assets` — editor/block styles.
- `widgets_init` — register sidebars.
- `customize_register` — Customizer settings/controls.
- `pre_get_posts` — alter the main query (see §7).
- `wp_head` / `wp_footer` — must be present via `wp_head()`/`wp_footer()` calls in classic templates or plugins/enqueues break.

Always remove or guard with `function_exists()` where a child theme might override.

## 2. Enqueueing styles & scripts

Never put raw `<link>`/`<script>` in templates. Enqueueing gives you dependency ordering, versioning/cache-busting, and conditional loading, and lets plugins coexist.

```php
add_action( 'wp_enqueue_scripts', 'mytheme_assets' );
function mytheme_assets() {
	$ver = wp_get_theme()->get( 'Version' );

	wp_enqueue_style(
		'mytheme-main',                              // unique handle (prefix it)
		get_theme_file_uri( 'assets/css/main.css' ), // never hardcode the URL
		array(),                                     // dependencies
		$ver                                         // version for cache-busting
	);

	wp_enqueue_script(
		'mytheme-nav',
		get_theme_file_uri( 'assets/js/nav.js' ),
		array(),
		$ver,
		array( 'strategy' => 'defer', 'in_footer' => true ) // WP 6.3+
	);

	// Pass PHP data to JS safely:
	wp_localize_script( 'mytheme-nav', 'MyThemeData', array(
		'ajaxUrl' => admin_url( 'admin-ajax.php' ),
		'nonce'   => wp_create_nonce( 'mytheme_nonce' ),
	) );
}
```

Use `wp_get_theme()->get('Version')` (or `filemtime()` in dev) as the version so browsers refetch on change. For the primary stylesheet that carries the theme header, `get_stylesheet_uri()` points at `style.css`. Conditionally enqueue (e.g. only on `is_single()`) to keep pages lean — but remember conditionals only work this late, not at file top.

## 3. Internationalization (i18n)

Wrap every user-facing string so the theme can be translated. Retrofitting is painful, so do it from the first line.

Load the text domain (the slug, matching `style.css` Text Domain):
```php
add_action( 'after_setup_theme', function () {
	load_theme_textdomain( 'my-theme', get_template_directory() . '/languages' );
} );
```

Functions:
- `__( 'Text', 'my-theme' )` — returns the translated string.
- `_e( 'Text', 'my-theme' )` — echoes it.
- `esc_html__()` / `esc_html_e()` / `esc_attr__()` / `esc_attr_e()` — translate **and** escape. Prefer these when outputting, combining i18n with the escaping rule.
- `_n( 'one item', '%d items', $count, 'my-theme' )` — plurals.
- `_x()` / `esc_html_x()` — with context for ambiguous words.
- `sprintf()` with placeholders, never string concatenation:
```php
printf( esc_html__( 'Posted on %s', 'my-theme' ), esc_html( get_the_date() ) );
```

The text domain must be a literal string matching the header — variables there break the string-extraction tools.

## 4. The Settings API & Customizer

For theme options, prefer the **Customizer** (live preview) for visual settings.

```php
add_action( 'customize_register', 'mytheme_customize' );
function mytheme_customize( $wp_customize ) {
	$wp_customize->add_section( 'mytheme_colors', array(
		'title' => __( 'Theme Colors', 'my-theme' ),
	) );
	$wp_customize->add_setting( 'mytheme_accent', array(
		'default'           => '#1a73e8',
		'sanitize_callback' => 'sanitize_hex_color', // REQUIRED — sanitize on input
		'transport'         => 'refresh',
	) );
	$wp_customize->add_control( new WP_Customize_Color_Control(
		$wp_customize, 'mytheme_accent', array(
			'label'   => __( 'Accent Color', 'my-theme' ),
			'section' => 'mytheme_colors',
		)
	) );
}
```

Read with `get_theme_mod( 'mytheme_accent', '#1a73e8' )`. Every setting **must** have a `sanitize_callback` — that's the input-sanitization rule in practice. When you output the value, still escape it (`esc_attr`, etc.).

Block themes lean on `theme.json` and the Site Editor instead and rarely need the Customizer.

## 5. Nav menus

```php
// register (after_setup_theme)
register_nav_menus( array(
	'primary' => __( 'Primary', 'my-theme' ),
	'footer'  => __( 'Footer', 'my-theme' ),
) );

// render (classic template)
wp_nav_menu( array(
	'theme_location' => 'primary',
	'container'      => 'nav',
	'menu_class'     => 'primary-menu',
	'fallback_cb'    => false,
) );
```

Block themes use the Navigation block instead; no registration needed.

## 6. Widget / block areas

```php
add_action( 'widgets_init', function () {
	register_sidebar( array(
		'name'          => __( 'Sidebar', 'my-theme' ),
		'id'            => 'sidebar-1',
		'before_widget' => '<section id="%1$s" class="widget %2$s">',
		'after_widget'  => '</section>',
		'before_title'  => '<h2 class="widget-title">',
		'after_title'   => '</h2>',
	) );
} );
// render: if ( is_active_sidebar( 'sidebar-1' ) ) dynamic_sidebar( 'sidebar-1' );
```

## 7. pre_get_posts

To change *which* posts the main query returns (posts per page on an archive, including a CPT in the blog, reordering), filter the main query — don't run a `new WP_Query` in the template and don't use `query_posts()`.

```php
add_action( 'pre_get_posts', function ( $query ) {
	if ( ! is_admin() && $query->is_main_query() && is_post_type_archive( 'product' ) ) {
		$query->set( 'posts_per_page', 12 );
		$query->set( 'orderby', 'title' );
	}
} );
```

The `! is_admin()` and `is_main_query()` guards are essential — without them you'll alter admin queries and every secondary query too.
