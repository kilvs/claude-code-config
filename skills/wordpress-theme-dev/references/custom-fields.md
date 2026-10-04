# Custom Fields: ACF / SCF and Carbon Fields

How to add custom fields and metaboxes to a theme with the two dominant libraries. Both attach extra structured data to posts, pages, taxonomies, users, and global options pages, which the theme then outputs. This is mostly a **classic-theme** concern (block themes lean on block attributes and `theme.json`), but both work alongside either type.

For escaping/sanitizing rules referenced here see `security.md`. For the hooks and enqueue patterns see `wp-apis.md`.

## Contents
1. ACF vs Carbon Fields — choosing
2. The ACF / SCF naming situation (read this first)
3. ACF: register, retrieve, output
4. Carbon Fields: install, register, retrieve, output
5. Output security — the field-escaping trap
6. Local JSON / version control
7. Where to define fields in a theme

---

## 1. ACF vs Carbon Fields — choosing

Both solve the same problem; they differ in workflow and dependency model.

**ACF (Advanced Custom Fields) / SCF (Secure Custom Fields)** — the most widely used. Fields are usually built in a **admin UI** and can be exported to PHP or synced via Local JSON. Free tier covers most field types; Repeater, Flexible Content, Gallery, Clone, and Options Pages historically required Pro (see §2 for how the fork changed this). Choose when: the client/team will manage fields in wp-admin, you want the mature ecosystem and field types, or you're on a stack that already uses it.

**Carbon Fields** (by htmlBurger) — **code-first**, no admin UI. Fields are declared in PHP with a fluent `Container::make()->add_fields()` API and installed via **Composer**, not as a plugin from the directory. Repeater-equivalent ("complex") fields are free. Choose when: you want fields fully in version control by definition, you prefer declaring everything in code, you're comfortable with Composer, or you want to avoid a plugin dependency the client could deactivate.

Rule of thumb: editor-managed fields and broad ecosystem → ACF/SCF. Code-only, Composer-based, everything-in-git → Carbon Fields. Don't run both for the same data.

## 2. The ACF / SCF naming situation (read this first)

This matters for what you install and recommend, and it's recent, so don't assume older habits hold.

