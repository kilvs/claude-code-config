# Theme Security

Applies to both theme types. The two ideas that prevent almost every theme vulnerability: **escape late** (right before output, chosen by output context) and **sanitize early** (when data comes in). Plus nonces for any action, and capability checks for anything privileged.

## Contents
1. Escape on output — the matrix
2. Sanitize on input
3. Nonces (forms & AJAX)
4. Capability checks
5. Direct-access guard
6. Quick audit checklist

---

## 1. Escape on output — the matrix

Escaping converts data so it can't break out of its context and inject markup/script. Pick the function by **where the value lands**, not by what you think the value contains — themes get reused with untrusted content.

| Output context | Function | Example |
|---|---|---|
| Between HTML tags (text) | `esc_html()` | `<p><?php echo esc_html( $name ); ?></p>` |
| Inside an attribute | `esc_attr()` | `<div class="<?php echo esc_attr( $class ); ?>">` |
| A URL (href/src) | `esc_url()` | `<a href="<?php echo esc_url( $link ); ?>">` |
| URL in a DB/redirect context | `esc_url_raw()` | storing a URL, not displaying |
| Inside inline JS | `esc_js()` | legacy; prefer `wp_localize_script` / `wp_add_inline_script` |
| Rich HTML you must allow | `wp_kses_post()` | post-content-level tags only |
| Arbitrary HTML, custom allowlist | `wp_kses( $html, $allowed )` | precise tag/attr control |
| Translate + escape (text) | `esc_html__()` / `esc_html_e()` | combines i18n + escaping |
| Translate + escape (attr) | `esc_attr__()` / `esc_attr_e()` | |
| Numeric | `absint()` / `intval()` | IDs, counts |

Rules of thumb:
- Core `the_*()` template tags (`the_title()`, `the_permalink()`) are already escaped for their normal context — don't double-escape. The `get_the_*()` variants are **not** echoed and not guaranteed escaped, so escape those yourself.
- Never echo `$_GET`/`$_POST`/`$_SERVER` (e.g. `$_SERVER['PHP_SELF']`) without escaping — classic XSS vector.
- `wp_kses_post()` is for content where you *intend* to allow formatting; don't use it as a lazy catch-all for plain text (`esc_html` is correct and cheaper there).

## 2. Sanitize on input

Sanitizing cleans data as it enters storage. Match the function to the data type:

| Data | Function |
|---|---|
| Plain text field | `sanitize_text_field()` |
| Textarea | `sanitize_textarea_field()` |
| Email | `sanitize_email()` |
| URL (for storage) | `esc_url_raw()` |
| Slug / key | `sanitize_title()` / `sanitize_key()` |
| Hex color | `sanitize_hex_color()` |
| Integer | `absint()` / `intval()` |
| HTML to keep | `wp_kses_post()` / `wp_kses()` |
| File name | `sanitize_file_name()` |

Every Customizer setting needs a `sanitize_callback` (see `wp-apis.md` §4). Validate (reject bad values) when the data's meaning matters, beyond just sanitizing its shape.

## 3. Nonces (forms & AJAX)

A nonce proves a request came from a legitimate user action on your site, not a forged cross-site request (CSRF). Any theme form or AJAX that *changes* something needs one.

Form:
```php
// in the form
wp_nonce_field( 'mytheme_save', 'mytheme_nonce' );

// on handling
if ( ! isset( $_POST['mytheme_nonce'] ) ||
     ! wp_verify_nonce( sanitize_key( $_POST['mytheme_nonce'] ), 'mytheme_save' ) ) {
	wp_die( esc_html__( 'Security check failed.', 'my-theme' ) );
}
```

AJAX (nonce created via `wp_localize_script`, see `wp-apis.md` §2):
```php
add_action( 'wp_ajax_mytheme_act', 'mytheme_ajax' );
add_action( 'wp_ajax_nopriv_mytheme_act', 'mytheme_ajax' );
function mytheme_ajax() {
	check_ajax_referer( 'mytheme_nonce', 'nonce' ); // dies on failure
	// ... sanitize inputs, do work, then:
	wp_send_json_success( array( 'ok' => true ) );
}
```

Nonces are not a substitute for capability checks or sanitization — they verify intent, not permission or content.

## 4. Capability checks

Before any privileged action, confirm the user is allowed:
```php
if ( ! current_user_can( 'edit_posts' ) ) {
	wp_die( esc_html__( 'Insufficient permissions.', 'my-theme' ) );
}
```
Check capabilities (`edit_posts`, `manage_options`, …), not roles. The pattern for a privileged handler is: capability check → nonce verify → sanitize input → act → escape output.

## 5. Direct-access guard

Top of every PHP file:
```php
defined( 'ABSPATH' ) || exit;
```
This stops the file being executed by hitting its URL directly, which can leak errors/paths or run code out of context.

## 6. Quick audit checklist

Before shipping, grep/scan for:
- [ ] Any `echo` of a variable without an `esc_*` — fix or justify.
- [ ] Any `$_GET`/`$_POST`/`$_REQUEST`/`$_SERVER` used without sanitizing.
- [ ] Every form has `wp_nonce_field` and its handler verifies it.
- [ ] Every Customizer setting has a `sanitize_callback`.
- [ ] No hardcoded paths/URLs (use `get_theme_file_uri()` etc.).
- [ ] `defined( 'ABSPATH' ) || exit;` at the top of each PHP file.
- [ ] All globals/functions/handles prefixed.
- [ ] Run with `WP_DEBUG = true` and resolve every notice/warning.
