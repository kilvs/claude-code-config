#!/usr/bin/env python3
"""Scaffold a block (FSE) WordPress theme.

Emits an activatable block theme: style.css header, a valid theme.json,
templates/ (index, single, page, archive, 404), parts/ (header, footer),
a sample pattern, and a lean functions.php.

Usage:
    python scaffold_block.py --name "My Theme" --slug my-theme --output ./out
    python scaffold_block.py --name "Child" --slug my-child --output ./out \\
        --child --parent twentytwentyfour

Run with --help for all options.
"""
import argparse
import json
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
    ap = argparse.ArgumentParser(description="Scaffold a block (FSE) WordPress theme.")
    ap.add_argument("--name", required=True)
    ap.add_argument("--slug", required=True, help="Folder slug + text domain (lowercase-hyphenated)")
    ap.add_argument("--output", required=True)
    ap.add_argument("--author", default="Your Name")
    ap.add_argument("--author-uri", default="https://example.com")
    ap.add_argument("--theme-uri", default="https://example.com")
    ap.add_argument("--description", default="A custom block theme.")
    ap.add_argument("--version", default="1.0.0")
    ap.add_argument("--wp-min", default="6.4")
    ap.add_argument("--php-min", default="7.4")
    ap.add_argument("--schema", type=int, default=3, choices=[2, 3], help="theme.json schema version")
    ap.add_argument("--child", action="store_true")
    ap.add_argument("--parent", default="")
    ap.add_argument("--with-samples", action="store_true",
                    help="Include example palette/fonts/sizes and a hero pattern. "
                         "Default is minimal: empty presets and no opinionated global styles, "
                         "so you set brand color, container size, fonts, etc. yourself.")
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
{template_line}Tags: full-site-editing, block-patterns, translation-ready
*/
"""
    write(os.path.join(root, "style.css"), style_css)

    if args.with_samples:
        settings = {
            "appearanceTools": True,
            "layout": {"contentSize": "640px", "wideSize": "1200px"},
            "color": {
                "palette": [
                    {"slug": "base", "color": "#ffffff", "name": "Base"},
                    {"slug": "contrast", "color": "#111111", "name": "Contrast"},
                    {"slug": "primary", "color": "#1a73e8", "name": "Primary"},
                ],
                "custom": True,
                "customDuotone": False,
            },
            "typography": {
                "fluid": True,
                "fontFamilies": [
                    {"slug": "body", "name": "Body", "fontFamily": "system-ui, -apple-system, sans-serif"},
                    {"slug": "heading", "name": "Heading", "fontFamily": "Georgia, serif"},
                ],
                "fontSizes": [
                    {"slug": "small", "size": "0.875rem", "name": "Small"},
                    {"slug": "medium", "size": "1rem", "name": "Medium"},
                    {"slug": "large", "size": "1.5rem", "name": "Large"},
                    {"slug": "x-large", "size": "2.25rem", "name": "Extra Large"},
                ],
            },
            "spacing": {
                "spacingScale": {"steps": 7},
                "units": ["px", "em", "rem", "vh", "vw", "%"],
            },
        }
        styles = {
            "color": {
                "background": "var(--wp--preset--color--base)",
                "text": "var(--wp--preset--color--contrast)",
            },
            "typography": {
                "fontFamily": "var(--wp--preset--font-family--body)",
                "fontSize": "var(--wp--preset--font-size--medium)",
                "lineHeight": "1.6",
            },
            "elements": {
                "link": {"color": {"text": "var(--wp--preset--color--primary)"}},
                "heading": {"typography": {"fontFamily": "var(--wp--preset--font-family--heading)", "fontWeight": "700"}},
                "button": {
                    "color": {
                        "background": "var(--wp--preset--color--primary)",
                        "text": "var(--wp--preset--color--base)",
                    }
                },
            },
        }
    else:
        # Minimal: valid structure, no brand opinions. You fill these in.
        # appearanceTools stays on so the editor shows the controls; presets are
        # empty arrays (valid, and they disable WP's default palette/sizes so the
        # editor isn't cluttered with values you didn't choose). layout is omitted
        # so you set contentSize/wideSize deliberately. No `styles` block, so no
        # color/font is assigned until you decide.
        settings = {
            "appearanceTools": True,
            "color": {
                "palette": [],
                "defaultPalette": False,
                "defaultDuotone": False,
                "defaultGradients": False,
            },
            "typography": {
                "fontFamilies": [],
                "fontSizes": [],
                "defaultFontSizes": False,
            },
            "spacing": {
                "units": ["px", "em", "rem", "vh", "vw", "%"],
            },
        }
        styles = {}

    theme_json = {
        "$schema": "https://schemas.wp.org/trunk/theme.json",
        "version": args.schema,
        "settings": settings,
        "templateParts": [
            {"name": "header", "title": "Header", "area": "header"},
            {"name": "footer", "title": "Footer", "area": "footer"},
        ],
    }
    if styles:
        theme_json["styles"] = styles
    write(os.path.join(root, "theme.json"), json.dumps(theme_json, indent="\t") + "\n")

    if args.child:
        functions = f"""<?php
