#!/usr/bin/env python3
"""Scaffold a classic (PHP) WordPress theme, _s-style.

Emits an activatable theme with a complete style.css header, security-clean
templates, prefixed functions, hooked enqueueing, and i18n wiring.

Usage:
    python scaffold_classic.py --name "My Theme" --slug my-theme --output ./out
    python scaffold_classic.py --name "Child" --slug my-child --output ./out \\
        --child --parent twentytwentyfour

Run with --help for all options.
"""
import argparse
import os
import re
import sys


def php_prefix(slug: str) -> str:
    p = re.sub(r"[^a-z0-9]+", "_", slug.lower()).strip("_")
    if not p or p[0].isdigit():
        p = "theme_" + p
    return p


GITIGNORE = """# Dependencies
/node_modules/
/vendor/

# Build artifacts
*.css.map
.sass-cache/

# OS / editor
.DS_Store
Thumbs.db
.idea/
.vscode/
*.sublime-*

# Logs / local env
*.log
debug.log
.env
.env.*
"""


def write(path: str, content: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def main() -> int:
    ap = argparse.ArgumentParser(description="Scaffold a classic WordPress theme.")
    ap.add_argument("--name", required=True, help="Theme display name")
    ap.add_argument("--slug", required=True, help="Theme folder slug + text domain (lowercase-hyphenated)")
    ap.add_argument("--output", required=True, help="Output directory (theme folder created inside)")
    ap.add_argument("--author", default="Your Name")
    ap.add_argument("--author-uri", default="https://example.com")
    ap.add_argument("--theme-uri", default="https://example.com")
    ap.add_argument("--description", default="A custom WordPress theme.")
    ap.add_argument("--version", default="1.0.0")
    ap.add_argument("--wp-min", default="6.0")
    ap.add_argument("--php-min", default="7.4")
    ap.add_argument("--child", action="store_true", help="Generate a child theme")
    ap.add_argument("--parent", default="", help="Parent theme slug (required with --child)")
    ap.add_argument("--with-samples", action="store_true",
                    help="Include decorative theme supports (custom-logo, align-wide). "
                         "Default is minimal: only essential supports, so you decide global styling yourself.")
    args = ap.parse_args()

    if args.child and not args.parent:
        ap.error("--parent is required when using --child")

    pre = php_prefix(args.slug)
    root = os.path.join(args.output, args.slug)
    if os.path.exists(root):
        print(f"Error: {root} already exists.", file=sys.stderr)
        return 1

    template_line = f"Template: {args.parent}\n" if args.child else ""
    style_css = f"""/*
Theme Name: {args.name}
Theme URI: {args.theme_uri}
Author: {args.author}
Author URI: {args.author_uri}
Description: {args.description}
Version: {args.version}
Requires at least: {args.wp_min}
Tested up to: {args.wp_min}
Requires PHP: {args.php_min}
License: GNU General Public License v2 or later
License URI: http://www.gnu.org/licenses/gpl-2.0.html
Text Domain: {args.slug}
{template_line}Tags: custom-menu, featured-images, translation-ready
*/
"""
    write(os.path.join(root, "style.css"), style_css)

    if args.child:
        # Child theme: minimal functions.php that enqueues parent + child styles.
        functions = f"""<?php
defined( 'ABSPATH' ) || exit;

add_action( 'wp_enqueue_scripts', '{pre}_enqueue' );
function {pre}_enqueue() {{
\t$parent = 'parent-style';
\twp_enqueue_style( $parent, get_template_directory_uri() . '/style.css', array(), wp_get_theme()->parent()->get( 'Version' ) );
\twp_enqueue_style( '{pre}-style', get_stylesheet_uri(), array( $parent ), wp_get_theme()->get( 'Version' ) );
}}
"""
        write(os.path.join(root, "functions.php"), functions)
        write(os.path.join(root, ".gitignore"), GITIGNORE)
        print(f"Child theme scaffolded at {root} (parent: {args.parent})")
        print("Next: add overriding template files as needed; they take precedence over the parent.")
        return 0

    # Essential supports only by default; decorative ones are opt-in via --with-samples.
    supports = [
        "\t\tadd_theme_support( 'automatic-feed-links' );",
        "\t\tadd_theme_support( 'title-tag' );",
        "\t\tadd_theme_support( 'post-thumbnails' );",
        "\t\tadd_theme_support( 'html5', array( 'search-form', 'comment-form', 'comment-list', 'gallery', 'caption', 'style', 'script' ) );",
    ]
    if args.with_samples:
        supports += [
            "\t\tadd_theme_support( 'custom-logo' );",
            "\t\tadd_theme_support( 'responsive-embeds' );",
            "\t\tadd_theme_support( 'align-wide' );",
        ]
    supports_block = "\n".join(supports)

    functions = f"""<?php
/**
 * {args.name} functions and definitions.
 *
 * @package {pre}
 */

defined( 'ABSPATH' ) || exit;

if ( ! defined( '{pre.upper()}_VERSION' ) ) {{
\tdefine( '{pre.upper()}_VERSION', wp_get_theme()->get( 'Version' ) );
}}

if ( ! function_exists( '{pre}_setup' ) ) {{
\tfunction {pre}_setup() {{
\t\tload_theme_textdomain( '{args.slug}', get_template_directory() . '/languages' );
{supports_block}
\t\tregister_nav_menus( array(
\t\t\t'primary' => __( 'Primary Menu', '{args.slug}' ),
\t\t) );
\t}}
}}
add_action( 'after_setup_theme', '{pre}_setup' );

function {pre}_assets() {{
\twp_enqueue_style( '{pre}-style', get_stylesheet_uri(), array(), {pre.upper()}_VERSION );
\twp_enqueue_style( '{pre}-main', get_theme_file_uri( 'assets/css/main.css' ), array(), {pre.upper()}_VERSION );
\tif ( is_singular() && comments_open() && get_option( 'thread_comments' ) ) {{
\t\twp_enqueue_script( 'comment-reply' );
\t}}
}}
add_action( 'wp_enqueue_scripts', '{pre}_assets' );

function {pre}_widgets_init() {{
\tregister_sidebar( array(
\t\t'name'          => __( 'Sidebar', '{args.slug}' ),
\t\t'id'            => 'sidebar-1',
\t\t'before_widget' => '<section id="%1$s" class="widget %2$s">',
\t\t'after_widget'  => '</section>',
\t\t'before_title'  => '<h2 class="widget-title">',
\t\t'after_title'   => '</h2>',
\t) );
}}
add_action( 'widgets_init', '{pre}_widgets_init' );

/**
 * Autoload everything in /inc.
 *
 * Drop a file in the inc/ directory (e.g. inc/property.php to register a custom
 * post type, inc/fields.php for ACF/Carbon Fields, inc/blocks.php for block
 * registration) and it is required automatically — no need to edit this file
 * each time. Files load in alphabetical order; name them accordingly if order
 * matters. Each included file should start with its own `defined( 'ABSPATH' ) || exit;`.
 */
foreach ( glob( get_template_directory() . '/inc/*.php' ) as $_inc_file ) {{
\trequire_once $_inc_file;
}}
unset( $_inc_file );
"""
    write(os.path.join(root, "functions.php"), functions)
    # inc/ ships empty but present, so dropping files in "just works" via the autoload above.
    write(os.path.join(root, "inc", "README.md"),
          "# inc/\n\nFiles here are auto-required by functions.php (alphabetical order).\n"
          "Put custom post types, field registration (ACF/Carbon Fields), block registration,\n"
          "and other modular concerns here, one concern per file. Start each file with\n"
          "`defined( 'ABSPATH' ) || exit;`.\n")

    header = f"""<?php
/**
 * The header.
 *
 * @package {pre}
 */

defined( 'ABSPATH' ) || exit;
?>
<!DOCTYPE html>
<html <?php language_attributes(); ?>>
<head>
\t<meta charset="<?php bloginfo( 'charset' ); ?>">
\t<meta name="viewport" content="width=device-width, initial-scale=1">
\t<?php wp_head(); ?>
</head>

<body <?php body_class(); ?>>
<?php wp_body_open(); ?>
<header class="site-header">
\t<?php if ( has_custom_logo() ) {{ the_custom_logo(); }} else {{ ?>
\t\t<a class="site-title" href="<?php echo esc_url( home_url( '/' ) ); ?>"><?php bloginfo( 'name' ); ?></a>
\t<?php }} ?>
\t<nav class="primary-nav">
\t\t<?php
\t\twp_nav_menu( array(
\t\t\t'theme_location' => 'primary',
\t\t\t'container'      => false,
\t\t\t'fallback_cb'    => false,
\t\t) );
\t\t?>
\t</nav>
</header>
<main id="content" class="site-main">
"""
    write(os.path.join(root, "header.php"), header)

    footer = f"""<?php
/**
 * The footer.
 *
 * @package {pre}
 */

defined( 'ABSPATH' ) || exit;
?>
</main>
<footer class="site-footer">
\t<p>&copy; <?php echo esc_html( gmdate( 'Y' ) ); ?> <?php bloginfo( 'name' ); ?></p>
</footer>
<?php wp_footer(); ?>
</body>
</html>
"""
    write(os.path.join(root, "footer.php"), footer)

    index = f"""<?php
/**
 * Main template — ultimate fallback in the hierarchy.
 *
 * @package {pre}
 */

defined( 'ABSPATH' ) || exit;

get_header();
?>
<?php if ( have_posts() ) : ?>
\t<?php while ( have_posts() ) : the_post(); ?>
\t\t<?php get_template_part( 'template-parts/content', get_post_type() ); ?>
\t<?php endwhile; ?>
\t<?php the_posts_pagination(); ?>
<?php else : ?>
\t<?php get_template_part( 'template-parts/content', 'none' ); ?>
<?php endif; ?>
<?php
get_footer();
"""
    write(os.path.join(root, "index.php"), index)

    single = f"""<?php
/**
 * Single post template.
 *
 * @package {pre}
 */

defined( 'ABSPATH' ) || exit;

get_header();
?>
<?php while ( have_posts() ) : the_post(); ?>
\t<article id="post-<?php the_ID(); ?>" <?php post_class(); ?>>
\t\t<h1 class="entry-title"><?php the_title(); ?></h1>
\t\t<div class="entry-meta"><?php printf( esc_html__( 'Posted on %s', '{args.slug}' ), esc_html( get_the_date() ) ); ?></div>
\t\t<?php if ( has_post_thumbnail() ) {{ the_post_thumbnail( 'large' ); }} ?>
\t\t<div class="entry-content"><?php the_content(); ?></div>
\t</article>
\t<?php if ( comments_open() || get_comments_number() ) {{ comments_template(); }} ?>
<?php endwhile; ?>
<?php
get_footer();
"""
    write(os.path.join(root, "single.php"), single)

    page = f"""<?php
/**
 * Single page template.
 *
 * @package {pre}
 */

defined( 'ABSPATH' ) || exit;

get_header();
?>
<?php while ( have_posts() ) : the_post(); ?>
\t<article id="post-<?php the_ID(); ?>" <?php post_class(); ?>>
\t\t<h1 class="entry-title"><?php the_title(); ?></h1>
\t\t<div class="entry-content"><?php the_content(); ?></div>
\t</article>
<?php endwhile; ?>
<?php
get_footer();
"""
    write(os.path.join(root, "page.php"), page)

    archive = f"""<?php
/**
 * Archive template.
 *
 * @package {pre}
 */

defined( 'ABSPATH' ) || exit;

get_header();
?>
<?php if ( have_posts() ) : ?>
\t<header class="page-header"><h1 class="page-title"><?php the_archive_title(); ?></h1></header>
\t<?php while ( have_posts() ) : the_post(); ?>
\t\t<?php get_template_part( 'template-parts/content', get_post_type() ); ?>
\t<?php endwhile; ?>
\t<?php the_posts_pagination(); ?>
<?php else : ?>
\t<?php get_template_part( 'template-parts/content', 'none' ); ?>
<?php endif; ?>
<?php
get_footer();
"""
    write(os.path.join(root, "archive.php"), archive)

    search = f"""<?php
/**
 * Search results template.
 *
 * @package {pre}
 */

defined( 'ABSPATH' ) || exit;

get_header();
?>
<header class="page-header">
\t<h1 class="page-title">
\t\t<?php printf( esc_html__( 'Search results for: %s', '{args.slug}' ), '<span>' . esc_html( get_search_query() ) . '</span>' ); ?>
\t</h1>
</header>
<?php if ( have_posts() ) : ?>
\t<?php while ( have_posts() ) : the_post(); ?>
\t\t<?php get_template_part( 'template-parts/content', 'search' ); ?>
\t<?php endwhile; ?>
\t<?php the_posts_pagination(); ?>
<?php else : ?>
\t<?php get_template_part( 'template-parts/content', 'none' ); ?>
<?php endif; ?>
<?php
get_footer();
"""
    write(os.path.join(root, "search.php"), search)

    notfound = f"""<?php
/**
 * 404 template.
 *
 * @package {pre}
 */

defined( 'ABSPATH' ) || exit;

get_header();
?>
<section class="error-404 not-found">
\t<h1 class="page-title"><?php esc_html_e( 'Page not found', '{args.slug}' ); ?></h1>
\t<p><?php esc_html_e( 'The page you were looking for is not here.', '{args.slug}' ); ?></p>
\t<?php get_search_form(); ?>
</section>
<?php
get_footer();
"""
    write(os.path.join(root, "404.php"), notfound)

    content = f"""<?php
/**
 * Default content partial.
 *
 * @package {pre}
 */

defined( 'ABSPATH' ) || exit;
?>
<article id="post-<?php the_ID(); ?>" <?php post_class(); ?>>
\t<h2 class="entry-title"><a href="<?php the_permalink(); ?>"><?php the_title(); ?></a></h2>
\t<?php if ( has_post_thumbnail() ) {{ ?>
\t\t<a href="<?php the_permalink(); ?>"><?php the_post_thumbnail( 'medium' ); ?></a>
\t<?php }} ?>
\t<div class="entry-summary"><?php the_excerpt(); ?></div>
</article>
"""
    write(os.path.join(root, "template-parts", "content.php"), content)

    content_none = f"""<?php
/**
 * "Nothing found" partial.
 *
 * @package {pre}
 */

defined( 'ABSPATH' ) || exit;
?>
<section class="no-results not-found">
\t<h2><?php esc_html_e( 'Nothing found', '{args.slug}' ); ?></h2>
\t<p><?php esc_html_e( 'No content matched your request.', '{args.slug}' ); ?></p>
\t<?php get_search_form(); ?>
</section>
"""
    write(os.path.join(root, "template-parts", "content-none.php"), content_none)

    write(os.path.join(root, "assets", "css", "main.css"),
          f"/* {args.name} — front-end styles. Compile from assets/scss/ if using SCSS. */\n")
    write(os.path.join(root, "assets", "js", ".gitkeep"), "")
    write(os.path.join(root, "languages", f"{args.slug}.pot"),
          "# Translation template. Generate with WP-CLI: wp i18n make-pot . languages/" + args.slug + ".pot\n")
    write(os.path.join(root, ".gitignore"), GITIGNORE)

    print(f"Classic theme scaffolded at {root}")
    print("Files: style.css, functions.php, header/footer, index/single/page/archive/search/404, template-parts/, assets/, languages/")
    print(f"Function prefix: {pre}_  |  Text domain: {args.slug}")
    print("Next: read references/classic-themes.md and references/wp-apis.md before customizing.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
