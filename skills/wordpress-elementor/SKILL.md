---
name: wordpress-elementor
description: "Edit existing Elementor and Elementor Pro pages on live WordPress sites: text, images, buttons, per-device visibility, saved templates, Theme Builder parts, forms, and site-wide Additional CSS, then clear caches and verify. Use whenever a task touches a page built with Elementor, an Elementor template or saved section, an Elementor form, or Elementor's CSS cache. Works through the WordPress admin in the client's Chrome profile (Claude in Chrome); WP-CLI only when the host gives SSH. Not for building a theme from scratch (use wordpress-theme-dev)."
---

## Changes

- 29 Sep 2026: rewritten
  for how the user works. Dropped Jezweb's `wordpress-setup` dependency (`wp @site` alias) and
  playwright-cli; access now comes from the client card. Replaced the "Risk: None" labels,
  added the live-site rules, containers, template reach, cache purge, logged-out checks and the
  first lessons from a live Elementor Pro site. Grow the Lessons table as sites teach us.
- 29 Sep 2026: imported from Jezweb's MIT `claude-skills`
  (github.com/jezweb/claude-skills, `plugins/wordpress/skills/wordpress-elementor`, commit
  ee91a87). Licence in `LICENSE` beside this file. Superseded by the rewrite above.

# WordPress Elementor

Edit pages on sites that already exist. Most are live client sites, so every change is a
change to production.

## Rules

1. **Read the client card and the project `CLAUDE.md` RESUME HERE first.** They name the
   Chrome profile, the admin access, any MCP connector and the site's quirks.
2. **Live site: the user's word before each change.** Say what will change, where, and how to
   undo it. "Update" in the editor publishes instantly. One yes covers one change.
3. **Back up first.** Export the template or page JSON, or write the old value in the log, so
   the revert is one step.
4. **Copy is the client's.** Build it verbatim. Flag typos and em dashes; never fix them.
5. **Smallest reversible change.** Prefer a widget setting (Hide on Tablet, Hide on Mobile) or
   one dated rule in Additional CSS over restructuring. Hide rather than delete.
6. **Verify on the live page, logged out, after the cache purge.**
7. **Log it.** Project `CLAUDE.md` decision log (date, who asked, element IDs, revert steps)
   and `BACKLOG.md`.

## Step 1: Find what you are editing

- **Page ID:** hover the page in Pages (the link shows `post=<ID>`), or read the body class
  `page-id-<ID>` on the live page.
- **Editor URL:** `/wp-admin/post.php?post=<ID>&action=elementor`
- **Element ID:** every element renders `data-id="<id>"` and the class
  `elementor-element-<id>`. Use it to find the element in the Navigator and to log it.
- **Where it really lives:** walk up from the element to the nearest `data-elementor-id`.
  If that ID is not the page ID, the element sits in a saved template, a global widget or a
  Theme Builder part (header, footer, single). Editing it changes every page that uses it, so
  list those pages when you ask.

## Step 2: Pick the method

| Change | Method | Risk on a live site |
|---|---|---|
| Text, link or image in one widget | Editor | Medium: publishes on Update |
| Per-device visibility, spacing, style | Editor | Medium: check every breakpoint |
| Add, move or remove sections | Editor | High: layout can break at other widths |
| Anything in a saved template, global widget, header or footer | Editor, on the template | High: every page using it changes |
| Site-wide CSS fix | Appearance > Customize > Additional CSS, with a dated comment | Medium: every page |
| Reuse a layout on a new page | Export as template, insert into a draft page | Low while it stays a draft |
| Same text on many pages | WP-CLI search-replace, only with SSH | High: rewrites every matching row at once |

Default to the editor. Reach for WP-CLI only for a bulk text swap on a host with SSH.

## Step 3: Edit in the editor (Claude in Chrome)

- Load the `claude-in-chrome` skill and use the Chrome profile on the client card. If the admin is logged out, ask the user to log in; never type passwords.
- Open the editor URL and wait for the loading overlay to clear (5 to 10 seconds). It is ready
  when the left panel lists widgets.
- Find elements with the Navigator (Cmd+I). It is safer than clicking a dense canvas.
- A selected element has Content, Style and Advanced tabs. Per-device values use the device
  switcher; a desktop value cascades down unless tablet or mobile overrides it. Visibility is
  Advanced > Responsive > Hide on Desktop / Tablet / Mobile.
- Read the site's breakpoints in Site Settings > Layout > Breakpoints. Don't assume them.
- Click Update only after the user's word. The undo is History (Cmd+Shift+H) > Revisions.
- Avoid anything that opens a browser dialog (delete confirmations); it freezes the extension.

## Step 3b: Bulk text with WP-CLI (only with SSH)

1. Back up the page data into the project folder, never `/tmp`:
   `wp post meta get <ID> _elementor_data > elementor-<ID>-<date>.json`
2. Dry run: `wp search-replace "Old" "New" wp_postmeta --include-columns=meta_value --precise --dry-run`
3. Check the count. The swap hits every page, revision and template that holds the string,
   not just yours.
4. Run it for real, then regenerate CSS (Step 4) and verify (Step 5).

`_elementor_data` is JSON, so slashes are stored as `\/` and curly quotes as `’`. A URL or
a line with an apostrophe may not match as typed; grep the JSON first. For domain changes, use
Elementor > Tools > Replace URL instead.

## Step 4: Clear caches

- **Elementor CSS:** Elementor > Tools > Regenerate CSS & Data (or `wp elementor flush-css`).
- **Page cache:** purge the site's cache plugin (for example LiteSpeed Cache > Purge All in the
  admin bar), and any host or CDN cache.

## Step 5: Verify

- Load the live page **logged out**. Admins usually skip the page cache, so they can see a
  version visitors don't.
- Check the rendered DOM, not the editor: the element's text and computed styles, and
  `document.documentElement.scrollWidth > innerWidth` for sideways scroll, at 360 to 1440 and at
  the site's breakpoints.
- If you edited a template, check every page that uses it.

## Templates and Pro features

- **Saved templates:** Templates > Saved Templates (`edit.php?post_type=elementor_library`).
  Export one (hover > Export Template) before editing it; that is the backup.
- **Theme Builder (Pro):** header, footer, single and archive parts. Their display conditions
  decide where they show; read them before editing.
- **Never overwrite a live page's `_elementor_data`** with another page's. Copy layouts through
  an exported template into a draft.
- **Other Pro-only features:** the Form widget (reCAPTCHA, honeypot field, submissions under
  Elementor > Submissions), per-widget Custom CSS (Advanced tab), dynamic tags and popups.

## Structure

Current Elementor builds pages from Flexbox Containers (Container > widgets, containers nest).
Older pages use Section > Column > Widget. Both render `data-id` on every element.

## Lessons from real sites

| Date | What happened | Rule |
|---|---|---|
| 29 Sep 2026 | An absolutely positioned icon in a saved template made three pages 110px too wide on phones | Check absolute elements at every breakpoint. Fix them in the template once; every page using it is repaired |
| 29 Sep 2026 | `overflow-x: hidden` on `body` alone did not stop phones scrolling sideways | Use `html, body { overflow-x: clip; }`; clip keeps sticky headers working |
| 29 Sep 2026 | A CSS change was checked logged out, after a LiteSpeed cache miss | Verify as a visitor, after the purge |
