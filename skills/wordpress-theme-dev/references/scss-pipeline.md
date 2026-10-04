# CSS & SCSS Pipeline

How to structure and compile styles for a theme. Ties into enqueueing (see `wp-apis.md` §2).

## Plain CSS (simplest)

For small themes, a single `style.css` (classic) or `assets/css/main.css` is fine. In a block theme most styling lives in `theme.json`; keep CSS minimal and reference presets:

```css
.site-header { background: var(--wp--preset--color--base); padding: var(--wp--preset--spacing--40); }
```

Enqueue with a `filemtime()`/version cache-buster (see `wp-apis.md`). Don't put structural styling in the theme-header `style.css` of a block theme — prefer `theme.json`.

## SCSS — when the theme grows

Use SCSS for nesting, variables, partials, and mixins once styles get beyond a few hundred lines. Recommended layout is the **7-1 pattern** (folders, one output file):

```
assets/scss/
├── abstracts/    _variables.scss, _mixins.scss, _functions.scss
├── base/         _reset.scss, _typography.scss, _root.scss
├── components/   _buttons.scss, _cards.scss
├── layout/       _header.scss, _footer.scss, _grid.scss
├── pages/        _front-page.scss
├── utilities/    _helpers.scss
└── main.scss     @use's everything; the only file compiled
```

`main.scss` pulls partials in with the modern module system (`@use`, not the deprecated `@import`):

```scss
@use 'abstracts/variables' as *;
@use 'abstracts/mixins' as *;
@use 'base/reset';
@use 'base/typography';
@use 'layout/header';
@use 'components/buttons';
```

Partials are prefixed `_` so they aren't compiled standalone. Mirror WordPress preset tokens in SCSS variables so values stay in sync with `theme.json`:

```scss
// abstracts/_variables.scss
$color-primary: var(--wp--preset--color--primary);
$space-md: var(--wp--preset--spacing--40);
```

## Compilation

Use Dart Sass (the maintained implementation). Two common setups:

**Standalone Dart Sass (no Node build):**
```bash
sass assets/scss/main.scss:assets/css/main.css --style=compressed --source-map   # build
sass --watch assets/scss/main.scss:assets/css/main.css                            # dev
```

**Via npm (package.json scripts):**
```json
{
  "scripts": {
    "dev": "sass --watch assets/scss/main.scss:assets/css/main.css --source-map",
    "build": "sass assets/scss/main.scss:assets/css/main.css --style=compressed --no-source-map"
  },
  "devDependencies": { "sass": "^1.77.0" }
}
```

Compile to `assets/css/`, then enqueue the **compiled** CSS — never enqueue `.scss`. Ship compiled CSS in the theme; the `scss/` source is for development. For cache-busting in dev, version the enqueue with `filemtime( get_theme_file_path( 'assets/css/main.css' ) )`; in production use the theme version.

## Editor styles

To make the block editor reflect the theme's look, enqueue editor styles too:

```php
add_action( 'after_setup_theme', function () {
	add_theme_support( 'editor-styles' );
	add_editor_style( 'assets/css/editor.css' ); // compiled from scss/editor.scss
} );
```

Block themes get most of this for free from `theme.json`; add `editor-styles` only for CSS beyond what `theme.json` expresses.