defined( 'ABSPATH' ) || exit;

add_action( 'wp_enqueue_scripts', '{pre}_styles' );
function {pre}_styles() {{
\twp_enqueue_style( '{pre}-style', get_stylesheet_uri(), array(), wp_get_theme()->get( 'Version' ) );
}}
"""
        write(os.path.join(root, "functions.php"), functions)
        write(os.path.join(root, ".gitignore"), GITIGNORE)
        print(f"Block child theme scaffolded at {root} (parent: {args.parent})")
        print("Override parent templates by adding HTML files in templates/ or parts/, or a partial theme.json.")
        return 0

    header_part = f"""<!-- wp:group {{"tagName":"header","layout":{{"type":"constrained"}}}} -->
<header class="wp-block-group">
\t<!-- wp:group {{"layout":{{"type":"flex","justifyContent":"space-between"}}}} -->
\t<div class="wp-block-group">
\t\t<!-- wp:site-title /-->
\t\t<!-- wp:navigation /-->
\t</div>
\t<!-- /wp:group -->
</header>
<!-- /wp:group -->
"""
    write(os.path.join(root, "parts", "header.html"), header_part)

    footer_part = f"""<!-- wp:group {{"tagName":"footer","layout":{{"type":"constrained"}}}} -->
<footer class="wp-block-group">
\t<!-- wp:paragraph {{"align":"center"}} -->
\t<p class="has-text-align-center">&copy; <!-- wp:post-date /--> <!-- wp:site-title {{"isLink":false}} /--></p>
\t<!-- /wp:paragraph -->
</footer>
<!-- /wp:group -->
"""
    write(os.path.join(root, "parts", "footer.html"), footer_part)

    index_tpl = f"""<!-- wp:template-part {{"slug":"header","area":"header","tagName":"header"}} /-->

<!-- wp:group {{"tagName":"main","layout":{{"type":"constrained"}}}} -->
<main class="wp-block-group">
\t<!-- wp:query {{"queryId":1,"query":{{"perPage":10,"postType":"post","inherit":true}}}} -->
\t<div class="wp-block-query">
\t\t<!-- wp:post-template -->
\t\t\t<!-- wp:post-title {{"isLink":true,"level":2}} /-->
\t\t\t<!-- wp:post-excerpt /-->
\t\t<!-- /wp:post-template -->
\t\t<!-- wp:query-pagination -->
\t\t\t<!-- wp:query-pagination-previous /-->
\t\t\t<!-- wp:query-pagination-numbers /-->
\t\t\t<!-- wp:query-pagination-next /-->
\t\t<!-- /wp:query-pagination -->
\t\t<!-- wp:query-no-results -->
\t\t\t<!-- wp:paragraph -->
\t\t\t<p>Nothing found.</p>
\t\t\t<!-- /wp:paragraph -->
\t\t<!-- /wp:query-no-results -->
\t</div>
\t<!-- /wp:query -->
</main>
<!-- /wp:group -->

<!-- wp:template-part {{"slug":"footer","area":"footer","tagName":"footer"}} /-->
"""
    write(os.path.join(root, "templates", "index.html"), index_tpl)

    single_tpl = f"""<!-- wp:template-part {{"slug":"header","area":"header","tagName":"header"}} /-->

<!-- wp:group {{"tagName":"main","layout":{{"type":"constrained"}}}} -->
<main class="wp-block-group">
\t<!-- wp:post-title {{"level":1}} /-->
\t<!-- wp:post-featured-image /-->
\t<!-- wp:post-content /-->
\t<!-- wp:comments -->
\t<div class="wp-block-comments">
\t\t<!-- wp:comment-template -->
\t\t\t<!-- wp:comment-author-name /-->
\t\t\t<!-- wp:comment-content /-->
\t\t<!-- /wp:comment-template -->
\t</div>
\t<!-- /wp:comments -->
</main>
<!-- /wp:group -->

<!-- wp:template-part {{"slug":"footer","area":"footer","tagName":"footer"}} /-->
"""
    write(os.path.join(root, "templates", "single.html"), single_tpl)

    page_tpl = f"""<!-- wp:template-part {{"slug":"header","area":"header","tagName":"header"}} /-->

<!-- wp:group {{"tagName":"main","layout":{{"type":"constrained"}}}} -->
<main class="wp-block-group">
\t<!-- wp:post-title {{"level":1}} /-->
\t<!-- wp:post-content /-->
</main>
<!-- /wp:group -->

<!-- wp:template-part {{"slug":"footer","area":"footer","tagName":"footer"}} /-->
"""
    write(os.path.join(root, "templates", "page.html"), page_tpl)

    archive_tpl = f"""<!-- wp:template-part {{"slug":"header","area":"header","tagName":"header"}} /-->

