# WordPress playbook

**Status:** learning, since 22 Sep 2026. In client use since 23 Sep 2026: a live
Elementor Pro site, edited through WP admin.

## What it is used for
Candidate platform for clients who need a CMS with their own hosting, and a learning target
beside PHP (WordPress is the reason to learn PHP well). Notes on progress go in `learning.md`.

## Conventions
Default until a real build says otherwise:
- Classic theme or block theme decided per project and written in the project `CLAUDE.md`.
- Local dev with `wp-env` or Local; never edit a live site's files.
- Child theme or custom theme in a git repo under `~/Developer/<Org>/<Project>`; no edits
  through the WordPress admin theme editor.
- PHP follows the WordPress Coding Standards (`phpcs` with the WPCS ruleset). Escape on output,
  sanitise on input, nonces on forms.
- Plugins are a last resort; log each one and why.

## Accounts and tools
None yet. Skill `skills/wordpress-theme-dev/` (editable master; synced twin
`anthropic-skills:wordpress-theme-dev`) should be loaded for theme work.

Skill `skills/wordpress-elementor/` (29 Sep 2026, adapted from Jezweb's MIT `claude-skills`,
no synced twin) for editing existing Elementor pages, templates and forms on live sites: the
editor through Claude in Chrome by default, WP-CLI only with SSH. Load it on any Elementor task.
Its Lessons table is where new Elementor rules go.

## Gotchas that became rules
| Date | What happened | Rule |
|---|---|---|

## Pointers
`stacks/php/README.md`, `learning.md` in this folder.
