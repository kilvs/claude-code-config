# Client-First Naming for Classic WordPress Themes

Finsweet's Client-First is a **Webflow** class-naming system. This file explains how to carry its *naming convention* and *structure classes* into a hand-coded classic WordPress theme's markup and stylesheet — and, just as importantly, where the adaptation stops making sense. For the full Client-First system as used in Webflow itself, the installed **webflow-ui-design** skill is the authority; this file is only about the WordPress port.

## Contents
1. What ports and what doesn't
2. The structure classes (Client-First v2.1)
3. Naming convention rules
4. Applying it in PHP templates
5. The stylesheet side
6. When NOT to use this (block themes)

---

## 1. What ports and what doesn't

Client-First is, at heart, a CSS class **naming convention** plus a small set of **structural wrapper classes** and a utility/spacing system. Those are just class names and CSS — they port cleanly to any hand-written HTML, including a classic theme's `header.php`, templates, and `template-parts/`.

What does **not** port:
- **The Webflow Designer workflow** — the Style Guide page, visual class management, combo-class stacking in the UI. In a coded theme you write the CSS yourself; there's no Designer.
- **Finsweet's folder system** relies on the Finsweet extension in Webflow to visualize folders from underscores in class names. In a stylesheet the "folders" are just a naming idea you keep consistent by discipline, not a tool.
- **Block themes** actively conflict with it (see §6). This adaptation is for **classic themes only**.

So the honest framing: use Client-First in WordPress as *an opinionated, consistent way to name classes and structure page wrappers in a classic theme's markup*, giving you parity with how the same shop builds in Webflow. Don't expect a literal 1:1 of the Webflow experience.

## 2. The structure classes (Client-First v2.1)

These core structure classes are the backbone and map directly onto theme markup:

- `page-wrapper` — outermost wrapper around everything.
- `main-wrapper` — wraps the main content area.
- `container-small` / `container-medium` / `container-large` — width-constrained content containers.
- `padding-global` — the project's primary horizontal padding value (left/right gutters).
- `padding-section-small` / `padding-section-medium` / `padding-section-large` — vertical section spacing.
- `button-group` — wrapper for grouped buttons.
- Heading helpers: `heading-style-h1` … `heading-style-h6` (used when a heading's *style* doesn't match its HTML tag).
- `text-size-*`, `text-weight-*`, `text-color-*` utility families (general-to-specific naming).

## 3. Naming convention rules

Client-First v2 distinguishes class types by character usage — keep this consistent and the system reads itself:

- **Utility classes use dashes only**, no underscores: `text-size-large`, `padding-section-medium`, `margin-bottom-small`. They do one job and are reused globally.
- **Custom classes use an underscore** to denote a folder/grouping: `team-list_headshot-wrapper`, `faq_item`, `header_content`. The part before the underscore is the "folder" (the component/section/page grouping); the rest gets progressively more specific.
- **Components** are classified explicitly with the word `component` in the identifier (v2 change): an underscore alone now means "folder/grouping," not necessarily "component."
- **General-to-specific** ordering: `text-size-large`, never `large-text-size` — it groups related utilities together and makes search predictable.
- **Section classes** are custom classes (use the underscore): `section_hero`, `section_contact`.
- **Combo classes**: a base class plus a variant stacked on top (`button` + `is-secondary`). State/variant prefixes like `is-` are conventional.

## 4. Applying it in PHP templates

`header.php` skeleton with Client-First structure classes:

```php
<body <?php body_class(); ?>>
<?php wp_body_open(); ?>
<div class="page-wrapper">
	<header class="header_wrap">
		<div class="padding-global">
			<div class="container-large">
				<div class="header_content">
					<?php if ( has_custom_logo() ) { the_custom_logo(); } ?>
					<nav class="header_nav">
						<?php wp_nav_menu( array( 'theme_location' => 'primary', 'container' => false, 'menu_class' => 'nav_list', 'fallback_cb' => false ) ); ?>
					</nav>
				</div>
			</div>
		</div>
	</header>
	<main class="main-wrapper">
```

A section partial (`template-parts/section-hero.php`):

```php
<section class="section_hero">
	<div class="padding-global">
		<div class="padding-section-large">
			<div class="container-medium">
				<h1 class="heading-style-h1"><?php echo esc_html( get_the_title() ); ?></h1>
				<p class="text-size-large"><?php echo esc_html( get_field( 'subtitle' ) ); ?></p>
			</div>
		</div>
	</div>
</section>
```

Note this composes cleanly with everything else in the skill: `body_class()`, escaped output, `wp_nav_menu`, custom fields. Client-First governs the *class names*; the WordPress patterns are unchanged.

`wp_nav_menu` outputs its own markup — pass `menu_class`/`container` to align the generated classes with your convention, and use a `walker` only if you need full control over the nav markup to match Client-First exactly.

## 5. The stylesheet side

Pair this with the SCSS pipeline in `scss-pipeline.md`. A natural mapping:
- `abstracts/` holds spacing/typography tokens that back the utility classes.
- A `utilities/` partial defines the dash-named utility classes (`text-size-*`, `padding-section-*`, spacing system).
- `layout/` holds the structure classes (`page-wrapper`, `container-*`, `main-wrapper`).
- `components/` holds underscore-grouped custom classes (`faq_item`, `header_content`).

Because Client-First leans on global/utility classes rather than per-element styling, it produces a flatter, more reusable stylesheet than ad-hoc theme CSS — which is the point. Keep the spacing system values in SCSS variables (or `theme.json`-driven CSS custom properties if you ever go hybrid) so a global change is one edit.

## 6. When NOT to use this (block themes)

Do **not** apply Client-First to a block/FSE theme. Block themes already have a styling system: `theme.json` presets, generated `wp-block-*` classes, and editor-managed styles. Layering Client-First on top means fighting the editor, duplicating the spacing/typography system `theme.json` already provides, and producing classes the Site Editor won't understand or manage. If the project needs Client-First conventions, that's a strong signal to build a **classic theme**, not a block theme. If the project should be a block theme, embrace `theme.json` (see `block-themes.md`) and let Client-First stay in the Webflow side of the shop's work.