In October 2024 the ACF plugin became embroiled in a dispute between Automattic and WP Engine (ACF's owner). On October 12, 2024, ACF was replaced on the official WordPress.org directory by Secure Custom Fields (SCF), a fork set up by the WordPress security team. In November the fork was extended to ACF Pro features — repeater, gallery, flexible content, clone fields, options pages, and ACF Blocks — with licensing and update checks removed, and SCF became a non-commercial plugin.

Practical consequences for theme dev:
- **SCF** is what installs from the WordPress.org directory under the old ACF slug; sites that auto-updated were switched to it.
- **ACF / ACF Pro** continues to be distributed by WP Engine directly (their site / GitHub), and via Composer for Pro.
- The **PHP API is the same** (`acf_*` functions, `get_field()`, etc.), so theme code written against ACF generally works on SCF and vice versa. Write against the shared API and your theme stays portable.
- The situation has continued shifting through 2025–2026 (court rulings affecting distribution). If a current recommendation hinges on who-owns-what or which is on the directory today, **verify with a quick search** rather than stating it from memory — this is a moving target.

Throughout this doc "ACF" means the shared `acf_*` API common to both.

## 3. ACF: register, retrieve, output

**Register in PHP** (portable, version-controllable). The recommended hook is `acf/include_fields`:

```php
add_action( 'acf/include_fields', 'mytheme_register_fields' );
function mytheme_register_fields() {
	if ( ! function_exists( 'acf_add_local_field_group' ) ) {
		return; // ACF/SCF not active — fail gracefully
	}
	acf_add_local_field_group( array(
		'key'      => 'group_mytheme_property',
		'title'    => 'Property Details',
		'fields'   => array(
			array(
				'key'   => 'field_property_price',
				'label' => 'Price',
				'name'  => 'price',
				'type'  => 'number',
			),
			array(
				'key'   => 'field_property_address',
				'label' => 'Address',
				'name'  => 'address',
				'type'  => 'text',
			),
		),
		'location' => array(
			array(
				array( 'param' => 'post_type', 'operator' => '==', 'value' => 'property' ),
			),
		),
	) );
}
```

The usual real-world workflow is to build the group in the ACF UI, then use its **Generate PHP / JSON export** so it lives in the theme. Keys (`group_*`, `field_*`) must be unique and stable — they're how ACF tracks fields.

**Retrieve & output** in templates (inside the Loop, `$post` is implicit):

```php
$price = get_field( 'price' );          // returns the value
if ( $price ) {
	echo esc_html( number_format( (float) $price ) ); // escape on output — see §5
}

// Repeater / flexible content:
if ( have_rows( 'gallery_items' ) ) {
	while ( have_rows( 'gallery_items' ) ) { the_row();
		$img = get_sub_field( 'image' ); // returns array for image fields
		printf( '<img src="%s" alt="%s">', esc_url( $img['url'] ), esc_attr( $img['alt'] ) );
	}
}

// Options page value (global, not tied to a post):
$phone = get_field( 'contact_phone', 'option' );
```

`get_field()` returns the value (escape it yourself). `the_field()` echoes it — see §5 for why you should prefer `get_field()` + explicit escaping.

## 4. Carbon Fields: install, register, retrieve, output

**Install via Composer** and boot it — it is not a directory plugin:

```bash
composer require htmlburger/carbon-fields
```

```php
// functions.php — boot before registering
add_action( 'after_setup_theme', 'mytheme_boot_carbon' );
function mytheme_boot_carbon() {
	require_once get_template_directory() . '/vendor/autoload.php';
	\Carbon_Fields\Carbon_Fields::boot();
}
```

**Register** on `carbon_fields_register_fields` using the fluent API:

```php
use Carbon_Fields\Container;
use Carbon_Fields\Field;

add_action( 'carbon_fields_register_fields', 'mytheme_attach_fields' );
function mytheme_attach_fields() {
	// Post meta
	Container::make( 'post_meta', __( 'Property Details', 'my-theme' ) )
		->where( 'post_type', '=', 'property' )
		->add_fields( array(
			Field::make( 'text', 'crb_price', __( 'Price', 'my-theme' ) ),
			Field::make( 'text', 'crb_address', __( 'Address', 'my-theme' ) ),
		) );

	// Global theme options page
	Container::make( 'theme_options', __( 'Theme Options', 'my-theme' ) )
		->add_fields( array(
			Field::make( 'text', 'crb_contact_phone', __( 'Contact Phone', 'my-theme' ) ),
			Field::make( 'rich_text', 'crb_footer_copyright', __( 'Footer Copyright', 'my-theme' ) ),
		) );
}
```

**Retrieve & output** with the `carbon_get_*` functions:

```php
// Post meta (inside the Loop):
echo esc_html( carbon_get_the_post_meta( 'crb_price' ) );
// or for a specific ID:
echo esc_html( carbon_get_post_meta( get_the_ID(), 'crb_address' ) );

// Theme option (global):
echo esc_html( carbon_get_theme_option( 'crb_contact_phone' ) );

// Complex (repeater) field — pass 'complex':
$rows = carbon_get_theme_option( 'crb_addresses', 'complex' );
foreach ( $rows as $row ) {
	echo esc_html( $row['line'] );
}
```

By convention Carbon Fields names are prefixed `crb_`. Theme-options containers default to requiring the `manage_options` capability.

## 5. Output security — the field-escaping trap

This is the single most common custom-fields vulnerability, so it gets its own section.

Custom field values are **user input** (someone typed them in wp-admin). When you output them, escape by context exactly as in `security.md`: `esc_html()` between tags, `esc_attr()` in attributes, `esc_url()` for URLs, `wp_kses_post()` only for rich-text fields where formatting is intended.

The trap: the convenient echo helpers historically did **not** escape:
- ACF's `the_field()` / `the_sub_field()` echo raw. ACF added an opt-in filter (`acf/the_field/escape_html_optin`) to auto-escape `the_field`/`the_sub_field` ahead of this becoming default in a later release — but don't rely on whatever the installed version's default is.
- Carbon Fields' `carbon_get_*` return raw values.

Safe habit that works regardless of library version: **use the value-returning function and escape explicitly** — `echo esc_html( get_field('x') )` and `echo esc_html( carbon_get_the_post_meta('crb_x') )`. For a rich-text field, `echo wp_kses_post( get_field('body') )`. Never echo a field straight into an `href`/`src` without `esc_url()` — that's the classic injection path (and the exact case in the "phone number into a tel: link" scenario: `printf('<a href="tel:%s">', esc_attr( $phone ))`).

## 6. Local JSON / version control

A field definition that isn't in version control will drift between environments. Both libraries solve this:

- **ACF Local JSON**: create an `acf-json/` directory in the theme; ACF auto-saves field-group JSON there on every save and offers to sync changes on other environments. Keep `acf-json/` in git. Alternatively export to PHP (§3) and register in code.
- **Carbon Fields**: definitions *are* PHP code, so they're version-controlled by nature — nothing extra needed.

## 7. Where to define fields in a theme

Keep `functions.php` lean: put field registration in `inc/` files (e.g. `inc/fields-property.php`, `inc/fields-options.php`). The classic scaffold auto-requires every `*.php` in `inc/`, so adding a file is enough — no manual `require` needed. Guard ACF registration with a `function_exists( 'acf_add_local_field_group' )` check and Carbon Fields with awareness that `boot()` must have run, so the theme degrades gracefully if the dependency is missing rather than fatal-erroring. Output code lives in the relevant template or `template-parts/` partial, always escaped.