<!-- wp:group {{"tagName":"main","layout":{{"type":"constrained"}}}} -->
<main class="wp-block-group">
\t<!-- wp:query-title {{"type":"archive"}} /-->
\t<!-- wp:query {{"queryId":2,"query":{{"perPage":10,"postType":"post","inherit":true}}}} -->
\t<div class="wp-block-query">
\t\t<!-- wp:post-template -->
\t\t\t<!-- wp:post-title {{"isLink":true,"level":2}} /-->
\t\t\t<!-- wp:post-excerpt /-->
\t\t<!-- /wp:post-template -->
\t\t<!-- wp:query-pagination -->
\t\t\t<!-- wp:query-pagination-previous /-->
\t\t\t<!-- wp:query-pagination-next /-->
\t\t<!-- /wp:query-pagination -->
\t</div>
\t<!-- /wp:query -->
</main>
<!-- /wp:group -->

<!-- wp:template-part {{"slug":"footer","area":"footer","tagName":"footer"}} /-->
"""
    write(os.path.join(root, "templates", "archive.html"), archive_tpl)

    notfound_tpl = f"""<!-- wp:template-part {{"slug":"header","area":"header","tagName":"header"}} /-->

<!-- wp:group {{"tagName":"main","layout":{{"type":"constrained"}}}} -->
<main class="wp-block-group">
\t<!-- wp:heading {{"level":1}} -->
\t<h1>Page not found</h1>
\t<!-- /wp:heading -->
\t<!-- wp:search {{"label":"Search","buttonText":"Search"}} /-->
</main>
<!-- /wp:group -->

<!-- wp:template-part {{"slug":"footer","area":"footer","tagName":"footer"}} /-->
"""
    write(os.path.join(root, "templates", "404.html"), notfound_tpl)

    if args.with_samples:
        pattern = f"""<?php
/**
 * Title: Hero
 * Slug: {args.slug}/hero
 * Categories: featured, {args.slug}
 * Description: Full-width hero with heading and call-to-action button.
 */
?>
<!-- wp:cover {{"minHeight":420,"layout":{{"type":"constrained"}}}} -->
<div class="wp-block-cover">
\t<div class="wp-block-cover__inner-container">
\t\t<!-- wp:heading {{"level":1,"textAlign":"center"}} -->
\t\t<h1 class="has-text-align-center"><?php echo esc_html__( 'Welcome', '{args.slug}' ); ?></h1>
\t\t<!-- /wp:heading -->
\t\t<!-- wp:buttons {{"layout":{{"type":"flex","justifyContent":"center"}}}} -->
\t\t<div class="wp-block-buttons">
\t\t\t<!-- wp:button -->
\t\t\t<div class="wp-block-button"><a class="wp-block-button__link wp-element-button"><?php echo esc_html__( 'Get started', '{args.slug}' ); ?></a></div>
\t\t\t<!-- /wp:button -->
\t\t</div>
\t\t<!-- /wp:buttons -->
\t</div>
</div>
<!-- /wp:cover -->
"""
        write(os.path.join(root, "patterns", "hero.php"), pattern)

    # Pattern category registration only matters if a sample pattern uses it.
    pattern_cat_block = f"""

add_action( 'init', '{pre}_pattern_categories' );
function {pre}_pattern_categories() {{
\tregister_block_pattern_category( '{args.slug}', array( 'label' => __( '{args.name}', '{args.slug}' ) ) );
}}
""" if args.with_samples else ""

    functions = f"""<?php
/**
 * {args.name} — block theme setup.
 *
 * @package {pre}
 */

defined( 'ABSPATH' ) || exit;

add_action( 'after_setup_theme', '{pre}_setup' );
function {pre}_setup() {{
\tload_theme_textdomain( '{args.slug}', get_template_directory() . '/languages' );
\tadd_theme_support( 'wp-block-styles' );
\tadd_theme_support( 'editor-styles' );
\tadd_theme_support( 'responsive-embeds' );
}}

add_action( 'wp_enqueue_scripts', '{pre}_styles' );
function {pre}_styles() {{
\twp_enqueue_style( '{pre}-style', get_stylesheet_uri(), array(), wp_get_theme()->get( 'Version' ) );
}}{pattern_cat_block}"""
    write(os.path.join(root, "functions.php"), functions)

    write(os.path.join(root, "languages", f"{args.slug}.pot"),
          "# Translation template. Generate with WP-CLI: wp i18n make-pot . languages/" + args.slug + ".pot\n")
    write(os.path.join(root, ".gitignore"), GITIGNORE)

    samples_note = " (with samples)" if args.with_samples else " (minimal — empty presets, no global styles set)"
    print(f"Block theme scaffolded at {root}{samples_note}")
    file_list = "style.css, theme.json, templates/, parts/, functions.php, languages/"
    if args.with_samples:
        file_list += ", patterns/hero.php"
    print("Files: " + file_list)
    print(f"Schema version: {args.schema}  |  Text domain: {args.slug}")
    if not args.with_samples:
        print("theme.json ships empty: set your palette, contentSize/wideSize, and fontFamilies/fontSizes yourself.")
    print("Next: read references/block-themes.md before editing theme.json or templates.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
