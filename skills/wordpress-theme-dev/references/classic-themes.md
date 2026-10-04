# Classic (PHP) Themes

Reference for traditional template-file themes. For block/FSE themes see `block-themes.md`. For hooks, enqueueing, i18n details see `wp-apis.md`.

## Contents
1. Required & common files
2. The template hierarchy (how WP picks a file)
3. The Loop
4. Conditional tags
5. Template tags & partials
6. functions.php patterns

---

## 1. Required & common files

A classic theme needs at minimum `style.css` (with the header comment) and `index.php`. Everything else is optional but conventional.

```
my-theme/
├── style.css          REQUIRED — header comment identifies the theme; can hold CSS too
├── index.php          REQUIRED — ultimate fallback template
├── functions.php      theme setup, enqueueing, supports, hooks
├── header.php         get_header() loads this
├── footer.php         get_footer() loads this
├── sidebar.php        get_sidebar() loads this
├── front-page.php     static front page
├── home.php           blog posts index
├── single.php         single post
├── page.php           single page
├── archive.php        category/tag/date/author archives
├── search.php         search results
├── 404.php            not found
├── comments.php       comments template
├── screenshot.png     1200x900 recommended, shown in admin
├── template-parts/    reusable partials (content.php, content-none.php, etc.)
└── assets/            css/, js/, images/, fonts/
```

`style.css` header (required fields are Theme Name; the rest are strongly recommended):

```css
/*
Theme Name: My Theme
Theme URI: https://example.com/my-theme
Author: Your Name
Author URI: https://example.com
Description: A custom theme.
Version: 1.0.0
Requires at least: 6.0
Tested up to: 6.5
Requires PHP: 7.4
License: GNU General Public License v2 or later
License URI: http://www.gnu.org/licenses/gpl-2.0.html
Text Domain: my-theme
Tags: custom-background, custom-logo, custom-menu, featured-images
*/
```

For a **child theme**, add `Template: parent-theme-slug` to the header — that line is what makes it a child.

## 2. The template hierarchy

WordPress decides which template file to load based on the type of page requested, walking from most specific to least specific and using the first file that exists. `index.php` always catches what nothing else does. Understanding this is the core skill of classic theming — it's why you rarely need conditional logic for "what kind of page is this."

Key paths (most-specific → fallback):

- **Single post**: `single-{post-type}-{slug}.php` → `single-{post-type}.php` → `single.php` → `singular.php` → `index.php`
- **Page**: `{custom-template}.php` → `page-{slug}.php` → `page-{id}.php` → `page.php` → `singular.php` → `index.php`
- **Category**: `category-{slug}.php` → `category-{id}.php` → `category.php` → `archive.php` → `index.php`
- **Tag**: `tag-{slug}.php` → `tag-{id}.php` → `tag.php` → `archive.php` → `index.php`
- **Custom taxonomy**: `taxonomy-{tax}-{term}.php` → `taxonomy-{tax}.php` → `taxonomy.php` → `archive.php` → `index.php`
- **Custom post type archive**: `archive-{post-type}.php` → `archive.php` → `index.php`
- **Author**: `author-{nicename}.php` → `author-{id}.php` → `author.php` → `archive.php` → `index.php`
- **Date**: `date.php` → `archive.php` → `index.php`
- **Search**: `search.php` → `index.php`
- **404**: `404.php` → `index.php`
- **Front page**: `front-page.php` → (then home or page logic)
- **Blog index**: `home.php` → `index.php`
- **Attachment**: `{mime-type}.php` → `attachment.php` → `single-attachment.php` → `single.php` → `index.php`

Practical consequence: to style "all archives one way but the News category specially," you just create `category-news.php` and `archive.php`. No `if` needed.

## 3. The Loop

The Loop is how WordPress iterates the posts matched by the current query and renders each one. Nearly every template contains one.

```php
<?php if ( have_posts() ) : ?>
	<?php while ( have_posts() ) : the_post(); ?>
		<article id="post-<?php the_ID(); ?>" <?php post_class(); ?>>
			<h2><a href="<?php the_permalink(); ?>"><?php the_title(); ?></a></h2>
			<div class="entry-content"><?php the_content(); ?></div>
		</article>
	<?php endwhile; ?>
	<?php the_posts_pagination(); ?>
<?php else : ?>
	<p><?php esc_html_e( 'Nothing found.', 'my-theme' ); ?></p>
<?php endif; ?>
```

Notes that bite people:
- `the_post()` sets up the global `$post` and the template tags (`the_title()`, `the_content()`, etc.). Without it those tags return nothing.
- Output tags `the_*()` echo and are pre-escaped by core for their context. The `get_the_*()` variants return a value — escape those yourself before echoing.
- For a *secondary* query, use `WP_Query` and **always** `wp_reset_postdata()` after, or later template tags read the wrong post.

```php
$q = new WP_Query( array( 'post_type' => 'product', 'posts_per_page' => 6 ) );
if ( $q->have_posts() ) {
	while ( $q->have_posts() ) { $q->the_post();
		/* ... */
	}
	wp_reset_postdata();
}
```

Never use `query_posts()` — it overrides the main query and breaks pagination/conditionals. To modify the main query, hook `pre_get_posts` (see `wp-apis.md`).

## 4. Conditional tags

Used to branch behavior, most often inside `functions.php` hooks rather than templates (since the hierarchy handles most template selection). Common ones: `is_front_page()`, `is_home()`, `is_single()`, `is_page()`, `is_singular()`, `is_archive()`, `is_category()`, `is_tag()`, `is_tax()`, `is_search()`, `is_404()`, `is_admin()`, `is_user_logged_in()`, `in_the_loop()`.

Gotcha: most conditionals only work after the main query runs (`wp` action onward). Calling `is_page()` too early (e.g. in `functions.php` top level) returns false.

## 5. Template tags & partials

Load shared chunks with `get_header()`, `get_footer()`, `get_sidebar()`, and the flexible `get_template_part()`:

```php
get_template_part( 'template-parts/content', get_post_type() );
// loads template-parts/content-{post-type}.php, falling back to content.php
```

Pass data (WP 5.5+):
```php
get_template_part( 'template-parts/card', null, array( 'featured' => true ) );
// inside card.php: $args['featured']
```

Always echo paths through the URI helpers and escape:
```php
<img src="<?php echo esc_url( get_theme_file_uri( 'assets/images/logo.svg' ) ); ?>" alt="">
```

## 6. functions.php patterns

`functions.php` runs on every request. Keep it lean; split large concerns into `inc/` files. The scaffold auto-requires every `*.php` in `inc/` (alphabetical order), so you add modular files by dropping them in rather than editing `functions.php` each time. Standard setup skeleton:

```php
<?php
defined( 'ABSPATH' ) || exit;

if ( ! function_exists( 'mytheme_setup' ) ) {
	function mytheme_setup() {
		load_theme_textdomain( 'my-theme', get_template_directory() . '/languages' );
		add_theme_support( 'title-tag' );
		add_theme_support( 'post-thumbnails' );
		add_theme_support( 'html5', array( 'search-form', 'comment-form', 'comment-list', 'gallery', 'caption', 'style', 'script' ) );
		add_theme_support( 'custom-logo' );
		add_theme_support( 'automatic-feed-links' );
		add_theme_support( 'responsive-embeds' );
		register_nav_menus( array(
			'primary' => __( 'Primary Menu', 'my-theme' ),
		) );
	}
}
add_action( 'after_setup_theme', 'mytheme_setup' );
```

Enqueueing, the Settings API, and the hooks system all live in `wp-apis.md` — read it before wiring those up. The single most common `functions.php` mistake is enqueueing assets without hooking into `wp_enqueue_scripts`, or hardcoding asset URLs instead of using `get_theme_file_uri()`.
